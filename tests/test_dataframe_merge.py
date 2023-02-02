from omnipy.modules.pandas.models import PandasDataset
from pandas import DataFrame
import pytest
from src.omnipy_examples.table_tasks import join_tables


@pytest.fixture
def table_a():
    return DataFrame(
        [
            ['abc', 123, True],
            ['bcd', 234, False],
            ['cde', 345, True],
        ],
        columns=['A', 'B', 'C'],
    )


@pytest.fixture
def table_b():
    return DataFrame(
        [
            [1.2, 345, 34],
            [3.4, 234, 23],
            [3.2, 123, 34],
        ],
        columns=['D', 'B', 'E'],
    )


@pytest.fixture
def table_c():
    return DataFrame(
        [
            [1.2, 345, 34],
            [3.4, 432, 23],
            [3.2, 123, 34],
        ],
        columns=['D', 'B', 'E'],
    )


def test_join_tables_on_column(table_a, table_b):
    dataset = PandasDataset()
    dataset['table_a'] = table_a
    dataset['table_b'] = table_b

    joined_dataset = join_tables(dataset)

    assert joined_dataset.to_data() == {
        'table_a_join_table_b': [
            dict(A='abc', B=123, C=True, D=3.2, E=34),
            dict(A='bcd', B=234, C=False, D=3.4, E=23),
            dict(A='cde', B=345, C=True, D=1.2, E=34),
        ]
    }


# Further tests
# TODO: Missing data (e.g. table_a + table_c)
# TODO: Multiple tables
# TODO: Multiple columns that are the same
# TODO: Different column in A and B
# TODO: Type of merge: Inner, Outer, Left, Right
# TODO: Empty dataframe
# TODO: Multiple matching rows
