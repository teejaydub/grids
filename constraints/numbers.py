import logging

from .constraint import Constraint

class SymbolsNumericDigits(Constraint):
  """ Sets the symbol set to the numeric digits, 1-9,
      or to the given maximum digit value.
  """
  def __init__(self, max_digits=9):
    self.max_digits = max_digits

  def apply(self, puzzle):
    puzzle.symbols = [str(x) for x in range(1, self.max_digits + 1)]
    logging.debug("Setting symbols to %s", puzzle.symbols)
    return []

class SymbolsNumericByDiameter(Constraint):
  """ Sets the symbol set to the diameter of the puzzle.
      Requires that the puzzle be square.
  """
  def apply(self, puzzle):
    if puzzle.size:
      # Require that the puzzle be square.
      if puzzle.size[1] != puzzle.size[0]:
        raise Exception("Puzzle must be square, but its size is %s" % puzzle.size)
      return [SymbolsNumericDigits(puzzle.size[0])]
    else:
      # We can finish later, whenever the size is known.
      return [self]