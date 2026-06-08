import base64
from hashlib import sha512
from pathlib import Path
from typing import cast

from jsoncanon import canonicalize
from jsoncanon.util import JSON
from omnipy import (DagFlowTemplate,
                    Dataset,
                    FuncFlowTemplate,
                    HttpUrlDataset,
                    JsonDataset,
                    JsonDictDataset,
                    JsonDictOfDictsDataset,
                    JsonDictOfDictsModel,
                    Model,
                    PersistOutputsOptions,
                    runtime,
                    StrDataset,
                    TableOfPydanticRecordsModel,
                    TaskTemplate)
import omnipy.util.pydantic as pyd
from omnipy_examples.util import get_github_repo_urls

runtime.config.data.http.for_host['raw.githubusercontent.com'].requests_per_time_period = 5000
runtime.config.data.http.for_host['raw.githubusercontent.com'].time_period_in_secs = 3600


# Models
class SeqColDigestTarget(pyd.BaseModel):
    name: str = ''
    digest: str = ''
    sorted_name_length_pairs_digest: str = ''


class SeqColDigestTargetModel(Model[SeqColDigestTarget]):
    ...


class SeqColDigestTargetDataset(Dataset[SeqColDigestTargetModel]):
    ...


class FastaChecksumRecord(pyd.BaseModel):
    name: str = ''
    length: int = 0
    refget_digest: str = ''
    md5_digest: str = ''


class FastaChecksumModel(Model[TableOfPydanticRecordsModel[FastaChecksumRecord]]):
    ...


class FastaChecksumDataset(Dataset[FastaChecksumModel]):
    ...


class NameLengthPair(pyd.BaseModel):
    name: str = ''
    length: int = 0


class NameLengthPairListModel(Model[list[NameLengthPair]]):
    ...


class SeqColLevel2(pyd.BaseModel):
    class Config:
        arbitrary_types_allowed = True

    names: list[str] = pyd.Field(default_factory=list)
    lengths: list[int] = pyd.Field(default_factory=list)
    sequences: list[str] = pyd.Field(default_factory=list)
    sorted_sequences: list[str] = pyd.Field(default_factory=list)
    name_length_pairs: NameLengthPairListModel = pyd.Field(default_factory=NameLengthPairListModel)


class SeqColLevel2Model(Model[SeqColLevel2]):
    ...


class SeqColLevel2Dataset(Dataset[SeqColLevel2Model]):
    ...


class SeqColLevel1(pyd.BaseModel):
    names: str = ''
    lengths: str = ''
    sequences: str = ''
    sorted_sequences: str = ''
    name_length_pairs: str = ''
    sorted_name_length_pairs: str = ''


class SeqColLevel1Model(Model[SeqColLevel1]):
    ...


class SeqColLevel1Dataset(Dataset[SeqColLevel1Model]):
    ...


class SeqColLevel1Inherent(pyd.BaseModel):
    names: str = ''
    sequences: str = ''


class SeqColLevel1InherentModel(Model[SeqColLevel1Inherent]):
    ...


class SeqColLevel1InherentDataset(Dataset[SeqColLevel1InherentModel]):
    ...


class SeqColLevel0Model(Model[str]):
    ...


class SeqColLevel0Dataset(Dataset[SeqColLevel0Model]):
    ...


class FastaTestDataRecord(pyd.BaseModel):
    name: str = ''
    top_level_digest: str = ''
    sorted_name_length_pairs_digest: str = ''
    level1: SeqColLevel1 = pyd.Field(default_factory=SeqColLevel1)
    level2: SeqColLevel2 = pyd.Field(default_factory=SeqColLevel2)


class AllSeqcolLevels(pyd.BaseModel):
    level_0: SeqColLevel0Model = pyd.Field(default_factory=SeqColLevel0Model)
    level_1: SeqColLevel1Model = pyd.Field(default_factory=SeqColLevel1Model)
    level_2: SeqColLevel2Model = pyd.Field(default_factory=SeqColLevel2Model)


