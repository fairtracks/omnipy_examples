from omnipy import (Chain2,
                    convert_dataset,
                    Dataset,
                    LinearFlowTemplate,
                    Model,
                    PandasDataset,
                    SplitToItemsModel,
                    StrDataset,
                    TableOfPydanticRecordsDataset,
                    TableOfPydanticRecordsModel,
                    TaskTemplate)
from omnipy_examples.util import get_github_repo_urls
from pydantic import BaseModel, conint, constr

SplitToItemsOnCommaModel = SplitToItemsModel.adjust('SplitToItemsOnCommaModel', delimiter=',')
SplitToItemsWithTrailingCommaModel = SplitToItemsModel.adjust(
    'SplitToItemsWithTrailingCommaModel', delimiter=',', strip_chars=',')

SplitTrailingCommaStrToIntsModel = Chain2[
    SplitToItemsWithTrailingCommaModel,
    Model[list[int]],
]


class BedDataclassModel(BaseModel):
    chrom: constr(min_length=1)
    chromStart: conint(ge=0)
    chromEnd: conint(ge=0)
    name: str
    score: conint(ge=0, le=1000)
    strand: constr(regex='[+-\.]')
    thickStart: conint(ge=0)
    thickEnd: conint(ge=0)
    itemRgb: Chain2[
        SplitToItemsOnCommaModel,
        Model[list[conint(ge=0, le=255)]],
    ]
    blockCount: conint(ge=0)
    blockSizes: SplitTrailingCommaStrToIntsModel
    blockStarts: SplitTrailingCommaStrToIntsModel


class BedModel(TableOfPydanticRecordsModel[BedDataclassModel]):
    ...


class BedDataset(Dataset[BedModel]):
    ...


@TaskTemplate
def fetch_bed_dataset(url_list: StrDataset) -> BedDataset:
    bed_raw_dataset = StrDataset()
    bed_raw_dataset.load(*url_list.values())

    bed_dataset = BedDataset()
    bed_dataset |= bed_raw_dataset
    bed_dataset[0] += bed_raw_dataset[0]
    return bed_dataset


@LinearFlowTemplate(
    get_github_repo_urls.refine(
        fixed_params={'branch': 'master'}, restore_outputs='auto_ignore_params'),
    fetch_bed_dataset,
    convert_dataset.refine(fixed_params={'dataset_cls': PandasDataset}),
    persist_outputs='disabled',
)
def import_bed_files_to_pandas(owner: str, repo: str, path: str, file_suffix: str) -> PandasDataset:
    ...
