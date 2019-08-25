from functools import reduce
import logging
import operator
import re

def parseChess(s):
  """ Given a chess-style pair of coordinates like a1,
      return a pair of integer coordinates.

      Examples:
      >>> parseChess('b3')
      (1, 2)
  """
  (r, c) = re.search("^([a-z])(\d+)$", s).groups()
  r = ord(r) - ord('a')
  c = int(c) - 1
  return (r, c)

class Region():
  def __init__(self, region):
    """ Regions can be specified by a string of two chess-style coordinates separated by a dash,
        or as a list of 0-relative coordinate pairs,
        or as a single pair of coordinates to indicate the lower-right corner of an upper-left region.

        Examples:
        >>> str(Region('a1-b2'))
        '[(0, 0), (0, 1), (1, 0), (1, 1)]'
        >>> str(Region([(0,0),(0,1),(1,0)]))
        '[(0, 0), (0, 1), (1, 0)]'
        >>> str(Region([1, 2]))
        '[(0, 0), (0, 1)]'
        >>> str(Region([1, 1]))
        '[(0, 0)]'
        >>> str(Region([0, 0]))
        '[]'
        >>> str(Region((1, 1)))
        '[(0, 0)]'
    """
    if isinstance(region, str):
      # Chess-style string range: find the start and end as coordinates.
      (first, last) = region.split('-')
      (startRow, startCol) = parseChess(first)
      (endRow, endCol) = parseChess(last)

      self.cells = []
      for r in range(startRow, endRow + 1):
        for c in range(startCol, endCol + 1):
          self.cells += [(r, c)]
    elif isinstance(region, (list, tuple)):
      if len(region) > 0 and isinstance(region[0], int):
        # Looks like a single set of coordinates.
        self.cells = reduce(operator.concat, 
          [[(r, c) for r in range(0, region[0])] for c in range(0, region[1])],
          [])
      else:
        # List of coordinate tuples.
        self.cells = region
    elif isinstance(region, Region):
      self.cells = region.cells
    else:
      raise Exception("Don't know how to create a Region from " + str(region))

  def __str__(self):
    return str(self.cells)

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
        >>> Region('a1-b2').intersect(Region('a1-a9'))
        [(0, 0), (0, 1)]
    """
    return Region([cell for cell in other if cell in self.cells])
