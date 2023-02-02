#!/usr/bin/env python3

from omnipy import runtime
from omnipy_examples.isajson import convert_isa_json_to_relational_tables

runtime.config.engine = 'local'

convert_isa_json_to_relational_tables.run('input/isa-json')
