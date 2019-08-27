from functools import reduce
import logging
import operator

from .constraint import Constraint
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

class RegionConstraint(Constraint):
  """ A Constraint that is applied over a Region. """
  def __init__(self, region):
    super().__init__()
    self.region = Region(region)

  def techniques(self):
    return super().techniques() + [self.empty, self.solo]

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
    self.symbols = symbols

  def __str__(self):
    return super().__str__() + ': ' + self.showSymbols(self.symbols) + ' in ' + str(self.region)

  def techniques(self):
    return super().techniques() + [self.solo]

  def solo(self, puzzle):
    """ If there's only one symbol, it must be the symbol for a single cell.
        Set that in the solution, and then we're done with this constraint.
    """
    if len(self.symbols) == 1:  # Only one symbol is possible
      if puzzle.solution.at(self.region.cells[0]) != self.symbols:  # don't log if it's redundant
        logging.debug("Solo: Placing %s at %s", self.symbols[0], chess.location(self.region.cells[0]))
        puzzle.logTechnique('solo')
        puzzle.solution.setCell(self.region.cells[0], self.symbols)
      return []
