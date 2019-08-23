# Grids

This is a Python library and command-line utility for solving grid puzzles.
Examples include Sudoku, KenKen, and magic squares, but the principles are
general and generalizable.

My motivation for this is not necessarily to use it to solve puzzles per se;
it's that usually when I write code to solve a problem, I gain a much better
understanding of how to solve the problem without code.  Plus, it's fun!

## Current status

Solves easy-level Sudoku with the single "partition" technique.

Next to-dos:

* Better solving
  * Add more solving techniques and test with harder Sudokus
    * More status on solving: number of reduction steps, time
    * Permutation techniques that operate between constraints
    * Associate difficulty levels with techniques, so we can report how hard it was to solve
    * Tree traversal, starting with 2-symbol cells
  * Add Sixy Sudoku puzzle type - should need no further code
  * Add constraint types for KenKen, KaKuRo
* Puzzle creation, with target difficulty
* Code improvements
  * Use logging for verbose output - just remove the prefixes from the format?
  * Have just one argument for logging, and allow additional levels like TRACE.
  * symbolsAreChars: simplify output further?  Simplify input?
  * Better input error handling
    Its own exception type, with more helpful context and suggestions?
* Ease of use
  * Allow interactive prompting for initial if it's not provided (or any other missing parameters?)
  * Assume `.yml` extension for input files - so "grids solve Sudoku" is a complete command line.

## Concepts

The input is an initial state called a **puzzle**, consisting of:

* a **rectangular grid** of **cells** with given dimensions (currently fixed at 2 but could be generalizable in future)
* a set of **possible symbols** that can be placed in grid cells
* a set of **constraints** about how symbols must be placed in cells
* a set of **initial placements**, assignments of symbols to cells.  
  Initial placements can be represented as a kind of constraint.

The goal is to enumerate the possible **solutions** to the initial state; a
solution is an placement of one symbol to each cell of the grid that
satisfies all the constraints.

Traditional grid puzzles are meant to have a unique solution.

### Constraints

Constraints are where much of the conceptual complexity of the framework
resides.  New types of puzzles and new techniques for solving them efficiently
are expressed as new types of constraints.

Constraints can be represented in terms of other constraints that they imply,
so both composition and specialization are used to structure the constraint
set.

See the **Constraint types** section below.

## Command line interface

When run with the "solve" command, the program takes a puzzle, solves it, and
ouptuts the solution(s) to stdout.

Input is via one or more **constraint files**, each of which adds constraints
to the puzzle.

To solve a defined type of puzzle, it's common to use one base set of
constraints common to the puzzle format, followed by a specific set of
constraints that form the starting placements.  For instance, a Sudoku puzzle
would consist of a set of base Sudoku constraints, plus the starting
placements of numbers in the grid.

Constraint files are YAML (or JSON as a subset of YAML) with the following
rules:

* If the top-level content in the file is a list, it's a list of items, each of
  which can be either the name of another constraint file (with the suffix 
  `.yml` implied) or a map of `Puzzle` attributes.
* If the top-level content is a map, it's a map of `Puzzle` attributes.
* In particular, the `constraints` key contains a list of constraints, each of
  which names an available Python class that's derived from `Constraint`.
  If a constraint has a map value, it must have a `name` along with other 
  arguments, which are passed to the constraint constructor.

Example:

```YAML
- Sudoku  # includes constraints from Sudoku.yml
- initial: |
    **3*1****
    4**56*2*9
    7****81**
    *8*1****3
    **18*94**
    3****4*8*
    **59****7
    2*9*53**4
    ****4*9**
```

```YAML
# Sudoku.yml
size: [9, 9]
contraints:
  - SymbolsNumericByDiameter
  - EachDimensionIsCompletePermutation
  - name: RegionsAreCompletePermutation
    regions: [
      a1-c3, a4-c6, a7-c9,
      d1-f3, d4-f6, d7-f9,
      g1-i3, g4-i6, g7-i9
    ]
```

These are complete definitions of the Sudoku class of puzzles and an
individual puzzle.

Some simple rules make it easier to write constraint files for a new puzzle:

* Specifying the grid size implies its number of dimensions.  You can also
  specify dimensions without specifying size.  This allows a puzzle class
  to specify rules for puzzles of varying sizes.
* As shown above, lists of grid squares can contain ranges of chess-style squares,
  expressed as *start square*-*end square*, which are taken to be rectangular
  in shape and iterate rows and columns through the region listed.  E.g.,
  "a1-c3" means "a1, a2, a3, b1, b2, b3, c1, c2, c3".

