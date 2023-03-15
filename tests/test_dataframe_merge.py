import os

from omnipy.modules.pandas.models import PandasDataset
from pandas import DataFrame
import pytest
from src.omnipy_examples.table_tasks import join_tables


@pytest.fixture
def table_abc():
    return DataFrame(
        [
            ['abc', 123, True],
            ['bcd', 234, False],
            ['cde', 345, True],
        ],
        columns=['A', 'B', 'C'],
    )


@pytest.fixture
def table_dbe():
    return DataFrame(
        [
            [1.2, 345, 34],
            [3.4, 234, 23],
            [3.2, 123, 34],
        ],
        columns=['D', 'B', 'E'],
    )


@pytest.fixture
def table_dbe2():
    return DataFrame(
        [
            [1.2, 345, 34],
            [3.4, 432, 23],
            [3.2, 123, 34],
        ],
        columns=['D', 'B', 'E'],
    )


@pytest.fixture
def table_bce():
    return DataFrame(
        [
            [345, True, 34],
            [234, False, 23],
            [123, True, 34],
        ],
        columns=['B', 'C', 'E'],
    )


def test_default_outer_join_tables_on_column_all_matching(table_abc, table_dbe):
    dataset = PandasDataset()
    dataset['table_abc'] = table_abc
    dataset['table_dbe'] = table_dbe

    joined_dataset = join_tables(dataset)

    assert joined_dataset.to_data() == {
        'table_abc_join_table_dbe': [
            dict(A='abc', B=123, C=True, D=3.2, E=34),
            dict(A='bcd', B=234, C=False, D=3.4, E=23),
            dict(A='cde', B=345, C=True, D=1.2, E=34),
        ]
    }


def test_default_outer_join_tables_on_column_some_matching(table_abc, table_dbe2):
    dataset = PandasDataset()
    dataset['table_abc'] = table_abc
    dataset['table_dbe2'] = table_dbe2

    joined_dataset = join_tables(dataset)

    assert joined_dataset.to_data() == {
        'table_abc_join_table_dbe2': [
            dict(A='abc', B=123, C=True, D=3.2, E=34),
            dict(A='bcd', B=234, C=False, D=None, E=None),
            dict(A='cde', B=345, C=True, D=1.2, E=34),
            dict(A=None, B=432, C=None, D=3.4, E=23),
        ]
    }


def test_inner_join_tables_on_column_all_matching(table_abc, table_dbe):
    dataset = PandasDataset()
    dataset['table_abc'] = table_abc
    dataset['table_dbe'] = table_dbe

    joined_dataset = join_tables(dataset, join_type='inner')

    assert joined_dataset.to_data() == {
        'table_abc_join_table_dbe': [
            dict(A='abc', B=123, C=True, D=3.2, E=34),
            dict(A='bcd', B=234, C=False, D=3.4, E=23),
            dict(A='cde', B=345, C=True, D=1.2, E=34),
        ]
    }


def test_inner_join_tables_on_column_some_matching(table_abc, table_dbe2):
    dataset = PandasDataset()
    dataset['table_abc'] = table_abc
    dataset['table_dbe2'] = table_dbe2

    joined_dataset = join_tables(dataset, join_type='inner')

    assert joined_dataset.to_data() == {
        'table_abc_join_table_dbe2': [
            dict(A='abc', B=123, C=True, D=3.2, E=34),
            dict(A='cde', B=345, C=True, D=1.2, E=34),
        ]
    }


def test_left_join_tables_on_column_all_matching(table_abc, table_dbe):
    dataset = PandasDataset()
    dataset['table_abc'] = table_abc
    dataset['table_dbe'] = table_dbe

    joined_dataset = join_tables(dataset, join_type='left')

    assert joined_dataset.to_data() == {
        'table_abc_join_table_dbe': [
            dict(A='abc', B=123, C=True, D=3.2, E=34),
            dict(A='bcd', B=234, C=False, D=3.4, E=23),
            dict(A='cde', B=345, C=True, D=1.2, E=34),
        ]
    }


def test_left_join_tables_on_column_some_matching(table_abc, table_dbe2):
    dataset = PandasDataset()
    dataset['table_abc'] = table_abc
    dataset['table_dbe2'] = table_dbe2

    joined_dataset = join_tables(dataset, join_type='left')

    assert joined_dataset.to_data() == {
        'table_abc_join_table_dbe2': [
            dict(A='abc', B=123, C=True, D=3.2, E=34),
            dict(A='bcd', B=234, C=False, D=None, E=None),
            dict(A='cde', B=345, C=True, D=1.2, E=34),
        ]
    }


