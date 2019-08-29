import copy
import functools
import io
import logging
import pathlib
import yaml

from constraints import *
from placements import Placements

def concatWithSep(elements, sep = ','):
  return sep.join(x for x in elements if x)

class Puzzle:
  """ Holds a set of initial conditions and constriants. 
  """
  def __init__(self):
    self.constraints = []
    self.dimensions = None
    self.size = None
    self.symbols = None  # a SymbolSet
    self.symbolsAreChars = True  # True if all symbols are single-character strings  (to do: default to None and set with symbols)
    self.initial = None  # a Placement
    self.solution = None  # a Placement, set when a solution is found
    self.stats = None
    self.techniqueCallback = None  # Set to call back each time a technique is used.

  def addConstraints(self, constraints):
    """ Add constraints from various sources, distinguished by type.
      >>> p = Puzzle()
      >>> p.addConstraints({'size': [2, 2], 'initial': ['12', '21']})
      >>> str(p)
      '[ 1 2\\n  2 1 ]'
      >>> p.addConstraints(['Unknown'])
      Traceback (most recent call last):
      ...
      Exception: Can't load constraint Unknown: {} - KeyError
    """
    if constraints is None:
      return
    logging.debug("Loading constraints: %s", constraints)
    if isinstance(constraints, io.IOBase):
      self.addConstraints(yaml.safe_load(constraints))
    elif isinstance(constraints, list):
      for constraint in constraints:
        self.addConstraints(constraint)
    elif isinstance(constraints, str):
      self.addConstraintNamed(constraints)
    elif isinstance(constraints, dict) and len(constraints) > 0:
      first = list(constraints.keys())[0]
      if 'name' in constraints:
        # Dictionary of constraint constructor properties + a class name
        self.addConstraintNamed(constraints['name'], constraints)
      elif len(constraints) == 1 and first[0].isupper():
        # A single capitalized word: Try loading a constraint with that name and an "initializer" property.
        self.addConstraintNamed(first, {'initializer': constraints[first] })
      else:
        # Absorb all named Puzzle properties we recognize.
        self.setDimensions(constraints.get('dimensions', None))
        self.setSize(constraints.get('size', None))
        self.setInitial(constraints.get('initial', None))
        self.addConstraints(constraints.get('constraints', None))
    else:
      logger.warning("Unrecognized item: %s", constraints)

  def addConstraintNamed(self, c, new_args={}):
    """ Adds a constraint with the given name, if we know it.
        Pass the specified arguments to its constructor.
        Otherwise, if the constraint is a string containing '=', load a Math equation.
        Otherwise, if it's the name of a file in theh current directory,
        optionally with the suffix ".yml" or ".yaml", load constraints from that file.
        Otherwise, raise an exception.
    """
    logging.debug("loading constraint: %s", c)
    if isinstance(c, str) and '=' in c:
      return self.addConstraintNamed('Math', {'initializer': c})
    for extension in ['', '.yml', '.yaml']:
      if self.tryLoad(c + extension):
        return
    try:
      constraintClass = globals()[c]
      if 'name' in new_args:
        del new_args['name']  # so it doesn't get passed as an argument to the constraint constructor
      constraint = constraintClass(**new_args)
      self.constraints.append(constraint)
    except Exception as e:
      raise Exception("Can't load constraint " + c + ': ' + str(new_args) + " - " + e.__class__.__name__)

  def tryLoad(self, filename):
    """ If filename exists, load constraints from it and return True.
        Otherwise, return False.
    """
    try:
      p = pathlib.Path(filename)
      self.addConstraints(p.open())
      return True
    except OSError:  # let other loading exceptions propagate
      return False

  def __str__(self):
    """ String conversion.  Shows whatever we know about the puzzle.
      >>> p = Puzzle()
      >>> print(p)
      (empty Puzzle)
      >>> p.setDimensions(2)
      >>> print(p)
      (2-dimensional)
      >>> p.setSize([2,2])
      >>> print(p)
      (2x2)
      >>> p.setInitial(['12', '34'])
      >>> print(p)
      [ 1 2
        3 4 ]
    """
    result = ''
    if self.solution:
      result = str(self.solution)
    elif self.initial:
      result = str(self.initial)
    elif self.size:
      result = self.formatSize(self.size)
    elif self.dimensions:
      result = '(' + str(self.dimensions) + "-dimensional)"
    if self.constraints:
      result = concatWithSep([result, self.constraintNames()], "\n")
    if result == '':
      result = "(empty Puzzle)"
    return result

  def constraintNames(self):
    """ Returns a printable list of the current constraint set. """
    return '{\n  ' + '\n  '.join([str(c) for c in self.constraints]) + '\n}'

  def formatSize(self, size):
    return '(' + functools.reduce(lambda a, b: a + 'x' + b, map(str, self.size)) + ")"

  def setDimensions(self, dimensions):
    if dimensions:
      if self.dimensions:
        if self.dimensions != dimensions:
          raise Exception("Conflicting dimensions: " + str(self.dimensions) + " vs. " + str(dimensions))
      else:
        self.dimensions = dimensions

  def setSize(self, size):
    if size:
      if self.size:
        if self.size != size:
          raise Exception("Conflicting sizes: " + str(self.size) + " vs. " + str(size))
      else:
        self.setDimensions(len(size))
        self.size = size

  def setInitial(self, initial):
    """ Sets the initial contents of the grid.
        The syntax is from Placements:
          >>> p = Puzzle()
          >>> p.setInitial(['12', '21'])  # array of strings, one per row, with one char per column
          >>> print(p)
          [ 1 2
            2 1 ]
          >>> p.setInitial(" 12 \\n 34")  # a single string, with rows separated by newlines
          >>> print(p)
          [ 1 2
            3 4 ]
    """
    if initial:
      self.initial = Placements(initial)
      self.solution = Placements(initial)
      self.setSize(self.initial.size())
      self.expandStars()

  def expandStars(self):
    """ For every cell in the solution that contains '*',
        replace the '*' with a list of all the symbols.
    """
    logged = False
    if self.size and self.solution and self.symbols:
      for location in region.Region(self.size):
        cell = self.solution.at(location)
        if cell.value() == '*':
          if not logged:
            logging.debug("Expanding stars.")
            logged = True
          self.solution.setCell(location, self.symbols)

  def reduceConstraints(self):
    """ Apply all constraints.
        Remove all the finished ones.
        Return true if something changed - if there are a different set of constraints
        as a result of the reduction, or if the solution changed.
    """
    # This is the simplest implementation, but it can't tell when anything changes.
    # self.constraints = [c.apply(self) for c in self.constraints]
    constraintsChanged = False
    if self.solution:
      self.solution.changed = False

    self.expandStars()
    newConstraints = []
    for c in self.constraints:
      changes = c.apply(self)
      if changes != [c]:
        constraintsChanged = True
        # logging.debug("constraint change from %s to %s", c, changes)
      if changes:
        newConstraints.extend(changes)
    self.constraints = newConstraints
    
    self.stats['passes'] += 1
    return constraintsChanged or (self.solution and self.solution.changed)

  def logTechnique(self, name):
    """ Notes down the use of a named technique while solving. """
    t = self.stats['techniques']
    t[name] = t.setdefault(name, 0) + 1
    if self.techniqueCallback:
      self.techniqueCallback(name)

  def solve(self):
    """ Attempt to find a solution to the initial condition and constraints.
        If one can be found, return True and put its position in self.solution.
        If not, return False.
    """
    # Collect some stats as we go.
    self.stats = {'passes': 0, 'techniques': {} }
    # Reduce the constraints as far as possible analytically.
    while self.reduceConstraints() and not (self.isSolved() or self.isUnsolvable()):
      logging.debug("\nPass %s:\n%s", self.stats['passes'], self)
    return self.isSolved()

  def isSolved(self):
    " Return True if the solution is complete - with only one symbol placement per cell. "
    if not self.solution:
      return False
    return self.solution.isSolved()

  def isUnsolvable(self):
    " Return True if the puzzle can't be solved - some cells have no placement options. "
    if not self.solution:
      return False
    return self.solution.isUnsolvable()