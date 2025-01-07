from collections import defaultdict
from math import nan

from omnipy import (Chain2,
                    Chain3,
                    convert_dataset,
                    Dataset,
                    import_directory,
                    LinearFlowTemplate,
                    Model,
                    NestedSplitToItemsModel,
                    PandasDataset,
                    PandasModel,
                    PersistOutputsOptions,
                    SplitToLinesModel,
                    TableListOfDictsOfJsonScalarsModel,
                    TableOfPydanticRecordsModel,
                    TaskTemplate)
import pandas as pd
from pydantic import BaseModel, conint, constr

# Constants

GFF_COLS = ['seqid', 'source', 'type', 'start', 'end', 'score', 'strand', 'phase', 'attributes']
ATTRIB_COL = GFF_COLS[-1]

# Models

# class GffFileDataclassModel(BaseModel):
#     comments: list[str] = []
#     directives: list[str] = []
#     data: list[str] = []
#     sequences: list[str] = []


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
        return gff_file


class StrDotMissingModel(Model[str | None]):
    @classmethod
    def _parse_data(cls, data: str | None) -> str | None:
        return None if data == '.' else data


GenomeCoord = conint(ge=0, le=2**64 - 1)


class FloatDotMissingModel(Model[float | str]):
    @classmethod
    def _parse_data(cls, data: float | str) -> float:
        return nan if data == '.' else float(data)


class StrandBoolDotMissingModel(Model[bool | None | str]):
    @classmethod
    def _parse_data(cls, data: bool | None | str) -> bool | None:
        if isinstance(data, str):
            match data:
                case '+':
                    return True
                case '-':
                    return False
                case '.':
                    return None
        else:
            return data


AttributesSplitToItemsModel = NestedSplitToItemsModel.adjust(
    'AttributesSplitToItemsModel', delimiters=(';', '='))


class GffRecordModel(BaseModel):
    seqid: constr(min_length=1, max_length=255, regex='[a-zA-Z0-9]+')
    source: StrDotMissingModel
    type: StrDotMissingModel
    start: GenomeCoord
    end: GenomeCoord
    score: FloatDotMissingModel
    strand: Chain2[constr(regex='[-+\.]'), StrandBoolDotMissingModel]
    phase: Chain2[constr(regex='[012\.]'), FloatDotMissingModel]
    attributes: str


# Omnipy models
class GffFeaturesModel(Chain2[SplitToLinesModel, TableOfPydanticRecordsModel[GffRecordModel]]):
    ...


# Chained models

# TODO: Fix deepcopy issue in AttributesToPandasModel.

AttributesToPandasModel = Chain3[
    Model[list[AttributesSplitToItemsModel]],
    TableListOfDictsOfJsonScalarsModel,
    PandasModel,
]

# Tasks


@TaskTemplate(iterate_over_data_files=True)
def gff_to_pandas(dataset: GffSectionsModel) -> PandasDataset:
    output = PandasDataset()
    for key, val in dataset.items():
        if key == 'features':
            plain_table = PandasModel(GffFeaturesModel(val))
            attributes_as_list: list[str] = plain_table[ATTRIB_COL].to_list()
            attributes_table = AttributesToPandasModel(attributes_as_list)
            # attributes_table = PandasModel(
            #     TableListOfDictsOfJsonScalarsModel(
            #         Model[list[AttributesSplitToItemsModel]](attributes_as_list)))
            plain_table = plain_table.drop(columns=[ATTRIB_COL])
            table = PandasModel(pd.concat([plain_table, attributes_table], axis=1, join='inner'))
        else:
            table = PandasModel(val)
        output[key] = table
    return output


# Flows


@LinearFlowTemplate(
    import_directory.refine(
        name='import_gff_files',
        fixed_params=dict(include_suffixes=('.gff',), model=Model[str]),
        # persist_outputs=PersistOutputsOptions.DISABLED,
    ),
    convert_dataset.refine(
        name='parse_gff',
        fixed_params=dict(dataset_cls=Dataset[GffSectionsModel]),
        # persist_outputs=PersistOutputsOptions.DISABLED,
    ),
    gff_to_pandas.refine(persist_outputs=PersistOutputsOptions.DISABLED,),
    # persist_outputs=PersistOutputsOptions.DISABLED,
)
def import_gff_as_pandas(directory: str) -> PandasDataset:
    ...
