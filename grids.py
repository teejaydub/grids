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
@click.option('-q', '--quiet', 'loglevel', flag_value=logging.ERROR, help="Minimal output")
@click.option('--normal-output', 'loglevel', flag_value=logging.WARNING, help="Normal output", default=True)
@click.option('-v', '--verbose', 'loglevel', flag_value=logging.INFO, help="More output")
@click.option('-d', '--debug', 'loglevel', flag_value=logging.DEBUG, help="Debugging output")
def solve(input, loglevel):
  """ Solve a puzzle specified by one or more INPUT constraints files. """
  logging.basicConfig(format='%(message)s', level=loglevel)

  p = puzzle.Puzzle()
  for i in input:
    p.addConstraints(i)
  logging.info("Puzzle:")
  logging.info(p)
  logging.info("\nSolving...")
  if p.solve():
    logging.info("")  # separator
    click.echo("Solved:")
    click.echo(str(p.solution))
  else:
    logging.info("")  # separator
    click.echo("Can't solve.")
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
  assert """Solved:
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

  result = runner.invoke(cli, ['solve', 'su-test-2.yml'])
  assert result.exit_code == 0
  assert """Solved:
[ 1 4 2 6 9 3 5 8 7
  9 6 8 1 7 5 2 4 3
  7 3 5 4 2 8 6 1 9
  4 7 9 2 6 1 8 3 5
  5 1 6 3 8 4 9 7 2
  8 2 3 9 5 7 1 6 4
  2 9 4 7 1 6 3 5 8
  6 5 7 8 3 2 4 9 1
  3 8 1 5 4 9 7 2 6 ]
""" in result.output

if __name__ == "__main__":
  cli()
