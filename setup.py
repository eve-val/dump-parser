import os
from setuptools import setup

setup(
  name = "ccp_sde_parser",
  version = "1.0.1",
  author = "Silas Snider",
  author_email = "swsnider@gmail.com",
  description = ("EVE Online Static Dump Export Parser. Works with https://github.com/eve-val/dump_extractor"),
  license = "BSD",
  keywords = "EVE Online Static Dump Export Parser",
  url = "https://github.com/eve-val/dump-parser",
  packages=['ccp_sde_parser'],
  long_description="EVE Online Static Dump Export Parser. Works with https://github.com/eve-val/dump_extractor",
  classifiers=[
    "Development Status :: 3 - Alpha",
    "Topic :: Utilities",
    "License :: OSI Approved :: BSD License",
  ],
  install_requires=[
    'google-api-python-client',
    'python-gflags',
    'progressbar',
    'PyYAML'
  ],
  entry_points={
    'console_scripts': [
      'split_tables = ccp_sde_parser.split_tables:main',
      'schema_converter = ccp_sde_parser.schema_converter:main',
      'merge_ccp_yaml = ccp_sde_parser.merge_ccp_yaml:main',
      'csvize = ccp_sde_parser.csvize:main',
      'sqlize = ccp_sde_parser.sqlize:main',
      'bigqueryize = ccp_sde_parser.bigqueryize:main',
    ]
  }
)
