from collections import defaultdict
from collections.abc import Iterable, Mapping
from math import nan
from pathlib import Path
from types import GenericAlias
from typing import Union

from omnipy import (Chain2,
                    convert_dataset,
                    Dataset,
                    import_directory,
                    IteratingPydanticRecordsModel,
                    LinearFlowTemplate,
                    Model,
                    NestedDataset,
                    NestedSplitToItemsModel,
                    SplitLinesToColumnsModel,
                    SplitToItemsModel,
                    SplitToLinesModel,
                    StrDataset,
                    TaskTemplate)
from omnipy.components.json.typedefs import JsonScalar
from omnipy.components.tables.models import (_ColumnWiseTableWithColNamesMixin,
                                             JsonMaxLevel2ColumnModel,
                                             JsonMaxLevel2ColumnWiseTableWithColNamesModel,
                                             JsonMaxLevel2Types,
                                             PrintableTable)
import omnipy.util.pydantic as pyd

# Constants

GFF_COLS = ['seqid', 'source', 'type', 'start', 'end', 'score', 'strand', 'phase', 'attributes']
ATTRIB_COL = GFF_COLS[-1]

# Models

AttributesSplitToItemsModel = NestedSplitToItemsModel.adjust(
    'AttributesSplitToItemsModel', delimiters=(';', '='))

SplitToItemsBySpaceModel = SplitToItemsModel.adjust('SplitToItemsBySpaceModel', delimiter=' ')
SplitToItemsByCommaModel = SplitToItemsModel.adjust('SplitToItemsByCommaModel', delimiter=',')

ReferencesSplitToItemsModel = NestedSplitToItemsModel.adjust(
    'ReferencesSplitToItemsModel', delimiters=(',', ':'))


class TargetRecord(pyd.BaseModel):
    target_id: str
    start: int
    end: int
    strand: bool | None = None

    @pyd.validator('strand', pre=True)
    def validate_strand(cls, v):
        if isinstance(v, str):
            match v:
                case '+':
                    return True
                case '-':
                    return False
                case _:
                    raise ValueError(f'Invalid strand value: {v}')
        return v


class GapRecord(pyd.BaseModel):
    operation: pyd.constr(regex='[MIDFR]', max_length=1)
    length: int


class GapModel(Model[GapRecord | str]):
    @classmethod
    def _parse_data(cls, data: GapRecord | str) -> GapRecord:
        if isinstance(data, GapRecord):
            return data

        assert len(data) >= 2
        return GapRecord(operation=data[0], length=data[1:])


class CurieRecord(pyd.BaseModel):
    namespace: str
    id: str


AttributesModel = Chain2[
    AttributesSplitToItemsModel,
    Model[dict[str, JsonScalar]],
]


class MySpitter(SplitToItemsByCommaModel):
    @classmethod
    def _parse_data(cls, data: SplitToItemsByCommaModel) -> SplitToItemsByCommaModel:
        spitted = super()._parse_data(data)
        return spitted


class GffAttributesRecord(pyd.BaseModel):
    class Config:
        extra = pyd.Extra.allow

    ID: str | None = None
    Name: str | None = None
    Alias: str | None = None
    Parent: Chain2[SplitToItemsByCommaModel, Model[list[str]]] | None = None
    Target: Chain2[SplitToItemsBySpaceModel, Model[TargetRecord]] | None = None
    Gap: Chain2[SplitToItemsBySpaceModel, GapModel] | None = None
    Derives_from: str | None = None
    Note: Chain2[SplitToItemsByCommaModel, Model[list[str]]] | None = None
    Dbxref: Chain2[ReferencesSplitToItemsModel, Model[list[tuple[str, str]]]] | None = None
    Ontology_term: Chain2[ReferencesSplitToItemsModel, Model[CurieRecord]] | None = None
    Is_circular: bool | None = None

    @pyd.validator('Is_circular', pre=True)
    def validate_is_circular(cls, v):
        if isinstance(v, str):
            match v:
                case _v if _v.lower() == 'true':
                    return True
                case _v if _v.lower() == 'false':
                    return False
                case _:
                    raise ValueError(f'Invalid value for "Is_circular": {v}')
        return v


