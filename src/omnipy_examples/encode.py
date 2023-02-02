from omnipy.compute.flow import FuncFlowTemplate, LinearFlowTemplate
from omnipy.modules.fairtracks.tasks import import_dataset_from_encode
from omnipy.modules.general.tasks import cast_dataset
from omnipy.modules.json.flows import flatten_nested_json
from omnipy.modules.json.models import JsonDictOfAnyModel
from omnipy.modules.json.util import serialize_to_tarpacked_json_files
from omnipy.modules.pandas.models import PandasDataset
from omnipy.modules.pandas.tasks import convert_dataset_list_of_dicts_to_pandas
from omnipy.modules.pandas.util import serialize_to_tarpacked_csv_files
import omnipy.modules.tables.models
from omnipy.modules.tables.tasks import remove_columns

# cast_to_dict_on_top = cast_dataset.refine(
#     name='cast_to_dict_on_top',
#     fixed_params=dict(cast_model=JsonDictOfAnyModel),
# )

# encode_json_pruned =
# encode_json_dict = cast_to_dict_on_top.run(encode_json)

# runtime.config.engine = 'prefect'
# runtime.config.prefect.use_cached_results = True
#
#
# @FuncFlowTemplate
# def import_encode_data_tmpl():
#     encode_json = import_dataset_from_encode(
#         endpoints=[
#             'experiment',
#             'biosample',
#         ],
#         max_data_item_count=25,
#         serialize_as='csv',
#     )
#     encode_json_pruned = remove_columns(
#         encode_json,
#         column_keys_for_data_items=dict(
#             experiment=['audit'],
#             biosample=['audit'],
#         ),
#         serialize_as='csv',
#     )
#     return encode_json_pruned
#
#
# import_encode_data.run()


@LinearFlowTemplate(
    import_dataset_from_encode.refine(
        fixed_params=dict(
            endpoints=[
                'experiment',
                'biosample',
            ],
            max_data_item_count=25,
        )),
    flatten_nested_json,
    remove_columns.refine(
        fixed_params=dict(
            column_keys_for_data_items=dict(
                experiment=['audit'],
                biosample=['audit'],
            ))),
    convert_dataset_list_of_dicts_to_pandas,
)
def import_and_flatten_encode_data() -> PandasDataset:
    ...
