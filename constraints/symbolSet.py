""" Standardize working with a set of symbols,
    using a Python set of strings, one per symbol.

    Also includes a class for a list of symbols, that can have repeats.
"""

import itertools

class SymbolList(list):
  def __str__(self):
    return '(' + ' '.join(sorted(self)) + ')'

class SymbolSet(set):
  def __str__(self):
    return SymbolList(self).__str__()

  def value(self):
    """ Returns an arbitrarily-chosen value from the set.
        Primiarily useful if the set is already known to contain only one value.
    """
    return next(itertools.islice(self, 1))