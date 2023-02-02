#!/usr/bin/env python3

from omnipy import runtime
from omnipy_examples.encode import import_and_flatten_encode_data

runtime.config.engine = 'local'

import_and_flatten_encode_data.run()