import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
  return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
  name = "ccp_sde_parser",
  version = "1.0.0",
  author = "Silas Snider",
  author_email = "swsnider@gmail.com",
  description = ("EVE Online Static Dump Export Parser. Works with https://github.com/eve-val/dump_extractor"),
  license = "BSD",
  keywords = "EVE Online Static Dump Export Parser",
  url = "https://github.com/eve-val/dump-parser",
  packages=['ccp_sde_parser'],
  long_description=read('README'),
  classifiers=[
    "Development Status :: 3 - Alpha",
    "Topic :: Utilities",
    "License :: OSI Approved :: BSD License",
  ],
  install_requires=[
    'google-api-python-client',
    'gflags',
    'progressbar',
    'PyYAML'
  ]
  entry_points={
    'console_scripts': [
      'split_tables = ccp_sde_parser.split_tables:main',
      'schema_converter = ccp_sde_parser.schema_converter:main',
      'merge_ccp_yaml = ccp_sde_parser.merge_ccp_yaml:main',
      'csvize = ccp_sde_parser.csvize:main',
      'sqlize = ccp_sde_parser.sqlize:main',
      'biqueryize = ccp_sde_parser.biqueryize:main',
    ]
  }
)
