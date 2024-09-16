from collections import defaultdict
import os
from typing import cast, Generic, List, Optional, Tuple, TypeAlias, TypeVar

from omnipy import bind_adjust_model_func, SplitLinesToColumnsModel, SplitToLinesModel, StrModel
from omnipy.compute.flow import DagFlowTemplate, FuncFlowTemplate, LinearFlowTemplate
from omnipy.compute.task import TaskTemplate
from omnipy.data.dataset import Dataset
from omnipy.data.helpers import debug_get_sorted_validate_counts, debug_get_total_validate_count
from omnipy.data.model import Model
from omnipy.modules.general.tasks import convert_dataset, import_directory, split_dataset
from omnipy.modules.pandas.models import PandasDataset, PandasModel
from omnipy.modules.pandas.tasks import (concat_dataframes_across_datasets,
                                         convert_dataset_csv_to_pandas,
                                         convert_dataset_pandas_to_csv,
                                         extract_columns_as_files)
from omnipy.modules.raw.datasets import (SplitLinesToColumnsDataset,
                                         SplitToItemsDataset,
                                         SplitToLinesDataset)
from omnipy.modules.raw.models import _SplitToItemsMixin
from omnipy.modules.raw.tasks import modify_all_lines, modify_datafile_contents, modify_each_line
from omnipy.modules.tables.models import TableWithColNamesModel
import pandas as pd
from pydantic import BaseModel

# Constants

GFF_COLS = ['seqid', 'source', 'type', 'start', 'end', 'score', 'strand', 'phase', 'attributes']
ATTRIB_COL = GFF_COLS[-1]

# Models

# class GffTableModel(Model[SplitLinesToColumnsModel | list[str]]):
#     @classmethod
#     def _parse_data(cls, data: SplitLinesToColumnsModel | list[str]) -> SplitLinesToColumnsModel:
#         if isinstance(data, SplitLinesToColumnsModel):
#             return data
#         else:
#             return SplitLinesToColumnsModel(data, delimiter='\t')


class GffFileDataclassModel(BaseModel):
    comments: list[str] = []
    directives: list[str] = []
    data: list[str] = []
    sequences: list[str] = []


# class GffModel(Model[GffFileDataclassModel | SplitToLinesModel]):
class GffSectionsModel(Model[Dataset[Model[list[str]]] | SplitToLinesModel]):
    @classmethod
    def _parse_data(
            cls, data: Dataset[Model[list[str]]] | SplitToLinesModel) -> Dataset[Model[list[str]]]:

        if isinstance(data, Dataset):
            return data

        # gff_file = GffFileDataclassModel()
        gff_file = defaultdict(list[str])
        in_sequences_section = False

        for line in data:
            match line:
                case '' | '###':
                    pass
                case '##FASTA':
                    in_sequences_section = True
                case s if s.startswith('##'):
                    gff_file['directives'].append(line)
                case s if s.startswith('#'):
                    gff_file['comments'].append(line)
                case _:
                    if in_sequences_section:
                        gff_file['sequences'].append(line)
                    else:
                        gff_file['features'].append(line)
        # print(debug_get_sorted_validate_counts())
        return gff_file


class _SplitColumnValuesModelNew(
        Model[list[list[list[str]]] | list[list[str]] | list[list[StrModel]]],
        _SplitToItemsMixin,
):
    @classmethod
    def _parse_data(
        cls, data: list[list[list[str]]] | list[list[str]] | list[list[StrModel]]
    ) -> list[list[list[str]]]:
        if isinstance(data, list) and (len(data) == 0 or
                                       (isinstance(data[0], list) and
                                        (len(data[0]) == 0 or isinstance(data[0][0], list)))):
            return cast(list[list[list[str]]], data)

        return [[cls._split_line(cast(str, val)) for val in line] for line in data]


class SplitColumnValuesModelNew(_SplitColumnValuesModelNew):
    adjust = bind_adjust_model_func(_SplitColumnValuesModelNew.clone_model_cls,
                                    _SplitColumnValuesModelNew.Params)


# Functions

#
# def slice_lines_func(all_lines: List[str],
#                      start: Optional[int] = None,
#                      end: Optional[int] = None) -> List[str]:
#     return all_lines[start:end]
#

# Tasks


@TaskTemplate(iterate_over_data_files=True)
def gff_to_pandas(dataset: GffSectionsModel) -> PandasDataset:
    output = PandasDataset()
    for key in dataset.keys():

        if key == 'features':
            columns = SplitLinesToColumnsModel(dataset[key])
            # print('SplitLinesToColumnsModel', debug_get_sorted_validate_counts())

            columns.insert(0, GFF_COLS)
            table = PandasModel(TableWithColNamesModel(columns))
            # print('TableWithColNamesModel', debug_get_sorted_validate_counts())

            main_cols = table.loc[:, :'phase']
            attributes_col = table['attributes']
            attributes_as_list = attributes_col.values.to_numpy().tolist()
            SplitLinesToColumnsOnSemicolonModel = SplitLinesToColumnsModel.adjust(
                'SplitLinesToColumnsOnSemicolonModel', delimiter=';')
            attributes_as_table = SplitLinesToColumnsOnSemicolonModel(attributes_as_list)
            # print('SplitLinesToColumnsModel', debug_get_sorted_validate_counts())

            SplitColumnValuesOnEqualsModel = SplitColumnValuesModelNew.adjust(
                'SplitColumnValuesOnEqualsModel', delimiter='=')
            attributes_as_table_of_pairs = SplitColumnValuesOnEqualsModel(attributes_as_table)
            # print('SplitColumnValuesModel', debug_get_sorted_validate_counts())

            attributes_as_kw_table = PandasModel(attributes_as_table_of_pairs)
            # print('PandasModel', debug_get_sorted_validate_counts())

            table = PandasModel(
                pd.concat([main_cols, attributes_as_kw_table.contents], axis=1, join='inner'))
        else:
            table = PandasModel(dataset[key])
        output[key] = table
        # print(key, debug_get_sorted_validate_counts())
    # print(debug_get_total_validate_count())
    return output


