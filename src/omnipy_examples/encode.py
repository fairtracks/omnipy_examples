from omnipy import (convert_dataset_list_of_dicts_to_pandas,
                    flatten_nested_json,
                    LinearFlowTemplate,
                    PandasDataset,
                    remove_columns)
from omnipy.components._fairtracks.tasks import import_dataset_from_encode

# TODO: Reimplement encode example using Dataset.load()


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
