import functools
import itertools
import math

from .listutils import subtractListsUnique

def sumF(x, y):
  return x + y
def productF(x, y):
  return x * y
def differenceF(x, y):
  return x - y
def quotientF(x, y):
  return x / y

def hashInts(ints):
  """ Return a hashable that uniquely represents a list of integers.
      >>> hashInts([1, 2, 5])
      '1_2_5'
      >>> hashInts([2])
      '2'
  """
  return '_'.join([str(x) for x in ints])

def factorizations(n, m):
  """ Yield each combination of ways to multiply m integers to make n.
      >>> list(factorizations(1, 1))
      [[1]]
      >>> list(factorizations(2, 1))
      [[2]]
      >>> list(factorizations(2, 2))
      [[1, 2]]
      >>> list(factorizations(4, 2))
      [[1, 4], [2, 2]]
      >>> list(factorizations(50, 3))
      [[1, 1, 50], [1, 2, 25], [1, 5, 10], [2, 5, 5]]
  """
  if n == 1:
    yield m * [1]
  elif m == 1:
    yield [n]

  # Pull off every even factor we can.
  else:
    # Filter out repeats.
    seen = set()
    for i in range(1, n + 1):
      if n % i == 0:
        remainder = n // i
        for rest in factorizations(remainder, m - 1):
          combo = sorted([i] + rest)
          # Yield combo, but only if we haven't yet.
          h = hashInts(combo)
          if h not in seen:
            seen.add(h)
            yield combo
