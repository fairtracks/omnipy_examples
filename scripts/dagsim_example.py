#!/usr/bin/env python3

from omnipy import runtime
from omnipy_examples.dagsim import import_and_convert_bif_files_to_json

runtime.config.engine = 'local'

import_and_convert_bif_files_to_json.run('input/bif')
