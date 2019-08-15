# Grids

This is a Python library and command-line utility for solving grid puzzles.
Examples include Sudoku, KenKen, and magic squares, but the principles are
general and generalizable.

My motivation for this is not necessarily to use it to solve puzzles per se;
it's that usually when I write code to solve a problem, I gain a much better
understanding of how to solve the problem without code.  Plus, it's fun!

## Current status

Still under initial development.  Doesn't do anything useful yet.

## Concepts

The input is an initial state called a **puzzle**, consisting of:

* a **rectangular grid** with given dimensions
* a set of **possible symbols** that can be placed in grid squares
* a set of **constraints** about how symbols must be placed in squares
* a set of **initial placements**, assignments of symbols to squares.  
  Initial placements can be represented as a kind of constraint.

The goal is to enumerate the possible **solutions** to the initial state; a
solution is an assignment of one symbol to each square of the grid that
satisfies all the constaints.

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

When run at the command line, the program takes a puzzle, solves it, and
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
	`.yml` implied) or a map of `GridPuzzle` attributes.
* If the top-level content is a map, it's a map of `GridPuzzle` attributes.
* In particular, the `constraints` key contains a list of constraints, each of
	which names an available Python class that's derived from `Constraint`.
	If a constraint has a map value, it must have a `name` along with other 
	arguments, which are passed to the constraint constructor.

Example:

```YAML
- Sudoku  # includes constraints from Sudoku.yml
- initial: |
	  1****6***
	  *********
	  ****7****
	  ********3
	  *********
	  **8******
	  *********
	  ******5**
	  *********
```

```YAML
# Sudoku.yml
size: [9, 9]
contraints:
	- SymbolsNumericByDiameter
	- EachDimensionIsCompletePermutation
	- name: RegionsAreCompletePermutation
		regions: [
			[a0-c2], [a3-c5], [a6-c8],
			[d0-f2], [d3-f5], [d6-f8],
			[g0-i2], [g3-i5], [g6-i8]
		]
```

These are complete definitions of the Sudoku class of puzzles and an
individual puzzle.

Some simple rules make it easier to write constraint files for a new puzzle:

* Specifying the grid size implies its number of dimensions.  You can also
	specify dimensions without specifying size.  This allows a puzzle class
	to specify rules for puzzles of varying sizes.
* As shown above, lists of grid squares can be expressed in letter-number
	form for two-dimensional grids.  They can also contain ranges of squares,
	expressed as *start square*-*end square*, which are taken to be rectangular
	in shape and iterate rows and columns through the region listed.  E.g.,
	"a0-c2" means "a0, a1, a2, b0, b1, b2, c0, c1, c2".

### Arguments

Command-line arguments are listed in the `--help` text.  They include
specifying one of the following actions:

* Solve the puzzle completely, and output all solutions

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

A `Location` is a tuple of coordinates, indexed from 0.  For two-dimensional
grids, the order is row-major, so the first coordinate is the row, and the
second is the column.

A `Placement` is a pair of a `Location` with a symbol.

A `GridPuzzle` class instance holds all the pieces of the initial state, as
well as the following additional data while the puzzle is being solved:

* The **current placements** of symbols in the grid, as an array of rows,
	each of which is an array of columns, each of which is an array of symbols
	that are known to be possible for the corresponding grid square.
	This represents the symbols placements that are currently known to be 
	inferrable from the puzzle's initial state.  Squares with multiple symbols
	listed can have multiple placements (at the current stage of analysis).
	These correspond to "pencil marks" in traditional solving techniques.
	Squares with `*` could have any possible symbol.
* The **current constraint set**.  The initial constraints may be analyzable
	to derive further constraints.
* The **search tree** of puzzle state nodes that are being explored under
	this one.  These are stored as a map from a `Placement` to a resulting 
	`GridPuzzle`.

All constraints are child classes of the `Constraint` class.  Constraints have
the following key methods:

`ModifyPuzzle` - Modify aspects of the puzzle, like the size or symbol set.

`GenerateConstraints(gridPuzzle)` - Look at the current list of constraints
and placements, and return a tuple of the additional constraints that can be
inferred, and constraints that can be deleted.

`EliminatePlacements(gridPuzzle)` - Remove symbols from grid squares as
possible.


## Heuristic choices

Search tree generation is done in increasing order of the number of possible
placements per square, e.g.,  the entire tree (all leaf nodes) is expanded for
each square with two possible placements, then the entire tree is expanded for
each square with three possible placements, etc.  This is intended to keep the
tree as small as possible.

## Constraint classes

### SymbolsNumericByDiameter

When the size of the puzzle is known, sets the symbol set to the numbers from
1 to the diameter.  The diameter is the size in  any dimension, but if any
dimensions have different sizes, raise an exception.

### EachDimensionIsCompletePermutation

Creates a `RegionsAreCompletePermutation` constraint, with a region list
consisting of each row and each column, up to the number of dimensions.

### RegionConstraint

Constructor arguments:

* `regions` - A list of grid squares that this constraint applies to.  Can be
	parsed from the YAML input styles described above.

#### RegionsAreCompletePermutation

A `RegionConstraint`.

Each region listed must contain exactly one of each symbol in the symbol set.
An exception is raised if any region is not the same size as the symbol set.

### MathOpConstraint

A `RegionConstraint`.

Constructor arguments:

* `operator` - A function applied to the numeric values of all symbols in the region.
* `target` - A numeric value that the operator must return.

Specializations include `SumIs`, `DifferenceIs`, `ProductIs`, and
`QuotientIs`. These are useful because they can follow custom search rules -
e.g., `ProductIs` can do a prime factorization, `SumIs` can use min/max
analysis, etc.
