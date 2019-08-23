import logging

from .constraint import Constraint
from .region import Region

def subtractLists(alist, blist):
  """ Return list a with all elements that match an element in b removed.
      >>> subtractLists([1, 2, 3], [3])
      [1, 2]
      >>> subtractLists(['1', '2', '3'], ['1'])
      ['2', '3']
      >>> subtractLists([[0, 0], [0, 1]], [[0, 0]])
      [[0, 1]]
  """
  return [a for a in alist if not a in blist]

class RegionPermutesSymbols(Constraint):
  """ The core logic for regions containing each symbol in a set,
      where each symbol appears in exactly one square in the region.
      The region must have the same number of squares as there are symbols in the set.
  """
  def __init__(self, region, symbols):
    """ Regions are passed using string formats defined in the Region class.
        The symbol set is a list of strings.
    """
    self.region = Region(region)
    self.symbols = symbols
    logging.debug("RegionPermutesSymbols(%s, %s)", region, symbols)
    if len(symbols) != len(self.region.cells):
      raise Exception("Can't permute " + str(len(symbols)) + " symbols into " + str(len(self.region.cells)) + " cells")

  def __str__(self):
    return super().__str__() + ': ' + str(self.symbols) + ' in ' + str(self.region)

  def apply(self, puzzle):
    self.expandStars(puzzle)

    if len(self.symbols) == 0:  # Nothing to do, so finish this constraint
      logging.debug("discarding empty region")
      return []

    if len(self.symbols) == 1:  # Only one symbols is possible
      # We can't get here unless there's also exactly one cell in the region.
      # Set that in the solution, and then we're done with this constraint.
      logging.debug("Placing %s at %s", self.symbols[0], self.region.cells[0])
      puzzle.solution.setCell(self.region.cells[0], self.symbols)
      return []

    result = self.partition(puzzle)
    if result is not None: return result

    # If nothing produced new constraints, keep this one.
    return [self]

# Steps in solving the puzzle

  def expandStars(self, puzzle):
    """ For every cell in the region that has a '*' in its Placements,
        replace the '*' with a list of all the symbols.
    """
    for coords in self.region:
      cell = puzzle.solution.at(coords)
      if cell == '*' or cell == ['*']:
        puzzle.solution.setCell(coords, self.symbols)

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
    for coords in self.region:
      subset = puzzle.solution.at(coords)
      if len(subset) < len(self.symbols):
        symbols = '|'.join(subset)
        if symbols in index:
          index[symbols].append(coords)
        else:
          index[symbols] = [coords]

    for symbols, coordList in index.items():
      subset = symbols.split('|')
      if len(subset) == len(coordList):
        # There are the same number of symbols in this set as cells to put them in.
        # So, the given coordList can be partitioned off from the rest of the region.
        remainderRegion = subtractLists(self.region.cells, coordList)
        remainderSymbols = subtractLists(self.symbols, subset)
        logging.debug("Partitioning out %s in %s, leaving %s in %s", 
          subset, coordList, remainderSymbols, remainderRegion)
        result = [RegionPermutesSymbols(coordList, subset), 
          RegionPermutesSymbols(remainderRegion, remainderSymbols)]

        # We cank also remove all the subset symbols from the remainder region.
        for coords in remainderRegion:
          puzzle.solution.eliminateAt(coords, subset)

        return result

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
