#!/usr/bin/env python
"""Merge the CCP-provided YAML files with the JSON produced via the dump extractor."""
import os
import sys
import yaml
import json


def main(argv):
  if len(argv) < 3 or not os.path.isdir(argv[1]):
    print 'Must specify a directory of JSON files, and a directory with CCP\'s YAML files.\nUsage: %s JSON_DIR CCP_DIR\n' % (sys.argv[0])
    sys.exit(1)
  json_dir = argv[1]
  ccp_dir = argv[2]
  # First, convert the new table
  print "creating graphics table"
  with open(os.path.join(ccp_dir, 'graphicIDs.yaml')) as f:
    gids = yaml.safe_load(f)
    new_table = dict(table_name='eveGraphics',
                     columns=['graphicID', 'graphicFile', 'description', 'obsolete', 'graphicType', 'collidable', 'explosionID', 'directoryID', 'graphicName'],
                     data=[])
    for gid in gids.keys():
      new_table['data'].append(dict(graphicID=int(gid), **gids[gid]))
    with open(os.path.join(json_dir, 'eveGraphics.json'), 'w') as of:
      json.dump(new_table, of)
    del gids

  # Then merge the easy table:
  print "merging icons"
  origIcons = None
  with open(os.path.join(json_dir, 'eveIcons.json')) as f:
    origIcons = json.load(f)
  with open(os.path.join(ccp_dir, 'iconIDs.yaml')) as f:
    iids = yaml.safe_load(f)
    new_ids = set((int(i) for i in iids.keys()))
    old_ids = set((int(i['iconID']) for i in origIcons['data']))
    ids_to_add = new_ids - old_ids
    for iid in ids_to_add:
      origIcons['data'].append(dict(iconID=int(iid), **iids[iid]))
    with open(os.path.join(json_dir, 'eveIcons.json'), 'w') as of:
      json.dump(origIcons, of)
  del origIcons
  # Then merge the hard table:
  print "merging types"
  origTypes = None
  _type_cache = dict()

  def getType(tid):
    if tid not in _type_cache:
      for row in origTypes['data']:
        if row['typeID'] == tid:
          _type_cache[tid] = row
          break
      else:
        _type_cache[tid] = dict(typeID=tid)
        origTypes['data'].append(_type_cache[tid])
    return _type_cache[tid]

  with open(os.path.join(json_dir, 'invTypes.json')) as f:
    origTypes = json.load(f)
  with open(os.path.join(ccp_dir, 'typeIDs.yaml')) as f:
    tids = yaml.safe_load(f)
    for tid in tids.keys():
      row = getType(tid)
      trow = tids[tid]
      row.update(trow)
    with open(os.path.join(json_dir, 'invTypes.json'), 'w') as of:
      json.dump(origTypes, of)

if __name__ == '__main__':
  main(sys.argv)
