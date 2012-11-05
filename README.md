dump-parser
===========

A set of tools to deal with the JSON file produced by the dump extractor. You will need to run the dump through dos2unix or similar first.

The following tools are provided:

`split_tables`:
  Splits the monolithic JSON dump into a separate file per database table. The rest of the tools depend on this tool having already been run.

`merge_ccp_yaml`:
  Given a directory of JSON files produced by `split_tables.py`, and the YAML files from CCP, this tool merges the two sources of data, writing the result to the JSON files directly.

`schema_converter`:
  Convert the MS SQL CREATE TABLE script to a JSON schema. This is used by `sqlize.py` and `bigqueryize.py`.

`csvize`:
  Converts the specified JSON file into a CSV file, using the 'excel' format.

`sqlize`:
  Convert a directory of JSON files into a SQLite DB.

`bigqueryize`:
  Upload a directory of JSON files to Google BigQuery.
