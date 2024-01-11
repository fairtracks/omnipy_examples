from pathlib import Path
from subprocess import call

import pytest

TESTABLE_COMMANDS = [
    'dagsim',
    'encode',
    'gff',
    'isajson',
    'uniprot',
]


@pytest.mark.parametrize("command", TESTABLE_COMMANDS)
def test_invoke_all_testable_examples(command: str):
    return_code = call(
        f'python {Path(__file__).parent.parent.joinpath('src/omnipy_examples/main.py')} {command}',
        shell=True)
    assert return_code == 0
