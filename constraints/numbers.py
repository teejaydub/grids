import copy
import logging
import math
import re

from . import chess
from .factoring import *
from .constraint import Constraint
from .region import Region, RegionConstraint, RegionSymbolsConstraint
from .regionSymbolLists import RegionSymbolLists
from .symbolSet import SymbolSet

class SymbolsNumericDigits(Constraint):
  """ Sets the symbol set to the numeric digits, 1-9,
      or to the given maximum digit value.
  """
  def __init__(self, max_digits=9):
    self.max_digits = max_digits

  def apply(self, puzzle):
    puzzle.symbols = SymbolSet([str(x) for x in range(1, self.max_digits + 1)])
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
    return super().techniques() + [self.singleValue, self.removeKnown, self.twoCellOperator]

  def singleValue(self, puzzle):
    """ Technique to set the target value as a symbol if the region contains only one cell. """
    if puzzle.symbols and puzzle.solution:
      if self.region.size() == 1:
        assert self.isCommutative  # otherwise, you shouldn't end up with a single cell
        logging.debug("Single value: %s has a target value of %s",
          chess.location(self.region.cells[0]), self.target)
        assert str(self.target) in puzzle.symbols
        puzzle.logTechnique('singleValue')
        puzzle.solution.setCell(self.region.cells[0], str(self.target))
        return []

  def removeKnown(self, puzzle):
    """ Technique to remove cells with known values from the region,
        and generate a new constraint that adjusts the target appropriately.
    """
    if puzzle.solution:
      for location in self.region:
        cell = puzzle.solution.at(location)
        if len(cell) == 1 and cell.value() != '*':
          value = int(cell.value())
          if self.isCommutative:
            # For + and *, we can just apply the inverse operator to our current target to find the new target.
            new = copy.copy(self)
            new.target = round(self.inverse(self.target, value))
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
            b = self.operator(value, self.target)

            # If b is not an integer, it's not an option.
            if round(b) != b:
              logging.debug("Remove known: since %s and %s = %s, %s is %s (not %s)",
                self, chess.location(location), value, self.region.subtract([location]), a, b)
              puzzle.logTechnique('removeKnown')
              return [RegionSymbolsConstraint(self.region.subtract([location]), {a})]
            else:
              b = str(round(b))
              logging.debug("Remove known: since %s and %s = %s, %s is %s or %s",
                self, chess.location(location), value, self.region.subtract([location]), a, b)
              puzzle.logTechnique('removeKnown')
              return [RegionSymbolsConstraint(self.region.subtract([location]), {a, b})]

  def inverseSet(self, value):
    """ Apply the inverse operator to target and value and return the resulting symbol set.
        Remove non-integer values from the result.
        One or two values may be produced.
    """
    result = [self.inverse(self.target, value)]
    if not self.isCommutative:
      result.append(self.operator(value, self.target))
    result = filter(lambda x: x == round(x), result)  # eliminate non-integers
    return SymbolSet([str(round(x)) for x in result])

  def checkPair(self, puzzle, locations):
    """ Check the ordered pair at the first two of the given list of locations.
        Eliminate values from the first if the inverse operation doesn't produce 
        a valid result in the second.        
    """
    cells = list(map(puzzle.solution.at, locations))
    for xs in cells[0]:
      x = int(xs)
      y = self.inverseSet(x)

      if not (y & cells[1]):
        puzzle.solution.eliminateAt(locations[0], xs)
        logging.debug("Operator: Because %s and %s%s%s = %s, which isn't in %s, %s can't be in %s", 
          self, 
          self.target, self.inverseName, xs, y,
          cells[1],
          xs, chess.location(locations[0]))
        puzzle.logTechnique('twoCellOperator')

  def twoCellOperator(self, puzzle):
    """ If the region has two cells, we can run through all possible pairs of values, 
        and filter from the cells accordingly.
    """
    if self.region.size() == 2 and puzzle.symbols and puzzle.solution:
      if puzzle.solution.isInitializedThroughout(self.region):
        self.checkPair(puzzle, self.region.cells)
        self.checkPair(puzzle, list(reversed(self.region.cells)))

class Math(MathOp):
  """ Convenience for more compact typing in input YAML.
      >>> print(Math("a1+a2+a3 = 6").apply(None)[0])
      SumIs: a1+a2+a3 = 6
  """
  def __init__(self, initializer):
    leftside, rightside = initializer.split('=')
    try:
      operator = re.search('[+-/*x]', leftside).group()
    except:
      operator = '+'  # todo: more error checking - this is for "d1 = 7" e.g.
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
    super().__init__(region, sumF, '+', differenceF, '-', target)

class DifferenceIs(MathOp):
  """ A MathOp for subtraction. """
  def __init__(self, region, target):
    super().__init__(region, differenceF, '-', sumF, '+', target, isCommutative=False)

class ProductIs(MathOp):
  """ A MathOp for multiplication. """
  def __init__(self, region, target):
    super().__init__(region, productF, '*', quotientF, '/', target)
    self.factored = False

  def techniques(self):
    return super().techniques() + [self.primeFactors]

  def primeFactors(self, puzzle):
    """ Figure out the possible symbols for this region using prime factors.
        All symbols must either be prime factors, or products of prime factors.
        Do this just one time for this constraint.
    """
    if puzzle.symbols and puzzle.solution and not self.factored:
      # Step through all combinations of the factors of the target.
      allSymbols = SymbolSet()
      allSymbolLists = []
      for factors in factorizations(self.target, self.region.size()):
        factorSymbolList = [str(f) for f in factors]
        factorSet = SymbolSet(factorSymbolList)
        # Include a factorization only if all its factors are valid symbols in the puzzle.
        if factorSet <= puzzle.symbols:
          allSymbolLists.append(factorSymbolList)
          allSymbols.update(factorSet)

      # Generate a RegionSymbolLists constraint
      new = RegionSymbolLists(self.region, allSymbolLists)
      logging.debug("Prime factors: %s implies %s", self, new)
      puzzle.logTechnique('primeFactors')
      self.factored = True
      return [self, new]

class QuotientIs(MathOp):
  """ A MathOp for division. """
  def __init__(self, region, target):
    super().__init__(region, quotientF, '/', productF, '*', target, isCommutative=False)

class AllCellsMustHaveMathOp(Constraint):
  """ Require that every cell in the puzzle be included in a MathOp constraint's region.
      Also creates the initial placement, when the size is known, as an array of '*'.
  """
  def apply(self, puzzle):
    if puzzle.size:
      # Create the initial placement.
      if not puzzle.initial:
        logging.debug("Setting initial state to blank")
        puzzle.setInitial([puzzle.size[1] * '*' for i in range(puzzle.size[0])])
      else:
        logging.debug("About to set initial state, but it's already:\n%s", puzzle.initial)

      # Find out if any squares are uncovered.
      for row in range(0, puzzle.size[0]):
        for col in range(0, puzzle.size[1]):
          if not self.inMathOp(puzzle, (row, col)):
            raise Exception("The cell " + chess.location((row, col)) + " doesn't have a MathOp constraint.")

      return []  # finished
    else:
      return [self]  # wait for size

  def inMathOp(self, puzzle, location):
    """ Return True iff the puzzle has a MathOp constraint that includes the given location in its Region. """
    for c in puzzle.constraints:
      if isinstance(c, MathOp):
        if c.contains(location):
          return True
    return False