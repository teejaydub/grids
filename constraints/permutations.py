import logging

from .constraint import Constraint
from .region import Region

class RegionPermutesSymbols(Constraint):
	""" The core logic for regions containing each symbol in a set,
			where each symbol appears in exactly one square in the region.
			The region must have the same number of squares as there are symbols in the set.
	"""
	def __init__(self, region, symbols):
		""" Regions are passed using string formats defined in the Region class.
				The symbol set is a list of strings.
		"""
		self.region = Region(region)
		self.symbols = symbols

	def __str__(self):
		return super().__str__() + ': ' + str(self.symbols) + ' in ' + str(self.region)

	def apply(self, puzzle):
		return [self]

# The remaining classes are useful in providing concise shorthands that expand to the above.

class RegionIsCompletePermutation(Constraint):
	""" Creates a RegionPermutesSymbols constraint for all the symbols in the puzzle's symbol set.
	"""
	def __init__(self, region):
		""" The region is passed using string formats defined in the Region class. """
		self.region = region

	def apply(self, puzzle):
		if puzzle.symbols:
			return [RegionPermutesSymbols(self.region, puzzle.symbols)]
		else:
			# Wait until we know the complete symbol set.
			return [self]

class RegionsAreCompletePermutation(Constraint):
	""" Creates a separate region constraint for each region passed in.  
			For concisely expressing standard constraints.
		  The regions are passed as a list of strings, using string formats defined in the Region class.
  """
	def __init__(self, regions):
		self.regions = regions

	def apply(self, puzzle):
		return [RegionIsCompletePermutation(r) for r in self.regions]

class EachDimensionIsCompletePermutation(Constraint):
	""" Creates a RegionsAreCompletePermutation constraint for each row and column.
			Only works up to size 9.
	"""
	def apply(self, puzzle):
		if puzzle.size:
			lastRow = chr(ord('a') + puzzle.size[0] - 1)
			lastCol = chr(ord('1') + puzzle.size[1] - 1)
			# Rows: like "a1-a9", for a..i
			regions = [chr(r) + '1-' + chr(r) + lastCol for r in range(ord('a'), ord(lastRow) + 1)]
			# Cols: like "a1-i1" for 1..9
			regions += ['a' + chr(c) + '-' + lastRow + chr(c) for c in range(ord('1'), ord(lastCol) + 1)]
			return [RegionsAreCompletePermutation(regions)]
		else:
			# Can't resolve without the size, so wait for it to be known.
			return [self]
