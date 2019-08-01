# Command-line intrface for solving grid-based puzzles.

import click
import yaml

@click.group()
def cli():
  """ Analyze grid-based puzzles. """
# Example constraint file for Sudoku:

#   - Sudoku  # includes constraints from Sudoku.yaml
#   - initial: |
#     1****6***
#     *********
#     ****7****
#     ********3
#     *********
#     **8******
#     *********
#     ******5**
#     *********
# """)
#   parser.add_argument('input', nargs='*',
#                       help="""A YAML file containing constraints that define the puzzle to solve.  Assumes .yaml.""")
  pass

@cli.command()
def solve():
  """ Solve a puzzle specified by a constraints file. """
  click.echo("Solving...")

@cli.command()
@click.option('-v', '--verbose', is_flag=True)
def test(verbose):
  """ Run regression tests. """
  import doctest
  doctest.testmod(verbose=verbose)

if __name__ == "__main__":
  cli()
