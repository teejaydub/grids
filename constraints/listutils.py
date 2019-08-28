
def subtractLists(alist, blist):
  """ Return list a with all elements that match an element in b removed.
      >>> subtractLists([1, 2, 3], [3])
      [1, 2]
      >>> subtractLists(['1', '2', '3'], ['1'])
      ['2', '3']
      >>> subtractLists([[0, 0], [0, 1]], [[0, 0]])
      [[0, 1]]
  """
  return [a for a in alist if not a in blist]
  # return filter(alist, lambda a: a not in blist)

def subtractListsUnique(alist, blist):
  """ Return list a with all elements that match an element in b removed.
      But if there are duplicates, only treats each pair once.
      That is, one instance of 2 in blist removes one instance of 2 in alist.

      >>> subtractLists([1, 2, 2, 3], [2])
      [1, 2, 3]
      >>> subtractLists(['1', '2', '3'], ['1'])
      ['2', '3']
      >>> subtractLists([[0, 0], [0, 0], [0, 1]], [[0, 0]])
      [[0, 0], [0, 1]]
  """
  blist = list(blist[:])  # copy so as not to modify original
  for a in alist:
    if a in blist:
      blist.remove(a)
    else:
      yield a
