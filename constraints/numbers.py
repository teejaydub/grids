from .constraint import Constraint

class SymbolsNumericDigits(Constraint):
	""" Sets the symbol set to the numeric digits, 1-9,
			or to the given maximum digit value.
	"""
	def __init__(self, max_digits=9):
		self.max_digits = max_digits

	def apply(self, puzzle):
		puzzle.symbols = ['1', '2']

class SymbolsNumericByDiameter(Constraint):
	def apply(self, puzzle):
		if puzzle.size:
			return []
		else:
			# We can finish whenever the size is known.
			return [self]