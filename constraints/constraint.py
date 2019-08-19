
class Constraint:
	""" Base Constraint class for grid constraints.
			All constraints are derived from this class.

			The basic purpose of a constraint is to be **applied**
			to a puzzle.  This can affect the puzzle's basic attributes,
			its current placement set, or anything else.

			When a constraint is applied, it may be "finished" or not.
			Constraints that are finished can be discarded; their entire
			effect has taken place.  Unfinished constraints may have
			further effects in the future, and should be re-applied later.

			Constraints must allow for data to be available in any order.
			For instance, if a constraint needs to know the size of the
			puzzle, but the size is None, the correct behavior is to 
			do nothing and say it's unfinished, rather than consider
			it an error.
	"""
	def __init__(self, **kwargs):
		pass

	def apply(self, puzzle):
		""" Apply this constraint to the given puzzle.
				Return True if the constraint is now finished,
				False if unfinished.
		"""
		return True

	def __str__(self):
		return self.__class__.__name__