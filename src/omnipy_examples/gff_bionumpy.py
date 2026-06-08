from abc import ABC
from collections.abc import Mapping
from ctypes import cast
from dataclasses import asdict
from math import fabs
from pathlib import Path
from typing import Any, Generic, Iterable, Iterator, Protocol, SupportsIndex, TypeAlias, TypedDict

from attr import dataclass
import bionumpy
from bionumpy import EncodedArray, EncodedRaggedArray, GFFEntry
from bionumpy.string_array import StringArray
from npstructures.raggedarray import IndexableArray
import numpy as np
from numpy.lib.mixins import NDArrayOperatorsMixin
from omnipy import (ColumnModel,
                    ColumnWiseTableWithColNamesModel,
                    convert_dataset,
                    Dataset,
                    import_directory,
                    IteratingPydanticRecordsModel,
                    LinearFlowTemplate,
                    Model,
                    PersistOutputsOptions,
                    StrDataset,
                    TaskTemplate)
from omnipy.components.json.typedefs import JsonScalar
from omnipy.components.tables.models import _IsColumnWiseTableWithColNames, IterRow, PrintableTable
from omnipy.shared.protocols.stdlib_ext import IsItemSequenceLike
from omnipy.util.helpers import first_key_in_mapping
from pandas.io.common import abstractmethod
from typing_extensions import TypeVar

GFFEntry.__pydantic_model__ = True  # pyright: ignore [reportAttributeAccessIssue]

import numpy as np
# from omnipy.components.tables.models import ColumnWisePydanticRecordModel
from omnipy_examples.gff import GffRecord


class IsGFFEntry(TypedDict):
    seqid: StringArray
    source: EncodedRaggedArray
    type: StringArray
    start: np.ndarray[tuple[int], np.dtype[np.int64]]
    end: np.ndarray[tuple[int], np.dtype[np.int64]]
    score: EncodedRaggedArray
    strand: EncodedArray
    phase: EncodedRaggedArray
    attributes: EncodedRaggedArray


class GffEntryModel(Model[GFFEntry]):
    def _get_default_value(self) -> GFFEntry:
        return GFFEntry(*[[]] * 9)


class GffEntryDataset(Dataset[GffEntryModel]):
    pass


ColumnT = TypeVar('ColumnT')
ItemT = TypeVar('ItemT')
NumpyItemT = TypeVar('NumpyItemT', bound=np.dtype[Any])
ColumnModelT = TypeVar('ColumnModelT', bound=ColumnModel[Any, Any])


class StrDecodableColumnModel(ABC, ColumnModel[ColumnT, ItemT], Generic[ColumnT, ItemT]):
    def _decode_item(self, encoded: ItemT) -> str:
        return encoded

    def _decode_slice(self, encoded: IsItemSequenceLike[ItemT]) -> IsItemSequenceLike[str]:
        return encoded

    def __getitem__(self, item: SupportsIndex | slice) -> str:
        match (item):
            case SupportsIndex():
                return self._decode_item(super().__getitem__(item))
            case slice():
                return self._decode_slice(super().__getitem__(item))

    def __setitem__(self, key: SupportsIndex | slice, value: str) -> None:
        self.content[key] = value

    def __iter__(self) -> Iterator[str]:
        for el in self.content[:]:
            yield el


class EncodedRaggedArrayStrDecodableColumnModel(StrDecodableColumnModel[EncodedRaggedArray, str]):
    def _decode_item(self, encoded: str) -> str:
        return encoded.to_string()

    def _decode_slice(self, encoded: IsItemSequenceLike[str]) -> IsItemSequenceLike[str]:
        # return encoded.tolist()
        from bionumpy.encoded_array import from_encoded_array
        return np.fromiter((_.to_string() for _ in encoded.content), dtype=np.dtypes.StringDType())
        return from_encoded_array(encoded)


class EncodedArrayStrDecodableColumnModel(StrDecodableColumnModel[EncodedArray, str]):
    def _decode_item(self, encoded: str) -> str:
        return encoded.to_string()

    def _decode_slice(self, encoded: IsItemSequenceLike[str]) -> IsItemSequenceLike[str]:
        # return encoded.tolist()
        from bionumpy.encoded_array import from_encoded_array
        return from_encoded_array(encoded.content)
        # return np.fromiter((_.to_string() for _ in encoded), dtype=np.dtypes.StringDType())


class StringArrayStrDecodableColumnModel(StrDecodableColumnModel[StringArray, str]):
    def _decode_item(self, encoded: str) -> str:
        return encoded.content._data

    def _decode_slice(self, encoded: IsItemSequenceLike[str]) -> IsItemSequenceLike[str]:
        return encoded.content._data


class NumpyColumnModel(StrDecodableColumnModel[np.ndarray[tuple[int, ...], NumpyItemT], NumpyItemT],
                       Generic[NumpyItemT]):
    def _decode_item(self, encoded: str) -> str:
        return encoded

    def _decode_slice(self, encoded: IsItemSequenceLike[str]) -> IsItemSequenceLike[str]:
        return encoded.content

    ...


