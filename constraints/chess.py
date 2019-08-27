""" Routines to convert between location coordinate tuples
    and easier-to read, chess-style coordinates.
"""

import re

def parseSquare(s):
  """ Given a chess-style pair of coordinates like a1,
      return a pair of integer coordinates.

      Examples:
      >>> parseSquare('b3')
      (1, 2)
  """
  (r, c) = re.search("^([a-z])(\d+)$", s).groups()
  r = ord(r) - ord('a')
  c = int(c) - 1
  return (r, c)

def parseRect(rect):
  """ Given a pair of chess-style squares,
      return a list of pairs of integer coordinates within the rectangle
      formed between those two squares, inclusive.

      Examples:
      >>> parseRect('a1-b2')
      [(0, 0), (0, 1), (1, 0), (1, 1)]
      >>> parseRect('b1-b1')
      [(1, 0)]
  """
  # Find the start and end as coordinates.
  (first, last) = rect.split('-')

  (startRow, startCol) = parseSquare(first)
  (endRow, endCol) = parseSquare(last)

  result = []
  for r in range(startRow, endRow + 1):
    for c in range(startCol, endCol + 1):
      result.append((r, c))
  return result

def parseList(chess):
  """ Convert a string containing a comma-separated list of chess-style squares and rectangles 
      into a list of pairs of integer coordinates.

      Examples:
      >>> parseList('')
      []
      >>> parseList('b1-b2')
      [(1, 0), (1, 1)]
      >>> parseList('a1, b1-b2 c2')
      [(0, 0), (1, 0), (1, 1), (2, 1)]
      >>> parseList('d3')
      [(3, 2)]
  """
  result = []
  for c in chess.split(' '):
    c = c.strip(' ,')
    if '-' in c:
      result.extend(parseRect(c))
    elif len(c):
      result.append(parseSquare(c))
  return result

def location(location):
  """ Given a pair of zero-relative coordinates, return a string naming a chess-style square.
      >>> location((0, 0))
      'a1'
  """
  if not isinstance(location, (list, tuple)) or not isinstance(location[0], int):
    raise Exception("Expecting location, got '" + str(location) + "'")
  return chr(ord('a') + location[0]) + str(location[1] + 1)

def locations(locations):
  """ Given a list of zero-relative coordinate pairs, return a string listing chess-style squares.
      >>> locations([(0, 0), (0, 1)])
      '[a1 a2]'
  """
  return '[' + ' '.join([location(loc) for loc in locations]) + ']'