#
# @TaskTemplate()
# def attrib_df_names(dataset: Dataset[Model[object]]) -> List[str]:
#     return [name for name in dataset.keys() if name.endswith(ATTRIB_COL)]
#
#
# @TaskTemplate()
# def transform_attr_line_to_json(_line_no: int, line: str) -> str:
#     items = [item.strip().split('=') for item in line.strip().split(';') if item]
#     json_obj_items = [f'"{key}": "{val}"' for key, val in items]
#     return f'{{{", ".join(json_obj_items)}}},' + os.linesep

# Flows


@LinearFlowTemplate(
    import_directory.refine(
        name='import_gff_files',
        fixed_params=dict(include_suffixes=('.gff',), model=Model[str]),
        persist_outputs='disabled',
    ),
    convert_dataset.refine(
        name='parse_gff',
        fixed_params=dict(dataset_cls=Dataset[GffSectionsModel]),
        persist_outputs='disabled',
    ),
    gff_to_pandas.refine(persist_outputs='disabled',),
    # convert_dataset.refine(
    #     name='parse_json',
    #     fixed_params=dict(dataset_cls=GffModel),
    # ),
    # convert_dataset_csv_to_pandas.refine(
    #     name='convert_gff_to_pandas',
    #     fixed_params=dict(delimiter='\t', first_row_as_col_names=False, col_names=GFF_COLS),
    # ),
    persist_outputs='disabled',
)
def import_gff_as_pandas(directory: str) -> PandasDataset:
    ...

    # num_lines: Optional[int] = None)


#
# @DagFlowTemplate(
#     extract_columns_as_files.refine(
#         fixed_params=dict(col_names=[ATTRIB_COL]),
#         result_key='dataset',
#     ),
#     attrib_df_names.refine(result_key='datafile_names_for_b'),
#     split_dataset,
# )
# def extract_attrib_col_as_separate_dataset(
#         dataset: PandasDataset) -> Tuple[PandasDataset, PandasDataset]:
#     ...
#
#
# @LinearFlowTemplate(
#     convert_dataset_pandas_to_csv.refine(fixed_params=dict(first_row_as_col_names=False)),
#     modify_each_line.refine(
#         name='transform_all_lines_to_json',
#         fixed_params=dict(modify_line_func=transform_attr_line_to_json),
#     ),
#     modify_datafile_contents.refine(
#         name='transform_datafile_start_and_end_to_json',
#         fixed_params=dict(modify_contents_func=lambda x: f'[{x[:-2]}]'),
#     ),  # Brackets + strip comma and newline from end
# )
# def convert_attrib_col_to_table(dataset: PandasDataset) -> PandasDataset:
#     ...

# import_gff_as_pandas.run('input/gff', num_lines=1000)

#
# @FuncFlowTemplate
# def import_gff_and_convert_to_pandas() -> PandasDataset:
#     data: PandasDataset = import_gff_as_pandas(1000)
#     return data
#
#
# import_gff_and_convert_to_pandas.run()

# data_9_attrib = Dataset[JsonTableOfStrings]()
# data_9_attrib.from_json(data_8_attrib.to_data())
#
# pd_data_7_attrib = PandasDataset()
# pd_data_7_attrib.from_data(data_9_attrib.to_data())
#
# pd_data_10 = concat_dataframes_across_datasets(
#     [pd_data_5_main, pd_data_7_attrib],
#     vertical=False,
# )
# return pd_data_10

# @FuncFlowTemplate()
# def convert_gff_files(data: Dataset[Model[str]]) -> PandasDataset:
#     data = import_directory('input/gff', suffix='.gff', model=Model[str])
#
#     data__2 = slice_lines(data, start=0, end=1000)
#
#     pd_data_3 = convert_dataset_csv_to_pandas(data_2,
#                                               delimiter='\t',
#                                               first_row_as_col_names=False,
#                                               col_names=GFF_COLS)
#
#     pd_data_4 = extract_columns_as_files(pd_data_3, [ATTRIB_COL])
#
#     pd_data_5_main, pd_data_3_attrib = split_dataset(
#         pd_data_4, attrib_df_names(pd_data_4))
#
#     data_6_attrib = to_csv(pd_data_3_attrib, first_row_as_col_names=False)
#
#     data_7_attrib = transform_all_lines_to_json(data_6_attrib)
#
#     data_8_attrib = transform_datafile_start_and_end_to_json(data_7_attrib)
#
#     data_9_attrib = Dataset[JsonTableOfStrings]()
#     data_9_attrib.from_json(data_8_attrib.to_data())
#
#     pd_data_7_attrib = PandasDataset()
#     pd_data_7_attrib.from_data(data_9_attrib.to_data())
#
#     pd_data_10 = concat_dataframes_across_datasets(
#         [pd_data_5_main, pd_data_7_attrib],
#         vertical=False,
#     )
#     return pd_data_10

# @FuncFlowTemplate
# def import_gff_and_convert_to_pandas() -> PandasDataset:
#     data: Dataset[Model[str]] = import_directory('input/gff',
#                                                  suffix='.gff',
#                                                  model=Model[str])
#     return convert_gff_files(data)
#
#
# import_gff_and_convert_to_pandas.run()
