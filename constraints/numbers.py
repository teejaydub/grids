import logging

from .constraint import Constraint
from .region import Region

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

class MathOp(Constraint):
  """ Applies a math operator to the values of symbols in a region,
      and requires the result to be a given target value.
  """
  def __init__(self, region, operator, operatorName, target, isCommutative=True):
    self.region = Region(region)
    self.operator = operator
    self.operatorName = operatorName
    self.target = target
    self.isCommutative = isCommutative

  def __str__(self):
    return super().__str__() + ': '+ str(self.region) + ' = ' + str(self.target)

  def apply(self, puzzle):
    return [self]

class SumIs(MathOp):
  """ A MathOp for addition. """
  def __init__(self, region, target):
    super().__init__(region, lambda x,y: x + y, '+', target)

class DifferenceIs(MathOp):
  """ A MathOp for subtraction. """
  def __init__(self, region, target):
    super().__init__(region, lambda x,y: x - y, '-', target, isCommutative=False)

class ProductIs(MathOp):
  """ A MathOp for multiplication. """
  def __init__(self, region, target):
    super().__init__(region, lambda x,y: x * y, '*', target)

class QuotientIs(MathOp):
  """ A MathOp for division. """
  def __init__(self, region, target):
    super().__init__(region, lambda x,y: x / y, '/', target, isCommutative=False)