class AllSeqcolLevelsModel(Model[AllSeqcolLevels]):
    ...


class AllSeqcolLevelsDataset(Dataset[AllSeqcolLevelsModel]):
    ...


class FastaTestDataModel(Model[FastaTestDataRecord]):
    ...


class FastaTestDataDataset(Dataset[FastaTestDataModel]):
    ...


class DigestCheck(pyd.BaseModel):
    seqcol_digest_level_0: bool = False
    sorted_name_length_pairs_digest: bool = False


class DigestCheckDataset(Dataset[Model[DigestCheck]]):
    ...


# Omnipy tasks and flows


@TaskTemplate(result_key='seqcol_digest_targets')
def fetch_seqcol_digest_targets(
        seqcol_digest_target_urls: HttpUrlDataset) -> SeqColDigestTargetDataset:
    seqcol_digest_target_file = JsonDictOfDictsDataset.load(
        seqcol_digest_target_urls, as_mime_type='application/json')

    return SeqColDigestTargetDataset({f['name']: f for f in seqcol_digest_target_file[0].values()})


@TaskTemplate(result_key='fasta_test_data')
def fetch_fasta_test_data(fasta_test_data_urls: HttpUrlDataset) -> FastaTestDataDataset:
    json_data = JsonDictDataset.load(fasta_test_data_urls, as_mime_type='application/json')
    return FastaTestDataDataset(**json_data[0])


@FuncFlowTemplate(result_key='fasta_checksums')
def fetch_fasta_checksums(
    owner: str,
    repo: str,
    branch: str,
    path: Path,
    seqcol_digest_targets: SeqColDigestTargetDataset,
) -> FastaChecksumDataset:

    fasta_checksum_urls = HttpUrlDataset()
    dir_path = path.parent

    quiet_get_github_repo_urls = get_github_repo_urls.refine(
        persist_outputs=PersistOutputsOptions.DISABLED)
    for target in seqcol_digest_targets.values():
        target_checksum_name = target.name + '.checksums'
        fasta_checksum_urls[target.name] = quiet_get_github_repo_urls(
            owner,
            repo,
            branch,
            dir_path / target_checksum_name,
        )[target_checksum_name]

    return FastaChecksumDataset.load(fasta_checksum_urls)


#TODO: Copy name of first argument of wrapped func when iterate_over_data_files=True, to not have to
#      set param_key_map in DAG flows
@TaskTemplate(
    iterate_over_data_files=True,
    param_key_map=dict(dataset='fasta_checksums'),
    result_key='seqcols_level_2',
)
def convert_fasta_checksums_to_seqcols_level_2(
    fasta_checksums: FastaChecksumModel,) -> SeqColLevel2Model:
    names: list[str] = []
    lengths: list[int] = []
    sequences: list[str] = []
    name_length_pairs = NameLengthPairListModel()

    for record in fasta_checksums:
        names.append(record.name)
        lengths.append(record.length)
        sequences.append(record.refget_digest)
        name_length_pairs.append(NameLengthPair(name=record.name, length=record.length))

    return SeqColLevel2Model(
        names=names,
        lengths=lengths,
        sequences=sequences,
        name_length_pairs=name_length_pairs,
    )


def ga4gh_digest(json_canon: bytes) -> str:
    sha512_hash = sha512(json_canon).digest()
    urlsafe_b64 = base64.urlsafe_b64encode(sha512_hash[:24])
    return urlsafe_b64.decode('ascii')


def calculate_seqcol_digest(obj: JSON) -> str:
    """Calculate the digest of a SeqCol."""
    json_canon = canonicalize(obj)
    return ga4gh_digest(json_canon)


def calculate_sorted_name_length_pairs_digest(name_length_pairs: NameLengthPairListModel) -> str:
    """Calculate the digest of a sorted name-length pairs."""
    sorted_name_length_pairs = sorted(
        calculate_seqcol_digest(name_length_pair.dict()) for name_length_pair in name_length_pairs)
    return calculate_seqcol_digest(cast(list, sorted_name_length_pairs))


