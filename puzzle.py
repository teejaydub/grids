import functools
import io
import pathlib
import yaml

from constraints import *

def concatWithSep(elements, sep = ','):
  return sep.join(x for x in elements if x)

class Puzzle:
  """ Holds a set of initial conditions and constriants. 
  """
  def __init__(self):
    self.constraints = []
    self.dimensions = None
    self.size = None
    self.symbols = ['1', '2', '3', '4']  # a list of strings (to do: init to None and set by constraint)
    self.symbolsAreChars = True  # True if all symbols are single-character strings  (to do: default to None and set with symbols)
    self.initial = None  # a list of strings, listed for each dimension
    self.solution = None

  def addConstraints(self, constraints):
    """ Add constraints from various sources, distinguished by type.
      >>> p = Puzzle()
      >>> p.addConstraints({'size': [2, 2], 'initial': ['12', '21']})
      >>> str(p)
      '[ 12\\n  21 ]'
      >>> p.addConstraints(['Unknown'])
      Traceback (most recent call last):
      ...
      Exception: Can't find a constraint named Unknown
    """
    if constraints is None:
      return
    # print("Loading constraints:", constraints)
    if isinstance(constraints, io.IOBase):
      self.addConstraints(yaml.safe_load(constraints))
    elif isinstance(constraints, list):
      for constraint in constraints:
        self.addConstraints(constraint)
    elif isinstance(constraints, str):
      self.addConstraintNamed(constraints)
    elif isinstance(constraints, dict):
      if 'name' in constraints:
        # Dictionary of constraint constructor properties + a class name
        self.addConstraintNamed(constraints['name'], constraints)
      else:
        # Absorb all named Puzzle properties we recognize.
        self.setDimensions(constraints.get('dimensions', None))
        self.setSize(constraints.get('size', None))
        self.setInitial(constraints.get('initial', None))
        self.addConstraints(constraints.get('constraints', None))
    else:
      click.print("Warning: Unrecognized item", constraints)

  def addConstraintNamed(self, c, new_args={}):
    """ Adds a constraint with the given name, if we know it.
        Pass the specified arguments to its constructor.
        Otherwise, if it's the name of a file in theh current directory,
        optionally with the suffix ".yml" or ".yaml", load constraints from that file.
        Otherwise, raise an exception.
    """
    print("loading constraint", c)
    for extension in ['', '.yml', '.yaml']:
      if self.tryLoad(c + extension):
        return
    try:
      self.constraints.append(globals()[c](**new_args))
    except:
      raise Exception("Can't find a constraint named " + c)

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
      [ 12
        34 ]
    """
    result = ''
    if self.initial:
      result = self.formatPlacements(self.initial)
    elif self.size:
      result = self.formatSize(self.size)
    elif self.dimensions:
      result = '(' + str(self.dimensions) + "-dimensional)"
    if self.constraints:
      result = concatWithSep([result, '[' + ', '.join([str(c) for c in self.constraints]) + ']'], "\n")
    if result == '':
      result = "(empty Puzzle)"
    return result

  def formatSize(self, size):
    return '(' + functools.reduce(lambda a, b: a + 'x' + b, map(str, self.size)) + ")"

  def formatPlacements(self, p):
    """ Returns the placement set p, formatted as a string. 
        Requires that dimensions are already set.
    """
    if self.dimensions <= 2:
      if self.symbolsAreChars:
        lines = [''.join(row) for row in p]
      else:
        lines = p
      return '[ ' + "\n  ".join(lines) + ' ]'
    else:
      return self.formatSize(self.size)  # punt for now

  def setDimensions(self, dimensions):
    if dimensions:
      if self.dimensions:
        if self.dimensions != dimensions:
          raise Exception("Conflicting dimensions: " + self.dimensions + " vs. " + dimensions)
      else:
        self.dimensions = dimensions

  def setSize(self, size):
    if size:
      if self.size:
        if self.size != size:
          raise Exception("Conflicting sizes: " + self.size + " vs. " + size)
      else:
        self.setDimensions(len(size))
        self.size = size

  def setInitial(self, initial):
    """ Sets the initial contents of the grid.
        Raises if the dimensions or size are already set and don't match; otherwise sets them.
        Handles multiple formats:
          >>> p = Puzzle()
          >>> p.setInitial(['12', '21'])  # array of strings, one per row, with one char per column
          >>> print(p)
          [ 12
            21 ]
          >>> p.setInitial(" 12 \\n 34")  # a single string, with rows separated by newlines
          >>> print(p)
          [ 12
            34 ]
    """
    if initial is None:
      pass
    elif isinstance(initial, str):
      # A single string: split into lines and treat it recursively.
      self.setInitial(initial.splitlines())
    elif isinstance(initial, list):
      if isinstance(initial[0], str):
        # It's a single array of one or more strings.
        if self.dimensions == 1:
          # We already know it has only one dimension, so the strings must be individual symbols (unusual but legal).
          self.setSize(len(initial))
          self.initial = initial
        elif self.dimensions == 2 or self.dimensions is None:
          # It's two-dimensional, so the strings must each be a row of single-character symbols (more common).
          # (Or we don't know it's two-dimensional yet, but that's the more plausible interpretation.)
          self.setSize([len(initial), max([len(x.strip()) for x in initial])]);
          self.initial = [list(x.strip()) for x in initial]
        else:
          raise Exception("Can't initialize " + str(self.dimensions) + "-dimensional puzzle with " + str(initial));
      elif isinstance(initial[0], list):
        # It's an array of arrays.
        # If no dimensions have been supplied, assume single-character symbols glommed into strings.
        pass  # to do
      else:
        raise Exception("Can't initialize with list " + str(initial))
    else:
      raise Exception("Can't initialize with " + str(initial))

  def reduceConstraints(self):
    """ Apply all constraints.
        Remove all the finished ones.
        Return true if something changed - if there are a different set of constraints
        as a result of the reduction.
    """
    return False

  def solve(self):
    """ Attempt to find a solution to the initial condition and constraints.
        If one can be found, return True and put its position in self.solution.
        If not, return False.
    """
    while self.reduceConstraints():
      pass