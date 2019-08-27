import logging

from . import chess
from .constraint import Constraint
from .region import Region, RegionSymbolsConstraint, subtractLists

class RegionPermutesSymbols(RegionSymbolsConstraint):
  """ The core logic for regions containing each symbol in a set,
      where each symbol appears in exactly one square in the region.
      The region must have the same number of squares as there are symbols in the set.
  """
  def __init__(self, region, symbols):
    """ Regions are passed using string formats defined in the Region class.
        The symbol set is a list of strings.
    """
    super().__init__(region, symbols)
    # logging.debug("RegionPermutesSymbols(%s, %s)", region, symbols)
    if len(symbols) != len(self.region.cells):
      raise Exception("Can't permute " + str(symbols) + " over " + str(self.region))

  def copy(self):
    """ Make a distinct duplicate. """
    return RegionPermutesSymbols(self.region, self.symbols)

# Solving techniques, from trivial to easy to harder:

  def techniques(self):
    return super().techniques() + [
      self.partition, 
      self.misfit, 
      self.borrow,
      self.intersection
    ]

  def partition(self, puzzle):
    """ For every group of n cells that contain the same n symbols and no others,
        partition the region into two new regions:
        - the "limited" region that contains those n cells and symbols, and
        - the "remainder" region that contains the other cells and the other symbols.
        For n = 1, this takes care of removing "settled" symbols from the remainder of the region.
        Returns constraints for those two regions as soon as the condition is found.
        (That may not be the most efficient option, but it does simplify the logic.)
    """
    # First, index the contents.
    index = {}  # maps a set of symbols to the coordinates at which they appear.
    for location in self.region:
      subset = puzzle.solution.at(location)
      if len(subset) < len(self.symbols):
        symbols = '|'.join(subset)
        index.setdefault(symbols, []).append(location)

    for symbols, coordList in index.items():
      subset = symbols.split('|')
      if len(subset) == len(coordList):
        # There are the same number of symbols in this set as cells to put them in.
        # So, the given coordList can be partitioned off from the rest of the region.
        remainder = self.remainder(coordList, subset)
        logging.debug("Partitioning out %s in %s, leaving %s in %s", 
          self.showSymbols(subset), chess.locations(coordList), self.showSymbols(remainder.symbols), remainder.region)
        puzzle.logTechnique('partition')
        result = [RegionPermutesSymbols(coordList, subset), remainder]

        # We can also remove all the subset symbols from the remainder region.
        puzzle.solution.eliminateThroughout(remainder.region, subset)

        return result

  def misfit(self, puzzle):
    """ Look for a symbol that only occurs in one place within the region.
        Everything else can be eliminated from that cell, 
        and we can replace this constraint with a new one excluding that cell and symbol.
    """
    # First, count how many times each symbol appears in our region.
    index = puzzle.solution.indexSymbolsIn(self.region)
    # logging.debug("misfit: index: %s", index)

    # Now, find the first misfit symbol.
    for s, locations in index.items():
      if len(locations) == 1:
        puzzle.solution.setCell(locations[0], s)
        remainder = self.remainder(locations, [s])
        logging.debug("Misfit: %s must be %s, since it can't occur elsewhere in %s",
          chess.location(locations[0]), self.showSymbols(s), self.region)
        puzzle.logTechnique('misfit')
        return [remainder]

  def borrow(self, puzzle):
    """ Look for another permutation constraint whose region is a subset of this one.
        We can eliminate those symbols from all our cells NOT in that region.
        Then we can replace this constraint with a new one that doesn't include that region or its symbols.
        Returns a list containing the new constraint, or None if no such constraints were found.
    """
    for constraint in puzzle.constraints:
      if isinstance(constraint, RegionPermutesSymbols):
        if self.region.hasProperSubset(constraint.region):
          remainder = self.remainderConstraint(constraint)
          logging.debug("Borrowing %s from %s, leaving %s in %s", 
            self.showSymbols(constraint.symbols), constraint.region, self.showSymbols(remainder.symbols), remainder.region)
          puzzle.logTechnique('borrow')
          puzzle.solution.eliminateThroughout(remainder.region, constraint.symbols)
          return [remainder]

  def intersection(self, puzzle):
    """ Look for another permutation constraint whose region intersects with this one.
        If there are any symbols that only occur in the other constraint's region within the intersection,
        that means they have to occur in that intersection,
        so they can be removed from the remainder of the cells in this region.
        Make a new constraint, but just to document that something's chnaged.
    """
    for constraint in puzzle.constraints:
      if isinstance(constraint, RegionPermutesSymbols) and constraint is not self:
        intersection = self.region.intersect(constraint.region)
        if not intersection.isEmpty() and intersection.size() < self.region.size():
          index = puzzle.solution.indexSymbolsIn(constraint.region)
          # logging.debug("Intersection index: %s", index)
          for s, locations in index.items():
            if intersection.hasSubset(locations):
              remainder = self.region.subtract(intersection)
              logging.debug("Intersection: %s occurs only in %s, so remove it from %s",
                s, intersection, chess.locations(remainder))
              puzzle.logTechnique('intersection')
              puzzle.solution.eliminateThroughout(remainder, [s])
              return [self.copy()]

  # Utility functions:

  def remainder(self, locations, symbols):
    """ Return a new RegionPermutesSymbols constraint, by subtracting the given locations and symbols
        from this region's locations and symbols.
    """
    remainderLocations = self.region.subtract(locations)
    remainderSymbols = subtractLists(self.symbols, symbols)
    return RegionPermutesSymbols(remainderLocations, remainderSymbols)

  def remainderConstraint(self, other):
    """ Return a new RegionPermutesSymbols constraint, subtracting out the regions and symbol sets
        in `other` from those in `self`.
    """
    return self.remainder(other.region, other.symbols)

# The remaining classes are useful in providing concise shorthands that expand to the above.

class RegionIsCompletePermutation(Constraint):
  """ Creates a RegionPermutesSymbols constraint for all the symbols in the puzzle's symbol set.
  """
  def __init__(self, region):
    """ The region is passed using string formats defined in the Region class. """
    self.region = region

  def apply(self, puzzle):
    if puzzle.symbols:
      return [RegionPermutesSymbols(self.region, puzzle.symbols)]
    else:
      # Wait until we know the complete symbol set.
      return [self]

class RegionsAreCompletePermutation(Constraint):
  """ Creates a separate region constraint for each region passed in.  
      For concisely expressing standard constraints.
      The regions are passed as a list of strings, using string formats defined in the Region class.
  """
  def __init__(self, regions):
    self.regions = regions

  def apply(self, puzzle):
    return [RegionIsCompletePermutation(r) for r in self.regions]

class EachDimensionIsCompletePermutation(Constraint):
  """ Creates a RegionsAreCompletePermutation constraint for each row and column.
      Only works up to size 9.
  """
  def apply(self, puzzle):
    if puzzle.size:
      lastRow = chr(ord('a') + puzzle.size[0] - 1)
      lastCol = chr(ord('1') + puzzle.size[1] - 1)
      # Rows: like "a1-a9", for a..i
      regions = [chr(r) + '1-' + chr(r) + lastCol for r in range(ord('a'), ord(lastRow) + 1)]
      # Cols: like "a1-i1" for 1..9
      regions += ['a' + chr(c) + '-' + lastRow + chr(c) for c in range(ord('1'), ord(lastCol) + 1)]
      return [RegionsAreCompletePermutation(regions)]
    else:
      # Can't resolve without the size, so wait for it to be known.
      return [self]
