#!/usr/bin/env python
"""Parses a MS SQL Server script that contains CREATE TABLE statements, and converts it to JSON."""
import json
import os
import re
import StringIO
import sys

# This matches individual column defs to ensure that we throw an error on an unkown SQL type.
LINE_REGEX = re.compile(r'^\s+(\w+)\s+.*(text|char|int|float|real|money|datetime|bit).*,')

# Maps SQL types to schema types. If the SQL type is not present, 'string' is assumed.
SCHEMA_TYPE = dict(int='integer', float='float', real='float', bit='boolean')

# This parser uses an adaptation of Rob Pike's framework for writing lexers, which will be explained inline.

class Lexer(object):
  """Provides a way to iterate over input with possible backup and errors."""
  def __init__(self, inp):
    self._inp = inp[:]
    self._idx = 0
    self.output = dict()
  def __iter__(self):
    """The core of the lexer. Explicitly written to allow the current index to change, for backup purposes."""
    while True:
      l = self.get_one_line()
      if not l:
        return
      yield l
  def backup(self, i):
    """Moves the current index into the input backward by `i` lines."""
    self._idx = self._idx - i
    if self._idx < -1:
      self._idx = -1
  def error(self, msg):
    """Renders an error to stderr, adding information about the current line."""
    sys.stderr.write('Error!!\n')
    sys.stderr.write(msg + '\n')
    sys.stderr.write('At line #%s\n' % (self._idx))
    self.output = []
  def get_one_line(self):
    """Steps the lexer forward one line, returning it."""
    self._idx += 1
    if self._idx > len(self._inp):
      return None
    return '%s\n' % self._inp[self._idx-1]
  def run(self):
    """Actually starts the whole lexer going."""
    state = startState
    while state:
      state = state(self)

##### BEGIN state functions

def constraintState(lexer):
  """Parses the bodies of CONSTRAINT clauses, so we know which columns are primary."""
  lexer.get_one_line()
  for line in lexer:
    if line.startswith(')'):
      lexer.backup(1)
      return startState
    field = re.search(r'\[(\w+)\]', line).group(1)
    lexer.output[lexer.curr_table][field] = 'primary'
  lexer.error('Reached end of file before end of CONSTRAINT clause!\nTable: %s' % lexer.curr_table)
  return None

def createTableState(lexer):
  """Parses CREATE TABLE clauses"""
  line = lexer.get_one_line()
  if not line or not line.startswith('CREATE TABLE'):
    lexer.error('Malformed CREATE TABLE stanza.')
    return None
  table_name = line[20:-3]  # Table names are located at a deterministic position.
  lexer.curr_table = table_name  # TODO(swsnider): Find a less messy way of passing state to the constraint parser.

  # Basically, each CREATE TABLE turns into a dictionary of field->type pairs.
  lexer.output[table_name] = dict()
  for line in lexer:
    if 'CONSTRAINT' in line:
      return constraintState
    line = line.replace('[', '').replace(']', '')  # It's easier to write regexes without having brackets.
    m = LINE_REGEX.match(line)
    if not m:
      # This really only happens if the SQL script has a new kind of database type we've never seen before.
      lexer.error('Could not match the LINE_REGEX to this value!\nSaw line: %s' % line)
      return None
    else:
      lexer.output[table_name][m.group(1)] = SCHEMA_TYPE.get(m.group(2),'string')
  return startState

def startState(lexer):
  """Eats input until it hits CREATE TABLE, then hands off to createTableState"""
  for line in lexer:
    if line.startswith('CREATE TABLE'):
      lexer.backup(1)
      return createTableState
  return None

##### END state functions

def main(argv):
  if len(argv) != 3:
    sys.stderr.write('Incorrect number of arguments.\n')
    sys.stderr.write('USAGE: %s SQL_SCRIPT OUTPUT_FILE\n' % argv[0])
    sys.exit(1)
  sql_script = argv[1]
  output_file = argv[2]
  if not os.path.isfile(sql_script):
    sys.stderr.write('Unable to access file %s\n' % sql_script)
    sys.exit(1)
  inp = None
  with open(sql_script) as sql_file:
    inp = sql_file.read().splitlines()
  lexer = Lexer(inp)
  lexer.run()
  with open(output_file, 'w') as out_file:
    json.dump(lexer.output, out_file, sort_keys=True, indent=2)

if __name__=='__main__':
  main(sys.argv)
