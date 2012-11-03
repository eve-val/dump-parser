dump-parser
===========

A set of tools to deal with the JSON file produced by the dump extractor.

The following tools are provided:

`split_tables.py`:
  Splits the monolithic JSON dump into a separate file per database table. The rest of the tools depend on this tool having already been run.

`merge_ccp_yaml.py`:
  Given a directory of JSON files produced by `split_tables.py`, and the YAML files from CCP, this tool merges the two sources of data, writing the result to the JSON files directly.

`csvize.py`:
  Converts the specified JSON file into a CSV file, using the 'excel' format.

`sqlize.py`:
  Convert a directory of JSON files into a SQLite DB.
