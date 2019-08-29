""" A constraint that takes a list of symbol sets.
    Separated out here to avoid circular reference.
"""
import itertools
import logging

from .permutations import RegionPermutesSymbols
from .region import RegionSymbolsConstraint
from .symbolSet import SymbolSet, SymbolList

class RegionSymbolLists(RegionSymbolsConstraint):
  """ A RegionSymbolsConstraint that knows several lists of symbols,
      one per cell in the region, that have to be used in some order.
      Like several possible RegionPermutesSymbols, but trickier since symbols can be repeated,
      so you can't infer from the presence of the symbol in one place its absence in another.
      If there is only one symbol list and it doesn't contain duplicates, it's reduced to RegionPermutesSymbols.
  """
  def __init__(self, region, symbolSets):
    super().__init__(region, SymbolSet(itertools.chain.from_iterable(symbolSets)))  # the union of all the sets
    assert symbolSets
    for s in symbolSets:
      assert len(s) == self.region.size()
    self.symbolLists = [SymbolList(s) for s in symbolSets]

  def __str__(self):
    return self.__class__.__name__ + ': one of [' + ', '.join([str(s) for s in self.symbolLists]) + '] in ' + str(self.region)

  def techniques(self):
    return super().techniques() + [self.makePermutation]

  def filterFromPuzzle(self, puzzle):
    """ Overrides base case - must remove from the lists. """
    if puzzle.symbols:
      for slist in self.symbolLists:
        if len(SymbolSet(slist) - puzzle.symbols) > 0:
          # This symbol list has symbols that aren't in the puzzle: remove it.
          new = self.symbolLists.copy()
          new.remove(slist)
          return [RegionSymbolLists(self.region, new)]

  def makePermutation(self, puzzle):
    """ If we get down to a single list, and all symbols are unique,
        and there's one symbol per cell,
        replace this with a RegionPermutesSymbols constraint.
    """
    if len(self.symbolLists) == 1:
      if len(self.symbols) == self.region.size():
        # That implies the symbol lists have unique elements.
        # The symbol set always has the same number of symbols as any symbol list or fewer,
        # and we started with one symbol in each list per cell.
        new = RegionPermutesSymbols(self.region, self.symbols)
        logging.debug("List to permutation: %s is now reduced to %s", self, new)
        puzzle.logTechnique('makePermutation')
        return [new]
