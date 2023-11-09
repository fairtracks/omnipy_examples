from omnipy.compute.flow import LinearFlowTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.modules.general.tasks import import_directory
from omnipy.modules.json.datasets import JsonDataset, JsonDictOfAnyDataset
from omnipy.modules.json.flows import flatten_nested_json
from omnipy.modules.json.models import JsonDictOfAnyModel, JsonModel
from omnipy.modules.json.tasks import (convert_dataset_string_to_json,
                                       transpose_dicts_of_lists_of_dicts_2_lists_of_dicts)
from omnipy.modules.pandas.tasks import convert_dataset_list_of_dicts_to_pandas


@LinearFlowTemplate(
    import_directory.refine(
        name='import_json_files_from_dir',
        fixed_params=dict(include_suffixes=('.json',)),
    ),
    convert_dataset_string_to_json,
    transpose_dicts_of_lists_of_dicts_2_lists_of_dicts,
    flatten_nested_json,
    convert_dataset_list_of_dicts_to_pandas,
)
def convert_isa_json_to_relational_tables(dir_path: str):
    ...


#
# @TaskTemplate()
# def insert_into_object(dataset: JsonDataset, insert_key: str) -> JsonDictOfAnyDataset:
#     output = JsonDataset()
#     for key, val in dataset.items():
#         output[key] = {insert_key: val}
#         # print('{"' + insert_key + '": ' + val.to_json() + '}')
#         # output[key] = JsonModel().from_json('{"' + insert_key + '": ' + val.to_json() + '}')
#     return output


@TaskTemplate(iterate_over_data_files=True)
def insert_into_object(input: JsonModel, insert_key: str) -> JsonDictOfAnyModel:
    return JsonDictOfAnyModel({insert_key: input})


@LinearFlowTemplate(
    import_directory.refine(
        name='import_json_files_from_dir',
        fixed_params=dict(include_suffixes=('.json',)),
    ),
    convert_dataset_string_to_json,
    insert_into_object.refine(
        name='insert_into_object_as_investigation',
        fixed_params=dict(insert_key='investigation'),
    ),
    transpose_dataset_of_dicts_to_lists,
    flatten_nested_json,
    convert_dataset_list_of_dicts_to_pandas,
)
def convert_isa_json_to_relational_tables_copy(dir_path: str):
    ...


convert_isa_json_to_relational_tables_copy.run('p27_orig')
