# Command-line intrface for solving grid-based puzzles.

import click
import yaml

@click.group()
def cli():
  # import argparse

#   parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
#                                    description='Solve grid-based puzzles.',
#                                    epilog="""
# Example constraint file for Sudoku:

# 	- Sudoku  # includes constraints from Sudoku.yaml
# 	- initial: |
# 	  1****6***
# 	  *********
# 	  ****7****
# 	  ********3
# 	  *********
# 	  **8******
# 	  *********
# 	  ******5**
# 	  *********

# See README.md for full documentation.
# """)
#   parser.add_argument('input', nargs='*',
#                       help="""A YAML file containing constraints that define the puzzle to solve.  Assumes .yaml.""")
#   parser.add_argument('--test', action='store_true', help='Run unit tests (only).')

#   args = parser.parse_args()
	pass

@cli.command()
def solve():
	click.echo("Solving...")

if __name__ == "__main__":
  cli()
