#!/usr/bin/env python3

from omnipy import runtime
from omnipy_examples.uniprot import import_and_flatten_uniprot_with_magic

runtime.config.engine = 'local'
runtime.config.job.persist_outputs = 'all'
# runtime.config.job.restore_outputs = 'auto_ignore_params'

import_and_flatten_uniprot_with_magic.run()
