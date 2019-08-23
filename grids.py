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
  if verbose:
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
  import doctest
  import placements
  from constraints import region
  doctest.testmod(verbose=verbose)
  doctest.testmod(puzzle, verbose=verbose)
  doctest.testmod(region, verbose=verbose)
  doctest.testmod(placements, verbose=verbose)

if __name__ == "__main__":
  cli()
