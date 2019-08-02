import io
import pathlib
import yaml

class Puzzle:
	def __init__(self):
		self.constraints = {}

	def addConstraints(self, constraints):
		""" Add constraints from various sources, distinguished by type.
		"""
		if isinstance(constraints, io.IOBase):
			self.addConstraints(yaml.safe_load(constraints))
		elif isinstance(constraints, list):
			for constraint in constraints:
				self.addConstraints(constraint)
		elif isinstance(constraints, str):
			self.addConstraintNamed(constraints)
		else:
			# Absorb all named properties we recognize.
			pass

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
		return str(self.constraints)
