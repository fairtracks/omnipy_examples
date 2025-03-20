from textwrap import dedent
from typing import Annotated, TypeAlias

from omnipy_examples.seqcol import (convert_fasta_checksums_to_seqcols_level_2,
                                    convert_seqcols_to_level_0,
                                    convert_seqcols_to_level_1,
                                    FastaChecksumDataset,
                                    FastaChecksumModel,
                                    SeqColLevel1Dataset,
                                    SeqColLevel2,
                                    SeqColLevel2Dataset,
                                    SeqColLevel2Model)
import pytest

FastaChecksumType: TypeAlias = list[dict[str, int | str]]
SeqColsLevel2Type: TypeAlias = dict[str, list[str | int | dict[str, int | str]]]
SeqColsLevel1Type: TypeAlias = dict[str, str]


@pytest.fixture()
def fasta_checksums_example() -> FastaChecksumType:
    return [
        {
            'name': 'chr1',
            'length': 248956422,
            'refget_digest': 'SQ.2YnepKM7OkBoOrKmvHbGqguVfF9amCST',
            'md5_digest': '.'
        },
        {
            'name': 'chr2',
            'length': 242193529,
            'refget_digest': 'SQ.lwDyBi432Py-7xnAISyQlnlhWDEaBPv2',
            'md5_digest': '.'
        },
        {
            'name': 'chr3',
            'length': 198295559,
            'refget_digest': 'SQ.Eqk6_SvMMDCc6C-uEfickOUWTatLMDQZ',
            'md5_digest': '.'
        },
    ]


@pytest.fixture()
def seqcols_example_level_2() -> SeqColsLevel2Type:
    return {
        'names': ['chr1', 'chr2', 'chr3'],
        'lengths': [248956422, 242193529, 198295559],
        'sequences': [
            'SQ.2YnepKM7OkBoOrKmvHbGqguVfF9amCST',
            'SQ.lwDyBi432Py-7xnAISyQlnlhWDEaBPv2',
            'SQ.Eqk6_SvMMDCc6C-uEfickOUWTatLMDQZ'
        ],
        'name_length_pairs': [{
            'name': 'chr1', 'length': 248956422
        }, {
            'name': 'chr2', 'length': 242193529
        }, {
            'name': 'chr3', 'length': 198295559
        }]
    }


@pytest.fixture()
def seqcols_example_level_1() -> SeqColsLevel1Type:
    return {
        'lengths': '5K4odB173rjao1Cnbk5BnvLt9V7aPAa2',
        'names': 'g04lKdxiYtG3dOGeUC5AdKEifw65G0Wp',
        'sequences': 'rD29ZKmEqwwHRXjiQ36p6UMZQ5hemmsb',
        'name_length_pairs': 'UehRI2awhWecANdwztdiIGPXv8xkHggG',
        'sorted_name_length_pairs': 'ydhV5UJwuvk3o1ygTJljBrzhyUI8stjc',
        'sorted_sequences': 'H7oLHTWQmNjnMNf6P7fZQxDlr66GKYVg',
    }


def test_fasta_checksum_model(
        fasta_checksums_example: Annotated[FastaChecksumType, pytest.fixture]) -> None:
    input_data = dedent("""\
    chr1\t248956422\tSQ.2YnepKM7OkBoOrKmvHbGqguVfF9amCST\t.
    chr2\t242193529\tSQ.lwDyBi432Py-7xnAISyQlnlhWDEaBPv2\t.
    chr3\t198295559\tSQ.Eqk6_SvMMDCc6C-uEfickOUWTatLMDQZ\t.
    """)

    fasta_checksums = FastaChecksumModel(input_data)

    # Check that the model has the expected attributes
    assert fasta_checksums.to_data() == fasta_checksums_example


def test_convert_fasta_checksums_to_seqcols_level_2(
    fasta_checksums_example: Annotated[FastaChecksumType, pytest.fixture],
    seqcols_example_level_2: Annotated[SeqColsLevel2Type, pytest.fixture],
) -> None:

    fasta_checksums = FastaChecksumDataset(example=fasta_checksums_example)
    seqcols = convert_fasta_checksums_to_seqcols_level_2.run(fasta_checksums)['seqcols_level_2']

    assert seqcols['example'].to_data() == seqcols_example_level_2


def test_convert_seqcols_to_level_1(
    seqcols_example_level_2: Annotated[SeqColsLevel2Type, pytest.fixture],
    seqcols_example_level_1: Annotated[SeqColsLevel1Type, pytest.fixture],
) -> None:
    seqcols_level_2 = SeqColLevel2Dataset(example=seqcols_example_level_2)
    seqcols_level_1 = convert_seqcols_to_level_1.run(seqcols_level_2)['seqcols_level_1']
    assert seqcols_level_1['example'].to_data() == seqcols_example_level_1


def test_convert_seqcols_to_level_0(
        seqcols_example_level_1: Annotated[SeqColsLevel1Type, pytest.fixture]) -> None:
    seqcols_level_1 = SeqColLevel1Dataset(example=seqcols_example_level_1)
    seqcols_level_0 = convert_seqcols_to_level_0.run(seqcols_level_1)['seqcols_level_0']
    assert seqcols_level_0['example'].to_data() == 'sjNNwm4zov3Dl0FRWbRTcZwzqrTQKIqL'