def test_right_join_tables_on_column_all_matching(table_abc, table_dbe):
    dataset = PandasDataset()
    dataset['table_abc'] = table_abc
    dataset['table_dbe'] = table_dbe

    joined_dataset = join_tables(dataset, join_type='right')

    assert joined_dataset.to_data() == {
        'table_abc_join_table_dbe': [
            dict(A='cde', B=345, C=True, D=1.2, E=34),
            dict(A='bcd', B=234, C=False, D=3.4, E=23),
            dict(A='abc', B=123, C=True, D=3.2, E=34),
        ]
    }


def test_right_join_tables_on_column_some_matching(table_abc, table_dbe2):
    dataset = PandasDataset()
    dataset['table_abc'] = table_abc
    dataset['table_dbe2'] = table_dbe2

    joined_dataset = join_tables(dataset, join_type='right')

    assert joined_dataset.to_data() == {
        'table_abc_join_table_dbe2': [
            dict(A='cde', B=345, C=True, D=1.2, E=34),
            dict(A=None, B=432, C=None, D=3.4, E=23),
            dict(A='abc', B=123, C=True, D=3.2, E=34),
        ]
    }


def test_default_outer_join_tables_multiple_columns_same_name_error(table_abc,
                                                                    table_bce_consistent):
    dataset = PandasDataset()
    dataset['table_abc'] = table_abc
    dataset['table_bce_consistent'] = table_bce_consistent

    with pytest.raises(ValueError):
        join_tables(dataset)


def test_default_outer_join_tables_multiple_columns_same_name_allow_multiple_consistent(
        table_abc, table_bce_consistent):
    dataset = PandasDataset()
    dataset['table_abc'] = table_abc
    dataset['table_bce_consistent'] = table_bce_consistent

    joined_dataset = join_tables(dataset, allow_multiple_join_cols_if_consistent=True)

    assert joined_dataset.to_data() == {
        'table_abc_join_table_bce_consistent': [
            dict(A='abc', B=123, C=True, E=34),
            dict(A='bcd', B=234, C=False, E=23),
            dict(A='cde', B=345, C=True, E=34),
        ]
    }


def test_default_outer_join_tables_multiple_columns_same_name_allow_multiple_consistent_dupl_row(
        table_abc, table_bce_consistent_dupl_row):
    dataset = PandasDataset()
    dataset['table_abc'] = table_abc
    dataset['table_bce_consistent_dupl_row'] = table_bce_consistent_dupl_row

    joined_dataset = join_tables(dataset, allow_multiple_join_cols_if_consistent=True)

    assert joined_dataset.to_data() == {
        'table_abc_join_table_bce_consistent_dupl_row': [
            dict(A='abc', B=123, C=True, E=34),
            dict(A='bcd', B=234, C=False, E=23),
            dict(A='bcd', B=234, C=False, E=45),
            dict(A='cde', B=345, C=True, E=34),
        ]
    }


def test_default_outer_join_tables_multiple_columns_same_name_allow_multiple_inconsistent(
        table_abc, table_bce_inconsistent):
    dataset = PandasDataset()
    dataset['table_abc'] = table_abc
    dataset['table_bce_inconsistent'] = table_bce_inconsistent

    with pytest.raises(ValueError):
        join_tables(dataset, allow_multiple_join_cols_if_consistent=True)


# def test_join_tables_on_column_missing_data(table_abc, table_dbe2):
#     dataset = PandasDataset()
#     dataset['table_abc'] = table_abc
#     dataset['table_dbe2'] = table_dbe2
#
#     joined_dataset = join_tables(dataset)
#
#     assert joined_dataset.to_data() == {
#         'table_a_join_table_b': [
#             dict(A='abc', B=123, C=True, D=3.2, E=34),
#             dict(A='bcd', B=234, C=False, D=3.4, E=23),
#             dict(A='cde', B=345, C=True, D=1.2, E=34),
#         ]
#     }

# Further tests
# TODO: join_tables: When Multiple columns that have the same name -> check consistency of common columns.
#       If identical, then merge columns.
# TODO: join_tables: Specify left/right columns to merge on
# TODO: join_tables: Specify left/right columns to merge on -> multiple columns with same name
# TODO: join_tables: Specify left/right columns to merge on -> specified columns do not exist
# TODO: join_tables: No overlapping column names in A and B
# TODO: join_tables: Empty dataframe
# TODO: join_tables: Multiple matching rows
# TODO: join_tables: Multiple tables
