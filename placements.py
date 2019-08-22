import logging

class Placements():
  """ A copy of an entire puzzle grid, with a set of possible symbols for each cell.
      If a cell has only one symbol, it's fully determined.
      If it has no symbols, the puzzle is unsolveable.
  """
  # A list of lists (for two dimensions), each cell of which contains an indexable containing symbols.
  cells = None
  symbolsAreChars = True

  def __init__(self, initial):
    self.cells = self.parse(initial)

  def parse(self, x):
    """ Returns grid contents matching the input.
        Handles multiple formats:
          >>> print(Placements(['12', '21']))  # array of strings, one per row, with one char per column
          [ 12
            21 ]
          >>> print(Placements(" 12 \\n 34"))  # a single string, with rows separated by newlines
          [ 12
            34 ]
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
        raise Exception("Can''t initialize with nested list yet: " + str(initial))
      else:
        raise Exception("Can't initialize with list " + str(initial))
    else:
      raise Exception("Can't initialize with " + str(initial))

  def size(self):
    """ Returns a two-dimensional array containing the grid size.
        For now, assumes the grid is fully populated.
    """
    return [len(self.cells), len(self.cells[0])]

  def dimensions(self):
    return 2

  def __str__(self):
    if self.symbolsAreChars:
      lines = [''.join(row) for row in self.cells]
    else:
      lines = self.cells
    return '[ ' + "\n  ".join(lines) + ' ]'
