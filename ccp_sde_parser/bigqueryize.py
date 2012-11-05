#!/usr/bin/env python
"""Upload a directory of JSON files into a BigQuery."""
import json
import os
import sys

from progressbar import ProgressBar, Bar, Percentage, ETA
import gflags

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import AccessTokenRefreshError
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run
from apiclient.errors import HttpError
import httplib2

FLAGS = gflags.FLAGS
gflags.DEFINE_string('project_id', None, 'The Google BigQuery project ID.')
gflags.DEFINE_string('dataset_id', None, 'The Google BigQuery dataset ID.')
gflags.DEFINE_string('table_prefix', '', 'The string to prefix all table names with.')
gflags.DEFINE_string('schema_file', None, 'The path to a schema file. Defaults to JSON_DIR/schema.json.')
gflags.DEFINE_string('credential_storage', 'biqueryize_creds.dat', 'Where to store credentials.')
gflags.DEFINE_string('client_id', None, 'The Google BigQuery client_id.')
gflags.DEFINE_string('client_secret', None, 'The Google BigQuery client_secret.')
gflags.DEFINE_string('start_at', '', 'The table at which to start the upload.')
gflags.DEFINE_list('skip_tables', [], 'Tables to skip.')
gflags.DEFINE_list('only_tables', None, 'Upload only these tables.')
gflags.MarkFlagAsRequired('project_id')
gflags.MarkFlagAsRequired('dataset_id')
gflags.MarkFlagAsRequired('client_id')
gflags.MarkFlagAsRequired('client_secret')

TYPE_MAPPING = dict(string='STRING', integer='INTEGER', float='FLOAT', boolean='BOOLEAN', primary='INTEGER')
TABLE_STANZA = '''--xxx
Content-Type: application/json; charset=UTF-8

{
  "configuration": {
    "load": {
      "sourceFormat": "NEWLINE_DELIMITED_JSON",
      "schema": {
        "fields":%s
      },
      "destinationTable": {
        "projectId": "%s",
        "datasetId": "%s",
        "tableId": "%s"
      }
    }
  }
}
--xxx
Content-Type: application/octet-stream

%s
--xxx--
'''
def load_tables(http, service, schema, json_dir):
  """Actually load all the requested tables into BigQuery."""
  url = 'https://www.googleapis.com/upload/bigquery/v2/projects/%s/jobs' % FLAGS.project_id
  if FLAGS.only_tables:
    schema = [i for i in schema.items() if i[0] in FLAGS.only_tables]
  else:
    schema = [i for i in schema.items() if FLAGS.start_at <= i[0]]
  pbar = ProgressBar(widgets=['Uploading...', Bar(), ' ', Percentage(), ' ', ETA()],
                     maxval=len(schema)-len(FLAGS.skip_tables)).start()
  jobs = dict()
  for table_name, scheme in sorted(schema, key=lambda x: x[0]):
    if table_name in FLAGS.skip_tables:
      continue
    table = None
    with open(os.path.join(json_dir, '%s.json' % table_name)) as f:
      table = json.load(f)
    table_id = FLAGS.table_prefix + table_name
    bq_schema = []
    for field, ftype in scheme.items():
      bq_schema.append(dict(mode='nullable', name=field, type=TYPE_MAPPING[ftype[0]]))
    bq_schema = json.dumps(bq_schema)
    data = []
    for row in table['data']:
      pbar.update(len(jobs.keys()))
      data.append(json.dumps(row))
    data = '\n'.join(data)
    bq_request = TABLE_STANZA % (bq_schema, FLAGS.project_id, FLAGS.dataset_id, table_id, data)
    bq_headers = {'Content-Type': 'multipart/related; boundary=xxx'}
    resp, content = http.request(url, method='POST', body=bq_request, headers=bq_headers)
    if resp.status != 200:
      print 'Error in sending request.'
      print 'REQUEST:'
      print bq_request
      print '--------------'
      print 'RESPONSE (%s):' % resp
      print content
      sys.exit(1)
    content = json.loads(content)
    jobs[content['jobReference']['jobId']] = table_name
    pbar.update(len(jobs.keys()))
  pbar.finish()
  import time
  while True:
    jobCollection = service.jobs()
    for jobRef in list(jobs.keys()):
      getJob = jobCollection.get(projectId=FLAGS.project_id, jobId=jobRef).execute()
      currentStatus = getJob['status']['state']
      if 'DONE' == currentStatus:
        print 'Table %s done!' % jobs[jobRef]
        del jobs[jobRef]
    if len(jobs.keys()) == 0:
      break
    time.sleep(10)

def validate_args(argv):
  try:
    argv = FLAGS(argv)
  except gflags.FlagsError, e:
    print '%s\nUsage: %s JSON_DIR\n%s' % (e, sys.argv[0], FLAGS)
    sys.exit(1)
  if len(argv) != 2:
    print 'Incorrect number of arguments.\nUsage: %s JSON_DIR\n%s' % (sys.argv[0], FLAGS)
    sys.exit()
  json_dir = argv[1]
  if not os.path.isdir(json_dir):
    print 'The given JSON dir doesn\'t exist!'
    sys.exit(1)
  if not FLAGS.schema_file:
    FLAGS.schema_file = os.path.join(json_dir, 'schema.json')
  if not os.path.isfile(FLAGS.schema_file):
    print 'The given schema file doesn\'t exist!'
    sys.exit(1)
  schema = None
  with open(FLAGS.schema_file) as s:
    schema = json.load(s)
  if not schema:
    print 'Unable to load the given schema file!'
    sys.exit(1)
  return json_dir, schema

def main(argv):
  json_dir, schema = validate_args(argv)
  storage = Storage(FLAGS.credential_storage)
  credentials = storage.get()
  FLOW = OAuth2WebServerFlow(
    client_id=FLAGS.client_id,
    client_secret=FLAGS.client_secret,
    scope='https://www.googleapis.com/auth/bigquery',
    user_agent='bigqueryize/1.0'
  )
  if not credentials or credentials.invalid:
    credentials = run(FLOW, storage)
  http = httplib2.Http()
  http = credentials.authorize(http)
  service = build('bigquery', 'v2', http=http)
  load_tables(http, service, schema, json_dir)

if __name__ == '__main__':
  main(sys.argv)
