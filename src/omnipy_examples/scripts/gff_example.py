#!/usr/bin/env python3

from omnipy import runtime
from omnipy_examples.gff import import_gff_as_pandas

runtime.config.engine = 'local'

import_gff_as_pandas.run('input/gff')