import copy
import logging
import re

from . import chess
from .constraint import Constraint
from .region import Region, RegionConstraint, RegionSymbolsConstraint

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

class MathOp(RegionConstraint):
  """ Applies a math operator to the values of symbols in a region,
      and requires the result to be a given target value.
  """
  def __init__(self, region, operator, operatorName, inverse, inverseName, target, isCommutative=True):
    super().__init__(region)
    self.operator = operator
    self.operatorName = operatorName
    self.inverse = inverse
    self.inverseName = inverseName
    self.target = target
    self.isCommutative = isCommutative

  def __str__(self):
    return super().__str__() + ': '+ self.region.display(self.operatorName, brackets=False) + ' = ' + str(self.target)

  def techniques(self):
    return super().techniques() + [self.singleValue, self.removeKnown]

  def singleValue(self, puzzle):
    """ Technique to set the target value as a symbol if the region contains only one cell. """
    if puzzle.symbols:
      if self.region.size() == 1:
        assert str(self.target) in puzzle.symbols
        assert self.isCommutative  # otherwise, you shouldn't end up with a single cell
        logging.debug("Single value: %s has a target value of %s",
          chess.location(self.region.cells[0]), self.target)
        puzzle.logTechnique('singleValue')
        puzzle.solution.setCell(self.region.cells[0], str(self.target))
        return []

  def removeKnown(self, puzzle):
    """ Technique to remove cells with known values from the region,
        and generate a new constraint that adjusts the target appropriately.
    """
    for location in self.region:
      cell = puzzle.solution.at(location)
      if len(cell) == 1 and cell[0] != '*':
        value = int(cell[0])
        if self.isCommutative:
          # For + and *, we can just apply the inverse operator to our current target to find the new target.
          new = copy.copy(self)
          new.target = self.inverse(self.target, value)
          new.region = self.region.subtract([location])
          logging.debug("Remove known: since %s and %s = %s, %s %s %s = %s",
            self, chess.location(location), value, self.target, self.inverseName, value, new.target)
          puzzle.logTechnique('removeKnown')
          return [new]
        else:
          # For - and / with two cells, there are now two possibilities for the remaining cell.
          # Make a RegionSymbolsConstraint for that, and eliminate values.
          assert self.region.size() == 2
          a = str(self.inverse(self.target, value))
          b = str(self.operator(value, self.target))
          logging.debug("Remove known: since %s and %s = %s, %s is %s or %s",
            self, chess.location(location), value, self.region.subtract([location]), a, b)
          puzzle.logTechnique('removeKnown')
          return [RegionSymbolsConstraint(self.region.subtract([location]), [a, b])]

class Math(MathOp):
  """ Convenience for more compact typing in input YAML.
      >>> print(Math("a1+a2+a3 = 6").apply(None)[0])
      SumIs: a1+a2+a3 = 6
  """
  def __init__(self, initializer):
    leftside, rightside = initializer.split('=')
    operator = re.search('[+-/*x]', leftside).group()
    squares = leftside.split(operator)
    super().__init__(squares, None, operator, None, None, int(rightside.strip()))

  def apply(self, puzzle):
    """ Chain to the appropriate specific operator class. """
    if self.operatorName == '+':
      return [SumIs(self.region, self.target)]
    if self.operatorName == '-':
      return [DifferenceIs(self.region, self.target)]
    if self.operatorName == '/':
      return [QuotientIs(self.region, self.target)]
    if self.operatorName in '*x':
      return [ProductIs(self.region, self.target)]
    else:
      return []

class SumIs(MathOp):
  """ A MathOp for addition. """
  def __init__(self, region, target):
    super().__init__(region, lambda x,y: x + y, '+', lambda x,y: x - y, '-', target)

class DifferenceIs(MathOp):
  """ A MathOp for subtraction. """
  def __init__(self, region, target):
    super().__init__(region, lambda x,y: x - y, '-', lambda x,y: x + y, '+', target, isCommutative=False)

class ProductIs(MathOp):
  """ A MathOp for multiplication. """
  def __init__(self, region, target):
    super().__init__(region, lambda x,y: x * y, '*', lambda x,y: x / y, '/', target)

class QuotientIs(MathOp):
  """ A MathOp for division. """
  def __init__(self, region, target):
    super().__init__(region, lambda x,y: x / y, '/', lambda x,y: x * y, '*', target, isCommutative=False)
