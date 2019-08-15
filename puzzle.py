import functools
import io
import pathlib
import yaml

def concatWithSep(elements, sep = ','):
	return sep.join(x for x in elements if x)

class Puzzle:
	""" Holds a set of initial conditions and constriants. 
	"""
	def __init__(self):
		self.constraints = {}
		self.dimensions = None
		self.size = None
		self.initial = None

	def addConstraints(self, constraints):
		""" Add constraints from various sources, distinguished by type.
		"""
		if constraints is None:
			return
		if isinstance(constraints, io.IOBase):
			self.addConstraints(yaml.safe_load(constraints))
		elif isinstance(constraints, list):
			for constraint in constraints:
				self.addConstraints(constraint)
		elif isinstance(constraints, str):
			self.addConstraintNamed(constraints)
		elif self.isKnownConstraint(constraints.get('name', None)):
			# Dictionary of constraint constructor properties + a class name
			self.addConstraintNamed(constraints['name'], constraints)
		else:
			# Absorb all named properties we recognize.
			self.setDimensions(constraints.get('dimensions', None))
			self.setSize(constraints.get('size', None))
			self.setInitial(constraints.get('initial', None))
			self.addConstraints(constraints.get('constraints', None))

	def addConstraintNamed(self, c):
		""" Adds a constraint with the given name, if we know it.
				Otherwise, if it's the name of a file in theh current directory,
				optionally with the suffix ".yml" or ".yaml", load constraints from that file.
				Otherwise, raise an exception.
		"""

		for extension in ['', '.yml', '.yaml']:
			if self.tryLoad(c + extension):
				return
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
		"""
		result = ''
		if self.initial:
			result = self.formatPlacements(self.initial)
		elif self.size:
			result = '(' + functools.reduce(lambda a, b: a + 'x' + b, map(str, self.size)) + ")"
		elif self.dimensions:
			result = '(' + str(self.dimensions) + "-dimensional)"
		if self.constraints:
			result = concatWithSep([result, str(self.constraints)], "\n")
		if result == '':
			result = "(empty Puzzle)"
		return result

	def setDimensions(self, dimensions):
		if self.dimensions and dimensions:
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
		pass

	def isKnownConstraint(self, constraintName):
		return False
