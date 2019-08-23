#!/usr/bin/env python
# Command-line intrface for solving grid-based puzzles.

import click
import logging
import puzzle

@click.group()

def cli():
  """ Analyze grid-based puzzles. """
  pass

@cli.command()
@click.argument('input', type=click.File('rb'), nargs=-1)
@click.option('-v/-q', '--verbose/--quiet', 'verbose', help="More output")
@click.option('-d', '--debug', 'debug', is_flag=True, help="Debugging output")
def solve(input, verbose, debug):
  """ Solve a puzzle specified by one or more INPUT constraints files. """
  if debug:
    logging.basicConfig(level=logging.DEBUG)
  elif verbose:
    logging.basicConfig(level=logging.INFO)

  p = puzzle.Puzzle()
  for i in input:
    p.addConstraints(i)
  if verbose or debug:
    click.echo("Puzzle:")
    click.echo(p)
    click.echo("\nSolving...")
  if p.solve():
    click.echo("\nSolved:")
    click.echo(str(p.solution))
  else:
    click.echo("\nCan't solve.")
    if p.solution:
      click.echo("Best solution:")
      click.echo(p.solution)

@cli.command()
@click.option('-v/-q', '--verbose/--quiet', 'verbose')
def test(verbose):
  """ Run regression tests. """

  # Using docstrings:
  import doctest
  import placements
  from constraints import region, permutations
  doctest.testmod(verbose=verbose)
  doctest.testmod(puzzle, verbose=verbose)
  doctest.testmod(region, verbose=verbose)
  doctest.testmod(placements, verbose=verbose)
  doctest.testmod(permutations, verbose=verbose)

  # Test command-line interface and solving:
  from click.testing import CliRunner
  runner = CliRunner()

  result = runner.invoke(cli, ['solve', 'su-test-1.yml'])
  assert result.exit_code == 0
  assert 'Solved' in result.output
  assert """
Solved:
[ 9 5 3 4 1 2 6 7 8
  4 1 8 5 6 7 2 3 9
  7 2 6 3 9 8 1 4 5
  6 8 4 1 2 5 7 9 3
  5 7 1 8 3 9 4 6 2
  3 9 2 6 7 4 5 8 1
  1 4 5 9 8 6 3 2 7
  2 6 9 7 5 3 8 1 4
  8 3 7 2 4 1 9 5 6 ]
""" in result.output

if __name__ == "__main__":
  cli()
