import re

def parseChess(s):
	""" Given a chess-style pair of coordinates like a1,
			return a pair of integer coordinates.
	"""
	(r, c) = re.search("^([a-z])(\d+)$", s).groups()
	r = ord(r) - ord('a')
	c = int(c)
	return (r, c)

class Region():
	def __init__(self, region):
		""" Regions can be specified by a string of two chess-style coordinates separated by a dash,
				or as a list of coordinate pairs.
				E.g.: a1-b2, [(0,0),(0,1),(1,0),(1,1)]
		"""
		if isinstance(region, str):
			# Find the start and end as coordinates.
			(first, last) = region.split('-')
			(startRow, startCol) = parseChess(first)
			(endRow, endCol) = parseChess(last)

			self.squares = []
			for r in range(startRow, endRow + 1):
				for c in range(startCol, endCol + 1):
					self.squares += [(r, c)]
		else:
			self.squares = region

	def __str__(self):
		return str(self.squares)