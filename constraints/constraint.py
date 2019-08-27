import logging

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

  def __str__(self):
    return self.__class__.__name__

  def showSymbols(self, symbols):
    """ Formats a list of symbols, returning a string.
        It's here just because it's a convenient place to standardize it.
    """
    return '(' + ' '.join([s for s in symbols]) + ')'

  def apply(self, puzzle):
    """ Apply this constraint to the given puzzle.
        Return a list of the constraints that should now replace this one.
        If this constraint is unfinished, include it in the return list;
        otherwise, don't.
        Also include any additional constraints created by applying.

        Default behavior is to throw away this constraint, for one-time-use constraints.

        If you have any techniques() defined, applies those and keeps this constraint,
        unless a technique returns a list, then returns that.
    """
    # Wait until we've initialized the solution and symbol set.
    if self.techniques():
      if puzzle.solution and puzzle.symbols:
        # Apply all the techniques, stopping when one has results.
        for technique in self.techniques():
          result = technique(puzzle)
          if result is not None:
            return result
      # If nothing produced new constraints, keep this one.
      return [self]
    else:
      # No techniques, so just eliminate this constraint.
      return []

  def techniques(self):
    """ Return a list of functions to be called, in order,
        when the puzzle has a solution and symbols.
        Override this in derived classes to append more techniques.
    """
    return []
