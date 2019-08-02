#!/usr/bin/env python
# Command-line intrface for solving grid-based puzzles.

import click
import puzzle

@click.group()

def cli():
  """ Analyze grid-based puzzles. """
  pass

@cli.command()
@click.argument('input', type=click.File('rb'), nargs=-1)
@click.option('-v/-q', '--verbose/--quiet', 'verbose')
def solve(input, verbose):
  """ Solve a puzzle specified by one or more INPUT constraints files. """
  p = puzzle.Puzzle()
  for i in input:
    p.addConstraints(i)
  click.echo("Solving...")
  if verbose: click.echo(p)

@cli.command()
@click.option('-v/-q', '--verbose/--quiet', 'verbose')
def test(verbose):
  """ Run regression tests. """
  import doctest
  doctest.testmod(verbose=verbose)
  doctest.testmod(puzzle, verbose=verbose)

if __name__ == "__main__":
  cli()