@TaskTemplate(
    iterate_over_data_files=True,
    param_key_map=dict(dataset='fasta_test_data'),
    result_key='seqcols_level_2',
)
def extract_seqcol_level2_from_fasta_test_data(
    fasta_test_data: FastaTestDataRecord,) -> SeqColLevel2Model:
    return SeqColLevel2Model(fasta_test_data.level2)


@TaskTemplate(
    iterate_over_data_files=True,
    param_key_map=dict(dataset='seqcols_level_2'),
    result_key='seqcols_level_1',
)
def convert_seqcols_level2_to_level1(seqcols_level_2: SeqColLevel2) -> SeqColLevel1Model:
    return SeqColLevel1Model(
        names=calculate_seqcol_digest(cast(list, seqcols_level_2.names)),
        lengths=calculate_seqcol_digest(cast(list, seqcols_level_2.lengths)),
        sequences=calculate_seqcol_digest(cast(list, seqcols_level_2.sequences)),
        name_length_pairs=calculate_seqcol_digest(
            cast(dict, seqcols_level_2.name_length_pairs.to_data())),
        sorted_name_length_pairs=calculate_sorted_name_length_pairs_digest(
            seqcols_level_2.name_length_pairs),
        sorted_sequences=calculate_seqcol_digest(list(sorted(seqcols_level_2.sequences))),
    )


@TaskTemplate(
    iterate_over_data_files=True,
    param_key_map=dict(dataset='seqcols_level_1'),
    result_key='seqcols_level_0',
    output_type=SeqColLevel0Dataset,
)
def convert_seqcols_level1_to_level0(seqcols_level_1: SeqColLevel1) -> str:
    return calculate_seqcol_digest(
        cast(
            dict,
            SeqColLevel1InherentModel(
                names=seqcols_level_1.names,
                sequences=seqcols_level_1.sequences,
            ).to_data()))
    # return calculate_seqcol_digest(
    #     cast(
    #         dict,
    #         SeqColLevel1InherentModel(
    #             names=seqcol_level1.names,
    #             sequences=seqcol_level1.sequences,
    #         ).to_data()))


@TaskTemplate(result_key='seqcol_digests_on_target',)
def check_seqcol_digests(
    seqcols_level_0: SeqColLevel0Dataset,
    seqcols_level_1: SeqColLevel1Dataset,
    seqcol_digest_targets: SeqColDigestTargetDataset,
) -> DigestCheckDataset:
    return DigestCheckDataset({
        name: {
            'seqcol_digest_level_0':
                seqcols_level_0[name].content == seqcol_digest_targets[name].digest,
            'sorted_name_length_pairs_digest':
                seqcols_level_1[name].content ==
                seqcol_digest_targets[name].sorted_name_length_pairs_digest,
        } for name in seqcols_level_0
    })


@TaskTemplate()
def all_seqcol_levels(
    seqcols_level_0: SeqColLevel0Dataset,
    seqcols_level_1: SeqColLevel1Dataset,
    seqcols_level_2: SeqColLevel2Dataset,
) -> AllSeqcolLevelsDataset:
    return AllSeqcolLevelsDataset({
        key:
            AllSeqcolLevelsModel(
                level_0=seqcols_level_0[key],
                level_1=seqcols_level_1[key],
                level_2=seqcols_level_2[key],
            ) for key in seqcols_level_0.keys()
    })


@DagFlowTemplate(
    get_github_repo_urls.refine(result_key='fasta_test_data_urls'),
    fetch_fasta_test_data,
    extract_seqcol_level2_from_fasta_test_data,
    convert_seqcols_level2_to_level1,
    convert_seqcols_level1_to_level0,
    all_seqcol_levels,
)
def seqcol_digest_check(owner: str, repo: str, branch: str, path: Path) -> AllSeqcolLevelsDataset:
    ...
