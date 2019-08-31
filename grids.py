#!/usr/bin/env python
# Command-line intrface for solving grid-based puzzles.

import click
import logging
import os

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
@click.option('-dd', '--debug-to-file', 'debugToFile', flag_value=True, help="Send debugging output to debug.log")
@click.option('-s', '--single-step', 'singleStep', flag_value=True, help="Pause at each step while solving")
def solve(input, loglevel, debugToFile, singleStep):
  """ Solve a puzzle specified by one or more INPUT constraints files. """
  if debugToFile:
    loglevel = logging.DEBUG
    logFileName = 'debug.log'
    if os.path.exists(logFileName):
      os.remove(logFileName)
    logging.basicConfig(format='%(message)s', level=loglevel, filename='debug.log')
  else:
    logging.basicConfig(format='%(message)s', level=loglevel)  # filename='output.txt' for grepping on Windows

  p = puzzle.Puzzle()
  if singleStep:
    p.techniqueCallback = showStep
  for i in input:
    p.addConstraints(i)
  logging.info("Puzzle:")
  logging.info(p)
  logging.info("\nSolving...")

  p.solve();

  # Report stats but not using logging - so it's available to regression tests.
  if loglevel <= logging.INFO:
    click.echo("\nTook %s reduction passes." % p.stats['passes'])
    if 'plies' in p.stats:
      click.echo("After the first %s passes, explored the solution tree to %s plies." 
        % (p.stats['firstPasses'], p.stats['plies']))
    techniques = sorted(p.stats['techniques'].items(), key=lambda kv: -kv[1])
    click.echo("Used these techniques: %s" % ', '.join([t[0] + ' (' + str(t[1]) + 'x)' for t in techniques]))

  logging.info("")  # separator
  if p.isSolved():
    click.echo("Solved:")
    click.echo(str(p.solution))
  else:
    if p.isUnsolvable():
      click.echo("Can't solve because it doesn't appear to be solvable.")
      click.echo("(Error in creation or transcription?  Or my bad?)")
    else:
      click.echo("Can't solve.")
    click.echo("Best solution:")
    click.echo(p)

def showStep(name):
  click.confirm("Continue?", default=True, abort=True)

@cli.command()
@click.option('-v/-q', '--verbose/--quiet', 'verbose')
def test(verbose):
  """ Run regression tests. """

  # Using docstrings:
  import doctest
  import placements
  from constraints import chess, region, permutations, numbers, factoring
  doctest.testmod(verbose=verbose)
  doctest.testmod(chess, verbose=verbose)
  doctest.testmod(numbers, verbose=verbose)
  doctest.testmod(permutations, verbose=verbose)
  doctest.testmod(placements, verbose=verbose)
  doctest.testmod(puzzle, verbose=verbose)
  doctest.testmod(region, verbose=verbose)
  doctest.testmod(factoring, verbose=verbose)

  # Test command-line interface and solving:
  from click.testing import CliRunner
  runner = CliRunner()

  result = runner.invoke(cli, ['solve', 'su-test-1.yml', '-v'])
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
  assert "partition" in result.output
  assert "misfit" in result.output

  result = runner.invoke(cli, ['solve', 'su-test-2.yml', '-v'])
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
  assert "partition" in result.output

  result = runner.invoke(cli, ['solve', 'su-test-3.yml', '-v'])
  assert result.exit_code == 0
  assert """Solved:
[ 2 5 4 1 6 9 3 7 8
  9 7 3 4 2 8 5 6 1
  6 8 1 7 3 5 4 2 9
  8 1 2 6 5 4 9 3 7
  4 3 9 8 1 7 2 5 6
  7 6 5 2 9 3 1 8 4
  3 4 7 9 8 2 6 1 5
  5 9 6 3 7 1 8 4 2
  1 2 8 5 4 6 7 9 3 ]
""" in result.output
  assert "intersection" in result.output
  assert "misfit" in result.output

  result = runner.invoke(cli, ['solve', 'ken-test-1.yml', '-v'])
  assert result.exit_code == 0
  assert """Solved:
[ 4 3 1 2 5
  3 5 2 4 1
  5 1 4 3 2
  2 4 5 1 3
  1 2 3 5 4 ]
""" in result.output
  assert "twoCellOperator" in result.output
  assert "primeFactors" in result.output
  assert "makePermutation" in result.output
  assert "removeKnown" in result.output
  assert "regionOperator" in result.output
  assert "singleValue" in result.output

if __name__ == "__main__":
  cli()
