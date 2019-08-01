# Command-line intrface for solving grid-based puzzles.

import click
import yaml

@click.group()

def cli():
  """ Analyze grid-based puzzles. """
#   parser.add_argument('input', nargs='*',
#                       help="""A YAML file containing constraints that define the puzzle to solve.  Assumes .yaml.""")
  pass

@cli.command()
@click.argument('input', type=click.File('rb'), nargs=-1)
@click.option('-v/-q', '--verbose/--quiet', 'verbose')
def solve(input, verbose):
  """ Solve a puzzle specified by one or more constraints files. """
  if verbose: click.echo("Loading...")
  for i in input:
    while True:
      chunk = i.read(1024)
      if not chunk:
          break
      if verbose: click.echo(chunk)

  click.echo("Solving...")

@cli.command()
@click.option('-v/-q', '--verbose/--quiet', 'verbose')
def test(verbose):
  """ Run regression tests. """
  import doctest
  doctest.testmod(verbose=verbose)

if __name__ == "__main__":
  cli()
