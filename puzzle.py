import yaml

class Puzzle:
	def __init__(self):
		self.constraints = {}

	def loadConstraints(self, f):
		""" Add constraints to the puzzle from a YAML constraints file. 
				The file must be open.
		"""
		self.constraints = yaml.load(f)

	def __str__(self):
		return str(self.constraints)
