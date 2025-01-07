from docker.utils.json_stream import json_decoder
from omnipy import (Chain2,
                    Chain3,
                    convert_dataset,
                    Dataset,
                    HttpUrlDataset,
                    LinearFlowTemplate,
                    MatchItemsModel,
                    Model,
                    PandasDataset,
                    SplitToItemsModel,
                    SplitToLinesModel,
                    StrDataset,
                    TableOfPydanticRecordsModel,
                    TaskTemplate)
from omnipy_examples.util import get_github_repo_urls
from pydantic import BaseModel, conint, constr

# Restricted types
GenomeCoord = conint(ge=0, le=2**64 - 1)
Color = conint(ge=0, le=255)
RgbColor = tuple[Color, Color, Color]

# Parameterized Omnipy models
SplitOnCommaModel = SplitToItemsModel.adjust('SplitOnCommaModel', delimiter=',')
SplitOnCommaTrailingModel = SplitToItemsModel.adjust(
    'SplitOnCommaTrailingModel', delimiter=',', strip_chars=',')
FilterCommentsAndEmptyLinesModel = MatchItemsModel.adjust(
    'FilterCommentsAndEmptyLinesModel',
    match_functions=(lambda x: x.startswith('#'), lambda x: x.strip() == ''),
    invert_matches=True,
    match_all=False)

# Chained Omnipy models
SplitOnComma2RgbColorModel = Chain2[SplitOnCommaModel, Model[RgbColor]]
SplitOnComma2ListOfIntsModel = Chain2[SplitOnCommaTrailingModel, Model[list[int]]]


# Pydantic models
class BedRecordModel(BaseModel):
    chrom: constr(min_length=1, max_length=255, regex='[a-zA-Z0-9]+')
    chromStart: GenomeCoord
    chromEnd: GenomeCoord
    name: constr(min_length=1, max_length=255, regex='[\x20-\x7e]+') | None
    score: conint(ge=0, le=1000) | None
    strand: constr(regex='[-+\.]') | None
    thickStart: GenomeCoord | None
    thickEnd: GenomeCoord | None
    itemRgb: SplitOnComma2RgbColorModel | conint(ge=0, le=0) | None
    blockCount: conint(ge=0) | None
    blockSizes: SplitOnComma2ListOfIntsModel | None
    blockStarts: SplitOnComma2ListOfIntsModel | None


# Omnipy models
class BedModel(Chain3[SplitToLinesModel,
                      FilterCommentsAndEmptyLinesModel,
                      TableOfPydanticRecordsModel[BedRecordModel]]):
    ...


# Omnipy datasets
class BedDataset(Dataset[BedModel]):
    ...


# Omnipy tasks
@TaskTemplate()
def fetch_bed_dataset(url_list: HttpUrlDataset) -> StrDataset:
    bed_raw_dataset = StrDataset()
    bed_raw_dataset.load(url_list)
    return bed_raw_dataset


# Omnipy flows
@LinearFlowTemplate(
    get_github_repo_urls,
    fetch_bed_dataset,
    convert_dataset.refine(name='parse_bed', fixed_params={'dataset_cls': BedDataset}),
    convert_dataset.refine(
        name='convert_to_dataframe', fixed_params={'dataset_cls': PandasDataset}),
)
def import_bed_files_to_pandas(owner: str, repo: str, branch: str, path: str,
                               file_suffix: str) -> PandasDataset:
    ...


# Running the flow
if __name__ == '__main__':
    import_bed_files_to_pandas.run(
        owner='arq5x', repo='bedtools2', branch='master', path='data', file_suffix='bed')

json_decoder