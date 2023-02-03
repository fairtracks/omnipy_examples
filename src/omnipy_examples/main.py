import importlib
from pathlib import Path

from omnipy import runtime
from omnipy.api.enums import ConfigPersistOutputsOptions, ConfigRestoreOutputsOptions, EngineChoice
import typer

app = typer.Typer()


def get_path_to_example_data() -> Path:
    ref = importlib.resources.files('omnipy_example_data')
    path: Path
    with importlib.resources.as_file(ref) as path:
        return path.resolve()


installed_example_data_path = get_path_to_example_data()


@app.command()
def dagsim(input_dir: str = installed_example_data_path.joinpath('bif')):
    from omnipy_examples.dagsim import import_and_convert_bif_files_to_json
    import_and_convert_bif_files_to_json.run(input_dir)


@app.command()
def encode():
    from omnipy_examples.encode import import_and_flatten_encode_data
    import_and_flatten_encode_data.run()


@app.command()
def gff(input_dir: str = installed_example_data_path.joinpath('gff')):
    from omnipy_examples.gff import import_gff_as_pandas
    import_gff_as_pandas.run(input_dir)


@app.command()
def isajson(input_dir: str = installed_example_data_path.joinpath('isa-json')):
    from omnipy_examples.isajson import convert_isa_json_to_relational_tables
    convert_isa_json_to_relational_tables.run(input_dir)


@app.command()
def uniprot():
    from omnipy_examples.uniprot import import_and_flatten_uniprot_with_magic
    import_and_flatten_uniprot_with_magic.run()


@app.callback()
def main(output_dir: str = runtime.config.job.persist_data_dir_path,
         engine: EngineChoice = 'local',
         persist_outputs: ConfigPersistOutputsOptions = 'all',
         restore_outputs: ConfigRestoreOutputsOptions = 'disabled'):

    runtime.config.engine = engine
    runtime.config.job.persist_data_dir_path = output_dir
    runtime.config.job.persist_outputs = persist_outputs
    runtime.config.job.restore_outputs = restore_outputs


if __name__ == "__main__":
    app()
