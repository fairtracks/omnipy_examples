from typing import Tuple

from omnipy.modules.pandas.models import PandasDataset
import pandas as pd


def is_pairwise_consistent_values(df_1: pd.DataFrame,
                                  df_2: pd.DataFrame,
                                  common_headers: Tuple[str, ...]):
    df_1_common_cols = pd.DataFrame(df_1, columns=common_headers)
    df_2_common_cols = pd.DataFrame(df_2, columns=common_headers)
    return (df_1_common_cols.drop_duplicates().sort_values(by=list(common_headers)).reset_index(drop=True) == \
        df_2_common_cols.drop_duplicates().sort_values(by=list(common_headers)).reset_index(drop=True)).all(axis=None)


def join_tables(dataset: PandasDataset,
                join_type: str = 'outer',
                allow_multiple_join_cols_if_consistent: bool = False) -> PandasDataset:
    assert len(dataset) == 2

    output_dataset = PandasDataset()

    table_name_1, table_name_2 = tuple(dataset.keys())
    output_table_name = f'{table_name_1}_join_{table_name_2}'
    df_1 = dataset[table_name_1]
    df_2 = dataset[table_name_2]

    common_headers_set = set(df_1.columns) & set(df_2.columns)
    common_headers = tuple(col for col in df_1.columns if col in common_headers_set)

    join_cols = []
    if len(common_headers) > 1:
        if allow_multiple_join_cols_if_consistent:
            if is_pairwise_consistent_values(df_1, df_2, common_headers):
                join_cols += list(common_headers)
            else:
                raise ValueError()
        else:
            raise ValueError(f'No common column names were found. '
                             f'"{table_name_1}": {tuple(df_1.columns)}. '
                             f'"{table_name_2}": {tuple(df_2.columns)}')
    else:
        join_cols = common_headers[0]

    merged_df = pd.merge(df_1, df_2, on=join_cols, how=join_type).convert_dtypes()

    output_dataset[output_table_name] = merged_df
    return output_dataset
