#!/usr/bin/env python
"""Convert a directory of JSON files into a SQLite DB."""
import sqlite3
import json
import os
from progressbar import ProgressBar, Bar, Percentage, ETA
import sys

TYPE_MAPPING = dict(string='text', integer='int', float='real', boolean='boolean')

def create_table(table_name, fields):
  """Generates a SQLite CREATE TABLE statement from the given table name and fields dict."""
  output = ['CREATE TABLE %s (' % table_name]
  primaries = []
  for field, dtype in fields.items():
    output.append('  %s %s,' % (field, TYPE_MAPPING[dtype[0]]))
    if dtype[1]:
      primaries.append(field)
  output.append('  CONSTRAINT %s_pk PRIMARY KEY (%s)' % (table_name, ','.join(primaries)))
  output.append(')')
  return '\n'.join(output)

def main(argv):
  if len(argv) != 4:
    print "Incorrect number of arguments specified. Expected 3, but got %s" % (len(argv) - 1)
    print "USAGE: %s JSON_DIR SCHEMA_FILE SQLITE_DB" % argv[0]
    sys.exit(1)
  json_dir = argv[1]
  schema_file = argv[2]
  sqlite_db = argv[3]
  if not os.path.isdir(json_dir):
    sys.stderr.write('The given JSON dir doesn\'t exist!\n')
    sys.exit(1)
  if not os.path.isfile(schema_file):
    sys.stderr.write('The given schema file doesn\'t exist!\n')
    sys.exit(1)
  schema = None
  with open(schema_file) as s:
    schema = json.load(s)
  if not schema:
    sys.stderr.write('Unable to load the given schema file!\n')
    sys.exit(1)
  if os.path.exists(sqlite_db):
    os.unlink(sqlite_db)
  conn = sqlite3.connect(sqlite_db)
  cursor = conn.cursor()
  table_num = 0
  pbar = ProgressBar(widgets=['Sqlizing... ', Bar(), ' ', Percentage(), ' ', ETA()], maxval=len(schema.keys())).start()
  for table_name, fields in schema.items():
    cursor.execute(create_table(table_name, fields))
    table = None
    with open(os.path.join(json_dir, '%s.json' % table_name)) as f:
      table = json.load(f)
    if not table:
      sys.stderr.write('ERROR: Unable to load table %s\n' % table_name)
      sys.exit(1)
    data = []
    for row in table['data']:
      data_row = []
      for column in table['columns']:
        data_row.append(row.get(column, None))
      data.append(tuple(data_row))
    insert = 'INSERT INTO %s (%s) VALUES (%s)' % (table_name, ','.join(table['columns']),
                                                  ','.join('?' * len(table['columns'])))
    cursor.executemany(insert, data)
    conn.commit()
    table_num += 1
    pbar.update(table_num)
  pbar.finish()
  conn.commit()
  conn.close()

if __name__ == '__main__':
  main(sys.argv)