class GffRecord(pyd.BaseModel):
    seqid: pyd.constr(min_length=1, max_length=255, regex='[a-zA-Z0-9]+')
    source: str | None = ...
    type: str | None = pyd.Field(...)
    start: int
    end: int = pyd.Field(...)
    score: float
    strand: bool | None = ...
    phase: float
    attributes: Chain2[AttributesSplitToItemsModel, Model[GffAttributesRecord]]

    class Config:
        arbitrary_types_allowed = True

    @pyd.validator('source', 'type', pre=True)
    def validate_perhaps_missing_string(cls, v):
        return None if v == '.' else v

    @pyd.validator('strand', pre=True)
    def validate_strand(cls, v):
        if isinstance(v, str):
            match v:
                case '+':
                    return True
                case '-':
                    return False
                case '.':
                    return None
                case _:
                    raise ValueError(f'Invalid strand value: {v}')
        return v

    @pyd.validator('score', pre=True)
    def validate_score(cls, v):
        return nan if v == '.' else float(v)

    @pyd.validator('phase', pre=True)
    def validate_phase(cls, v):
        if isinstance(v, str):
            match v:
                case '0' | '1' | '2':
                    return float(v)
                case '.':
                    return float('nan')
                case _:
                    raise ValueError(f'Invalid phase value: {v}')
        return v


class ParseGffTableModel(
        _ColumnWiseTableWithColNamesMixin,
        Chain2[SplitLinesToColumnsModel,
               IteratingPydanticRecordsModel[GffRecord,
                                             JsonMaxLevel2ColumnWiseTableWithColNamesModel,
                                             JsonMaxLevel2ColumnModel,
                                             JsonMaxLevel2Types]],
        PrintableTable,
):
    ...


class GffFileDataclassPydModel(pyd.BaseModel):
    comments: list[str]
    directives: list[str]
    sequences: list[str]
    features: ParseGffTableModel


class GffSectionsModel(Model[GffFileDataclassPydModel | SplitToLinesModel]):
    @classmethod
    def _parse_data(cls,
                    data: GffFileDataclassPydModel | SplitToLinesModel) -> GffFileDataclassPydModel:

        if isinstance(data, GffFileDataclassPydModel):
            return data

        in_sequences_section = False
        comments = []
        directives = []
        sequences = []
        features = []

        for line in data:
            match line:
                case '' | '###':
                    pass
                case '##FASTA':
                    in_sequences_section = True
                case s if s.startswith('##'):
                    directives.append(line)
                case s if s.startswith('#'):
                    comments.append(line)
                case _:
                    if in_sequences_section:
                        sequences.append(line)
                    else:
                        # Here, appending one at a time will create a large overhead
                        features.append(line)

        return GffFileDataclassPydModel(
            comments=comments, directives=directives, sequences=sequences, features=features)


class GffSectionsDataset(Dataset[GffSectionsModel]):
    ...


from omnipy.util.helpers import is_non_str_byte_iterable


class GroupByTypeModel(Chain2[Model[list], Model[dict[type | GenericAlias, list]]]):
    @classmethod
    def _parse_data(cls, data: Model[list]) -> Model[dict[type | GenericAlias, list]]:
        grouped: dict[type, list] = defaultdict(list)

        def _iter_union_type(seq: Iterable):
            return Union[tuple(type(item) for item in seq)]

        def _deduce_full_type(_item: object) -> type:
            try:
                if isinstance(_item, Mapping):
                    return type(_item)[  # type: ignore[index]
                        _iter_union_type(_item.keys()),
                        _iter_union_type(_item.values()),
                    ]
                elif isinstance(_item, tuple):
                    return tuple[tuple(type(_) for _ in _item)]
                elif is_non_str_byte_iterable(_item):
                    return type(_item)[_iter_union_type(_item)]  # type: ignore[index]
            except TypeError:
                pass
            return type(_item)

        for item in data.content:
            full_type = _deduce_full_type(item)
            grouped[full_type].append(item)  # pyright: ignore [reportArgumentType]
        return Model[dict[type | GenericAlias, list]](grouped)


# Flows


@TaskTemplate()
def first(dataset: StrDataset) -> StrDataset:
    return dataset[0:1]


@LinearFlowTemplate(
    import_directory.refine(
        name='import_gff_files',
        fixed_params=dict(include_suffixes=('.gff',)),
    ),
    first,
    convert_dataset.refine(
        name='parse_gff',
        fixed_params=dict(dataset_cls=GffSectionsDataset),
    ),
    convert_dataset.refine(
        name='to_nested_dataset',
        fixed_params=dict(dataset_cls=NestedDataset),
    ),
    # gff_to_pandas.refine(persist_outputs=PersistOutputsOptions.DISABLED,),
    # persist_outputs=PersistOutputsOptions.DISABLED,
)
def import_gff_as_pandas(directory: Path) -> NestedDataset:
    ...
