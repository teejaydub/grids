# Grids

This is a Python library and command-line utility for solving grid puzzles.
Examples include Sudoku, Ken Ken, and magic squares, but the principles are
general and generalizable.

My motivation for this is not necessarily to use it to solve puzzles per se;
it's that usually when I write code to solve a problem, I gain a much better
understanding of how to solve the problem without code.  Plus, it's fun!

## Concepts

The input is an initial state called a **puzzle**, consisting of:

* a **rectangular grid** with given dimensions
* a set of **possible symbols** that can be placed in grid squares
* a set of **constraints** about how symbols must be placed in squares
* a set of **starting placements**, assignments of symbols to squares.  
  Starting placements are represented as a kind of constraint.

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

## Solving process

To solve a grid puzzle:

1. Each grid square gets every possible symbol placed into it, tentatively.
2. Constraints are applied to eliminate symbols from squares where possible.
3. Constraints are combined with placements to produce additional constraints.
4. The preceding two steps are repeated until no new data is produced.
5. A search tree is explored, choosing one placement for a given square and 
   recursing the constraint proecss.  Tree nodes are eliminated if they 
   result in empty placement lists for any square.

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
* The **current constraint set**.  The initial constraints may be analyzable
	to derive further constraints.
* The **search tree** of puzzle state nodes that are being explored under
	this one.  These are stored as a map from a `Placement` to a resulting 
	`GridPuzzle`.

All constraints are child classes of the `Constraint` class.  Constraints have
the following key methods:

`Region`
: Returns a list of `Location`s defining the region that this constraint 
applies to.

`EliminatePlacements`
: Applies this constraint's definition to remove symbols from grid squares,
	anywhere in the grid where this constraint applies.

`GenerateConstraints`
: Looks at the current list of constraints and placements, and returns 
	additional constraints that can be inferred.


## Heuristic choices

Search tree generation is done in increasing order of the number of possible
placements per square, e.g.,  the entire tree (all leaf nodes) is expanded for
each square with two possible placements, then the entire tree is expanded for
each square with three possible placements, etc.  This is intended to keep the
tree as small as possible.

## Constraint types

...
