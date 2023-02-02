from omnipy.modules.pandas.models import PandasDataset
import pandas as pd


def join_tables(dataset: PandasDataset) -> PandasDataset:
    assert len(dataset) == 2

    output_dataset = PandasDataset()

    table_name_1, table_name_2 = tuple(dataset.keys())
    output_table_name = f'{table_name_1}_join_{table_name_2}'
    df_1 = dataset[table_name_1]
    df_2 = dataset[table_name_2]

    common_headers = set(df_1.columns) & set(df_2.columns)
    assert len(common_headers) == 1

    output_dataset[output_table_name] = pd.merge(df_1, df_2, on=common_headers.pop(), how='outer')
    return output_dataset
