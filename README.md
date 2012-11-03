dump-parser
===========

A set of tools to deal with the JSON file produced by the dump extractor.

The following tools are provided:

`split_tables.py`:
  Splits the monolithic JSON dump into a separate file per database table. The rest of the tools depend on this tool having already been run.

`merge_ccp_yaml.py`:
  Given a directory of JSON files produced by `split_tables.py`, and the YAML files from CCP, this tool merges the two sources of data, writing the result to the JSON files directly.

`schema_converter.py`:
  Convert the MS SQL CREATE TABLE script to a JSON schema. This is used by `sqlize.py` and `bigqueryize.py`.

`csvize.py`:
  Converts the specified JSON file into a CSV file, using the 'excel' format.

`sqlize.py`:
  Convert a directory of JSON files into a SQLite DB.

`bigqueryize.py`:
  Upload a directory of JSON files to Google BigQuery.
