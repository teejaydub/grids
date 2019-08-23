import logging

def showCell(cell):
  """ Returns a string representing a given cell's contents.
      It could be one symbol, or several potential symbols.
  """
  if not cell:
    return '_'
  if len(cell) == 1:
    return cell[0]
  else:
    return '(' + ' '.join(cell) + ')'

class Placements():
  """ A copy of an entire puzzle grid, with a set of possible symbols for each cell.
      If a cell has only one symbol, it's fully determined.
      If it has no symbols, the puzzle is unsolveable.
  """
  # A list of lists (for two dimensions), each cell of which contains a list of possible symbols.
  cells = None

  def __init__(self, initial):
    self.cells = self.parse(initial)

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
        return [list(row.strip()) for row in x]
      elif isinstance(x[0], list):
        # It's an array of arrays.
        # Assume it's in fully-defined list form.
        return x
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
      if len(cell) != 1:
        return False
    return True

  def at(self, coords):
    """ Returns the contents of the grid cell at the specified coordinates (a list or tuple).
    """
    return self.cells[coords[0]][coords[1]]

  def setCell(self, coords, contents):
    self.cells[coords[0]][coords[1]] = contents

  def eliminateAt(self, coords, symbols):
    """ Remove all symbols from the given symbol list from this placement 
        at the given coordinates.
    """
    cell = self.cells[coords[0]][coords[1]]
    self.setCell(coords, [s for s in cell if not s in symbols])
