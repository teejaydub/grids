import itertools
import logging

from constraints import chess
from constraints.symbolSet import SymbolSet

def showCell(cell):
  """ Returns a string representing a given cell's contents.
      It could be one symbol, or several potential symbols.
  """
  if not cell:
    return '_'
  if len(cell) == 1:
    return cell.value()
  else:
    return str(cell)

class Placements():
  """ A copy of an entire puzzle grid, with a set of possible symbols for each cell.
      If a cell has only one symbol, it's fully determined.
      If it has no symbols, the puzzle is unsolveable.
  """
  # A list of lists (for two dimensions), each cell of which contains a SymbolSet of possible symbols.
  cells = None
  changed = False

  def __init__(self, initial):
    # logging.debug("Placements(%s)", initial)
    self.cells = self.parse(initial)
    # logging.debug("  = \n%s", self)

  def parse(self, x):
    """ Returns grid contents matching the input.
        Handles multiple formats:
          >>> print(Placements(['12', '21']))  # array of strings, one per row, with one char per column
          [ 1 2
            2 1 ]
          >>> print(Placements(" 12 \\n 34"))  # a single string, with rows separated by newlines
          [ 1 2
            3 4 ]
    """
    if x is None:
      logging.debug("Initializing Placements from None")
      return None
    elif isinstance(x, str):
      # A single string: split into lines and treat it recursively.
      return self.parse(x.splitlines())
    elif isinstance(x, list):
      if isinstance(x[0], str):
        # The strings must each be a row of single-character symbols.
        return [[SymbolSet(cell) for cell in list(row.strip())] for row in x]
      elif isinstance(x[0], list):
        # It's an array of arrays.
        # Assume it's in fully-defined list form.
        # Convert each cell to a SymbolSet.
        return [[SymbolSet(cell) for cell in row] for row in x]
      else:
        raise Exception("Can't initialize with list " + str(x))
    else:
      raise Exception("Can't initialize with " + str(x))

  def size(self):
    """ Returns a two-dimensional array containing the grid size.
        For now, assumes the grid is fully populated.
    """
    return [len(self.cells), len(self.cells[0])]

  def dimensions(self):
    return 2

  def __str__(self):
    lines = [' '.join(showCell(col) for col in row) for row in self.cells]
    return '[ ' + "\n  ".join(lines) + ' ]'

  def all(self):
    """ Iterate through all cells in the grid """
    for row in self.cells:
      for cell in row:
        yield cell

  def isSolved(self):
    """ Return True iff all cells contain one item.
        >>> Placements([['1','2']]).isSolved()
        True
        >>> Placements([['1',['2', '3']]]).isSolved()
        False
    """
    for cell in self.all():
      if len(cell) != 1 or cell.value() == '*':
        return False
    return True

  def isUnsolvable(self):
    """ Return True if at least one cell contains no items.
        >>> Placements([[[]], [['1']]]).isUnsolvable()
        True
        >>> Placements([[['1'], ['2', '3']]]).isUnsolvable()
        False
    """
    for cell in self.all():
      if len(cell) == 0:
        return True
    return False

  def at(self, location):
    """ Returns the contents of the grid cell at the specified coordinates (a SymbolSet).
    """
    return self.cells[location[0]][location[1]]

  def indexSymbolsIn(self, region):
    """ Return a reverse index, that maps a single symbol to a list of locations where it occurs.
        Limits the index to the locations within the given region.
    """
    index = {}
    for location in region:
      for s in self.at(location):
        index.setdefault(s, []).append(location)
    return index

  def setCell(self, location, contents):
    if isinstance(contents, str):
      # If I set it to a single symbol, make it into a list.
      new = SymbolSet([contents])
    else:
      new = SymbolSet(contents)
    # logging.debug("setCell: %s = %s", chess.location(location), contents)
    if self.cells[location[0]][location[1]] != new:
      self.cells[location[0]][location[1]] = new
      self.changed = True

  def eliminateAt(self, location, symbols):
    """ Remove the given list of symbols from this placement 
        at the given coordinates.
    """
    cell = self.cells[location[0]][location[1]]
    new = cell.difference(symbols)
    if new != cell:
      self.setCell(location, new)
      self.changed = True

  def eliminateThroughout(self, locations, symbols):
    """ Remove the given iterable of symbols from this placement
        everywhere within the given list of locations (which can be a Region).
    """
    for location in locations:
      self.eliminateAt(location, symbols)

  def intersectAt(self, location, symbols):
    """ Eliminate symbols other than the given ones for the given location. """
    cell = self.cells[location[0]][location[1]]
    if len(cell) == 1 and cell.value() == '*':
      new = SymbolSet(symbols)
    else:
      new = cell & symbols
    if new != cell:
      self.setCell(location, new)
      self.changed = True

  def intersectThroughout(self, locations, symbols):
    """ Only the given symbols are valid within the given locations. """
    for location in locations:
      self.intersectAt(location, symbols)