from functools import reduce
import logging
import operator
import re

def parseChessSquare(s):
  """ Given a chess-style pair of coordinates like a1,
      return a pair of integer coordinates.

      Examples:
      >>> parseChessSquare('b3')
      (1, 2)
  """
  (r, c) = re.search("^([a-z])(\d+)$", s).groups()
  r = ord(r) - ord('a')
  c = int(c) - 1
  return (r, c)

def parseChessRect(rect):
  """ Given a pair of chess-style squares,
      return a list of pairs of integer coordinates within the rectangle
      formed between those two squares, inclusive.

      Examples:
      >>> parseChessRect('a1-b2')
      [(0, 0), (0, 1), (1, 0), (1, 1)]
      >>> parseChessRect('b1-b1')
      [(1, 0)]
  """
  # Find the start and end as coordinates.
  (first, last) = rect.split('-')

  (startRow, startCol) = parseChessSquare(first)
  (endRow, endCol) = parseChessSquare(last)

  result = []
  for r in range(startRow, endRow + 1):
    for c in range(startCol, endCol + 1):
      result.append((r, c))
  return result

def parseChessList(chess):
  """ Convert a string containing a comma-separated list of chess-style squares and rectangles 
      into a list of pairs of integer coordinates.

      Examples:
      >>> parseChessList('')
      []
      >>> parseChessList('b1-b2')
      [(1, 0), (1, 1)]
      >>> parseChessList('a1, b1-b2 c2')
      [(0, 0), (1, 0), (1, 1), (2, 1)]
      >>> parseChessList('d3')
      [(3, 2)]
  """
  result = []
  for c in chess.split(' '):
    c = c.strip(' ,')
    if '-' in c:
      result.extend(parseChessRect(c))
    elif len(c):
      result.append(parseChessSquare(c))
  return result

def locationToChessSquare(location):
  """ Given a pair of zero-relative coordinates, return a string naming a chess-style square.
      >>> locationToChessSquare((0, 0))
      'a1'
  """
  if not isinstance(location, (list, tuple)) or not isinstance(location[0], int):
    raise Exception("Expecting location, got '" + str(location) + "'")
  return chr(ord('a') + location[0]) + str(location[1] + 1)

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
      self.cells = parseChessList(region)
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
          self.cells.extend(parseChessList(s))
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
    result = sep.join([locationToChessSquare(c) for c in self.cells])
    if brackets:
      result = '[' + result + ']'
    return result

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
