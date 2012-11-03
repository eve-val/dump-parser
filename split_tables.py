#!/usr/bin/env python
"""Splits the monolithic dump JSON file into a file per table."""
import StringIO
import gc
import os
import sys
import json


def main(argv):
  if len(argv) < 3:
    print 'Must specify both a JSON dump file and a directory.'
    print 'Usage: %s MONOLITHIC_JSON OUTPUT_DIRECTORY\n' % sys.argv[0]
    sys.exit(1)
  target_dir = argv[2]
  json_file = argv[1]
  if not os.path.isfile(json_file) or not os.access(json_file, os.R_OK):
    print 'File %s does not exist or is not readable.' % json_file
    print 'Usage: %s MONOLITHIC_JSON OUTPUT_DIRECTORY\n' % sys.argv[0]
    sys.exit(1)
  if not os.path.isdir(target_dir):
    print 'Directory %s does not exist, creating.' % target_dir
    os.mkdir(target_dir)
  with open(json_file) as yf:
    current_table = None
    line_num = 0
    table_name = None
    for line in yf:
      line_num += 1
      if line == '---\r\n':
        current_table = StringIO.StringIO()
        continue
      elif line == '...\r\n':
        table = json.loads(current_table.getvalue())
        table_name = table['table_name']
        print table_name
        with open(os.path.join(target_dir, '%s.json' % table_name), 'w') as tf:
          tf.write(current_table.getvalue())
        current_table.close()
        del table
        table_name = None
        gc.collect()
        continue
      else:
        current_table.write('%s\n' % line[:-2])


if __name__ == '__main__':
  main(sys.argv)