class StrDecodableIterRow(IterRow[ColumnModelT, ItemT], Generic[ColumnModelT, ItemT]):
    def __init__(self, content: Mapping[str, ColumnModelT]) -> None:
        new_content = {
            key: value[:] if isinstance(value, StrDecodableColumnModel) else value
            for key, value in content.items()
        }
        super().__init__(new_content)


GffColumnModelUnion: TypeAlias = (
    StringArrayStrDecodableColumnModel | EncodedRaggedArrayStrDecodableColumnModel
    | EncodedArrayStrDecodableColumnModel | NumpyColumnModel[np.dtype[np.int64]])
GffColumnItemsUnion: TypeAlias = str | int | np.dtype[np.int64]


class StrDecodableColumnWiseTableWithColNamesModel(ColumnWiseTableWithColNamesModel[
        GffColumnModelUnion,
        GffColumnItemsUnion,
]):
    def _get_iter_row(self) -> IterRow[GffColumnModelUnion, GffColumnItemsUnion]:
        return StrDecodableIterRow[GffColumnModelUnion, GffColumnItemsUnion](self._content)


class GffFromBionumpyTableModel(
        IteratingPydanticRecordsModel[GffRecord,
                                      StrDecodableColumnWiseTableWithColNamesModel,
                                      GffColumnModelUnion,
                                      GffColumnItemsUnion],
        PrintableTable):
    ...


class GffFromBionumpyTableDataset(Dataset[GffFromBionumpyTableModel]):
    ...


@TaskTemplate(iterate_over_data_files=True)
def cleanup_and_convert(
    gff_file: GffEntryModel
) -> ColumnWiseTableWithColNamesModel[GffColumnModelUnion, GffColumnItemsUnion]:
    # dataset = dataset[0:1]
    # first_key = first_key_in_mapping(dataset)
    # output_dataset = Dataset[ColumnWiseTableDictOfListsModel]()
    # gff_file_dict = gff_file.todict()
    # dsa: EncodedRaggedArray = []
    # asd: IsItemSequenceLike = dsa
    # gff_file_dict = asdict(gff_file.content)
    NUM_ITEMS = None

    gff_file_dict = {}
    gff_file_dict['seqid'] = StringArrayStrDecodableColumnModel(gff_file.chromosome[:NUM_ITEMS])
    gff_file_dict['source'] = EncodedRaggedArrayStrDecodableColumnModel(gff_file.source[:NUM_ITEMS])
    gff_file_dict['type'] = StringArrayStrDecodableColumnModel(gff_file.feature_type[:NUM_ITEMS])
    gff_file_dict['start'] = ColumnModel[np.ndarray[tuple[int], np.dtype[np.int64]], int](
        gff_file.start[:NUM_ITEMS])
    gff_file_dict['end'] = ColumnModel[np.ndarray[tuple[int], np.dtype[np.int64]], int](
        gff_file.stop[:NUM_ITEMS])
    gff_file_dict['score'] = EncodedRaggedArrayStrDecodableColumnModel(gff_file.score[:NUM_ITEMS])
    gff_file_dict['strand'] = EncodedArrayStrDecodableColumnModel(gff_file.strand[:NUM_ITEMS])
    gff_file_dict['phase'] = EncodedRaggedArrayStrDecodableColumnModel(gff_file.phase[:NUM_ITEMS])
    gff_file_dict['attributes'] = EncodedRaggedArrayStrDecodableColumnModel(
        gff_file.atributes[:NUM_ITEMS])
    # gff_file_dict['attributes'] = gff_file_dict['atributes']
    # del gff_file_dict['chromosome']
    # del gff_file_dict['stop']
    # del gff_file_dict['atributes']
    return StrDecodableColumnWiseTableWithColNamesModel(gff_file_dict)
    # output_dataset[first_key] = Model[dict[str, Model[list]]](gff_file_dict)
    # return gff_file.to(ColumnWiseTableWithColNamesModel)


@TaskTemplate()
def first(dataset: StrDataset) -> StrDataset:
    return dataset[0:1]


@LinearFlowTemplate(
    import_directory.refine(
        name='import_gff_files',
        fixed_params=dict(
            include_suffixes=('.gff',), dataset_cls=GffEntryDataset, open_func=bionumpy.open),
        persist_outputs=PersistOutputsOptions.DISABLED,
    ),
    # convert_dataset.refine(
    #     name='parse_gff',
    #     fixed_params=dict(dataset_cls=GffEntryDataset),
    #     persist_outputs=PersistOutputsOptions.DISABLED,
    # ),
    first.refine(persist_outputs=PersistOutputsOptions.DISABLED),
    cleanup_and_convert.refine(persist_outputs=PersistOutputsOptions.DISABLED),
    convert_dataset.refine(
        name='parse_col_wise_with_gff_model',
        fixed_params=dict(dataset_cls=GffFromBionumpyTableDataset),
        persist_outputs=PersistOutputsOptions.DISABLED,
    ),
    persist_outputs=PersistOutputsOptions.DISABLED,
)
def import_gff_to_bionumpy(directory: Path) -> GffEntryDataset:
    ...
