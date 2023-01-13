from omnipy import runtime
from omnipy.modules.general.tasks import cast_dataset
from omnipy.modules.json.models import JsonDictOfAnyModel
from omnipy.modules.json.tasks import import_directory
from omnipy.modules.tables.models import JsonTableOfStrings
from omnipy.modules.tables.tasks import (flatten_nested_json_to_list_of_dicts,
                                         transpose_dataset_of_dicts_to_lists)

runtime.config.engine = 'local'
runtime.config.prefect.use_cached_results = False
runtime.config.job.persist_data_dir_path

cast_to_json_dict_of_any = cast_dataset.refine(
    name='cast_to_json_dict_of_any',
    fixed_params=dict(cast_model=JsonDictOfAnyModel))
cast_to_table_of_strings_and_lists = cast_dataset.refine(
    name='cast_to_table_of_strings_and_lists',
    fixed_params=dict(cast_model=JsonTableOfStrings))

# Workflow
isa_json_per_infile_ds = import_directory.run(directory='input/isa-json')
isa_json_per_infile_dict_ds = cast_to_json_dict_of_any.run(
    isa_json_per_infile_ds)
isa_json_nested_list_ds = transpose_dataset_of_dicts_to_lists.run(
    isa_json_per_infile_dict_ds)
isa_json_unnested_list_ds = flatten_nested_json_to_list_of_dicts.run(
    isa_json_nested_list_ds)
isa_json_tabular = cast_to_table_of_strings_and_lists.run(
    isa_json_unnested_list_ds)
