from functools import reduce
import itertools
import logging
import operator

from .listutils import subtractLists
from .constraint import Constraint
from .symbolSet import SymbolSet, SymbolList
from . import chess

class Region():
  def __init__(self, region):
    """ Regions can be specified by a string of two chess-style coordinates separated by a dash,
        or as a list of 0-relative coordinate pairs,
        or as a single pair of coordinates to indicate the size of an upper-left region.

        Examples:
        >>> str(Region('a1-b2'))
        '[a1 a2 b1 b2]'
        >>> str(Region('a1 a2 b3'))
        '[a1 a2 b3]'
        >>> str(Region([(0,0),(0,1),(1,0)]))
        '[a1 a2 b1]'
        >>> str(Region([1, 2]))
        '[a1 a2]'
        >>> str(Region([1, 1]))
        '[a1]'
        >>> str(Region([0, 0]))
        '[]'
        >>> str(Region((1, 1)))
        '[a1]'
    """
    if isinstance(region, str):
      # Strings are parsed as chess notation.
      self.cells = chess.parseList(region)
    elif isinstance(region, (list, tuple)):
      if len(region) > 0 and isinstance(region[0], int):
        # Looks like a single set of coordinates.
        self.cells = reduce(operator.concat, 
          [[(r, c) for r in range(0, region[0])] for c in range(0, region[1])],
          [])
      elif len(region) > 0 and isinstance(region[0], str):
        # A list of strings: interpret individual elements as chess notation.
        self.cells = []
        for s in region:
          self.cells.extend(chess.parseList(s))
      elif len(region) > 0 and isinstance(region[0], (list, tuple)) and len(region[0]) > 0 and isinstance(region[0][0], int):
        # List of coordinate tuples.
        self.cells = region
      elif len(region) == 0:
        self.cells = []
      else:
        raise Exception("Don't know how to create a Region from " + str(region))
    elif isinstance(region, Region):
      self.cells = region.cells
    else:
      raise Exception("Don't know how to create a Region from " + str(region))

  def __str__(self):
    return self.display()

  def display(self, sep=' ', brackets=True):
    """ Return a display string in chess notation, using the given separator between squares.
        >>> Region([(0,0), (0,1)]).display()
        '[a1 a2]'
        >>> Region([(0,0), (0,1)]).display(', ')
        '[a1, a2]'
        >>> Region([(0,0), (0,1)]).display(', ', brackets=False)
        'a1, a2'
    """
    result = sep.join([chess.location(c) for c in self.cells])
    if brackets:
      result = '[' + result + ']'
    return result

  def size(self):
    return len(self.cells)

  def __iter__(self):
    """ Yield the coordinate tuples in the Region. """
    for cell in self.cells:
      yield cell

  def isEmpty(self):
    return len(self.cells) == 0

  def contains(self, location):
    """ Return True if the given coordinate pair location is within this Region.
        >>> Region('a1-b2').contains((0, 0))
        True
        >>> Region('a1-b2').contains((1, 2))
        False
    """
    return location in self.cells

  def hasSubset(self, other):
    """ Return True if all cells in the other Region (or list of locations)
        are contained within this Region.

        >>> Region('a1-b2').hasSubset(Region('a1'))
        True
        >>> Region('a1-b2').hasSubset(Region('b3'))
        False
    """
    for cell in other:
      if not cell in self.cells:
        return False
    return True

  def hasProperSubset(self, other):
    """ Return True if other is a subset of self, and it's also smaller.

        >>> Region('a1-b2').hasProperSubset(Region('a1-b2'))
        False
        >>> Region('a1-b2').hasProperSubset(Region('a1-b3'))
        False
        >>> Region('a1-b2').hasProperSubset(Region('a1-b1'))
        True
    """
    return len(other.cells) < len(self.cells) and self.hasSubset(other)

  def intersect(self, other):
    """ Return a Region that contains all cells that are in both self and other. 
        >>> print(Region('a1-b2').intersect(Region('a1-a9')))
        [a1 a2]
    """
    return Region([cell for cell in other if cell in self.cells])

  def subtract(self, other):
    """ Return a Region that contains all cells in self that aren't in other.
        >>> print(Region('a1-b2').subtract(Region('a1 c5')))
        [a2 b1 b2]
    """
    return Region([cell for cell in self if not cell in other])

