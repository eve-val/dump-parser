#!/usr/bin/env python
import csv
import sys
import json

if __name__ == '__main__':
  if len(sys.argv) != 2:
    print 'wrong args'
    sys.exit(1)
  contents = None
  with open('%s.json' % sys.argv[1], 'rb') as f:
    contents = json.load(f)
  if not contents:
    print 'Unable to parse json'
    sys.exit(1)
  with open('%s.csv' % sys.argv[1], 'wb') as f:
    dw = csv.DictWriter(f, contents['columns'])
    dw.writeheader()
    dw.writerows(contents['data'])