### Arguments

Command-line arguments are listed in the `--help` text.  They include
specifying one of the following actions:

* Find a single solution for the puzzle, and output it

* Find a single solution for the puzzle, then back up the search tree as far
  as possible while still having only one solution, and output the placement.

Other options include the verbosity of output describing the search process.

## Solving process

To solve a grid puzzle:

1. Each grid square gets the placement `*`, indicating all symbols are possible.
2. Constraints are applied.  They can produce additional constraints or modify
   the puzzle's attributes.
3. The preceding step is repeated until no new changes are produced.
4. A search tree is explored, choosing one placement for a given square and 
   recursing the constraint proecss.  Tree nodes are eliminated if they 
   result in empty placement lists for any square.
5. The searh is stopped either when the grid placement is fully specified
   (a single symbol in each square), or when there are no more leaves in the
   search tree to explore, depending on the command-line arguments.

## Data structures

Symbols are represented as strings.  In puzzles using numbers where
mathematical values are significant, constraints convert the symbol values to
numbers as needed.

A **location** (not defined as a class) is a tuple of coordinates, indexed
from 0.  For two-dimensional grids, the order is row-major, so the first
coordinate is the row, and the second is the column.

A `Region` is a list of locations.

A `Placements` class lists all grid cells in the puzzle and the symbols that
can be placed in each.  Each cell contains a list of possible symbols.  If a
cell contains the single symbol `*`, it can contain any symbol in the puzzle
(convenient in cases where we don't yet know what symbols the puzzle can use).
Otherwise, a cell with one symbol is fully-determined, and a cell with
multiple symbols could have multiple possible symbols at the current stage of
analysis; these correspond to "pencil marks" in traditional solving
techniques.

A `Puzzle` class instance holds all the pieces of the initial state, as well
as the following additional data while the puzzle is being solved:

* The **current solution**, as a `Placements` instance.
* The **current constraint set**.  The initial constraints may be analyzable
  to derive further constraints, which may replace or augment the initial ones.
* The **search tree** of puzzle state nodes that are being explored under
  this one.

All constraints are child classes of the `Constraint` class.  Constraints have
one main method, `apply()`.  This can modify aspects of the puzzle, like the
dimensions or symbol set.  It can also modify the solution.  It returns a list
of constraints to replace itself with; if the return value is a list
containing only itself, it will be kept as is.  If the old constraint is not
within the list of returned constraints, it is removed from the list.

Constraints should not modify themselves during `apply()`; rather, they should
create new constraint instances with modified data and return those.

This method ensures helps in tracking the solving process, knowing when
there's nothing left to be done, and in constructing and managing search
trees.

## Heuristic choices

Brute-force search tree generation is done in increasing order of the number
of possible placements per square, e.g.,  the entire tree (all leaf nodes) is
expanded for each square with two possible placements, then the entire tree is
expanded for each square with three possible placements, etc.  This is
intended to keep the tree as small as possible.

## Constraint classes

The following classes are all derived from `constraints.Constraint`.

To add a new constraint, make sure it's referenced in `constraints/__init__.py`.

### SymbolsNumericByDiameter

When the size of the puzzle is known, sets the symbol set to the numbers from
1 to the diameter.  The diameter is the size in any dimension.  Requires that
the size be equal in all dimensions.

### EachDimensionIsCompletePermutation

Creates a `RegionsAreCompletePermutation` constraint, with a region list
consisting of each row and each column, up to the number of dimensions.

### RegionsAreCompletePermutation

Each region listed must contain exactly one of each symbol in the symbol set.
An exception is raised if any region is not the same size as the symbol set.

### RegionIsCompletePermutation

The same, but including only a single region.

### RegionPermutesSymbols

The same, but with a subset of the puzzle's full symbol set.

This class is where all the solving techniques are implemented for `Region`
constraints; other constraints reduce to this one.

### MathOpConstraint

Constructor arguments:

* `region` that the constraint applies to
* `operator` - A function applied to the numeric values of all symbols in the region.
* `target` - A numeric value that the operator must return.

Specializations include `SumIs`, `DifferenceIs`, `ProductIs`, and
`QuotientIs`. These are useful because they can follow custom search rules -
e.g., `ProductIs` can do a prime factorization, `SumIs` can use min/max
analysis, etc.