class RegionConstraint(Constraint):
  """ A Constraint that is applied over a Region. """
  def __init__(self, region):
    super().__init__()
    self.region = Region(region)

  def contains(self, location):
    return self.region.contains(location)

  def techniques(self):
    return super().techniques() + [self.empty]

  def empty(self, puzzle):
    """ Catch any empty constraints and discard them. """
    if self.region.isEmpty():
      logging.debug("discarding empty region")
      return []

class RegionSymbolsConstraint(RegionConstraint):
  """ A RegionConstraint that knows a subset of the puzzle's symbols
      that can be used within its region.
  """
  def __init__(self, region, symbols):
    super().__init__(region)
    self.symbols = SymbolSet(symbols)

  def __str__(self):
    return super().__str__() + ': ' + str(self.symbols) + ' in ' + str(self.region)

  def techniques(self):
    return super().techniques() + [self.filterFromPuzzle, self.solo, self.filterSolution]

  def filterFromPuzzle(self, puzzle):
    """ Eliminate any symbols from this constraint that aren't in the puzzle's symbol set. """
    if puzzle.symbols and self.symbols > puzzle.symbols:
      return [RegionSymbolsConstraint(self.region, SymbolSet(self.symbols & puzzle.symbols))]

  def solo(self, puzzle):
    """ If there's only one symbol, it must be the symbol for the entire region.
        Set that in the solution, and then we're done with this constraint.
    """
    if puzzle.solution and len(self.symbols) == 1:  # Only one symbol is possible
      for location in self.region:
        if puzzle.solution.setCell(location, self.symbols):
          logging.debug("Solo: Placing %s at %s", self.symbols.value(), chess.location(location))
          puzzle.logTechnique('solo')
      return []

  def filterSolution(self, puzzle):
    """ Eliminate any symbols from this region that aren't in the constraint's symbol set.
    """
    if puzzle.solution:
      result = puzzle.solution.intersectThroughout(self.region, self.symbols)
      if result:
        logging.debug("Filter solution: symbols not in %s from %s", self.symbols, chess.locations(result))
        puzzle.logTechnique('filterSolution')

class RegionSymbolLists(RegionSymbolsConstraint):
  """ A RegionSymbolsConstraint that knows several lists of symbols,
      one per cell in the region, that have to be used in some order.
      Like several possible RegionPermutesSymbols, but trickier since symbols can be repeated,
      so you can't infer from the presence of the symbol in one place its absence in another.
      If there is only one symbol list and it doesn't contain duplicates, it's reduced to RegionPermutesSymbols.
  """
  def __init__(self, region, symbolSets):
    super().__init__(region, SymbolSet(itertools.chain.from_iterable(symbolSets)))  # the union of all the sets
    assert symbolSets
    self.symbolLists = [SymbolList(s) for s in symbolSets]

  def __str__(self):
    return self.__class__.__name__ + ': one of [' + ', '.join([str(s) for s in self.symbolLists]) + '] in ' + str(self.region)

  def techniques(self):
    return super().techniques() + []

  def filterFromPuzzle(self, puzzle):
    """ Overrides base case - must remove from the lists. """
    if puzzle.symbols:
      for slist in self.symbolLists:
        if len(SymbolSet(slist) - puzzle.symbols) > 0:
          # This symbol list has symbols that aren't in the puzzle: remove it.
          new = self.symbolLists.copy()
          new.remove(slist)
          return [RegionSymbolLists(self.region, new)]
