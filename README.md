# omnipy-examples

Example projects that that makes use of the [omnipy](https://pypi.org/project/omnipy/) package for 
type-driven, scalable and interoperable data wrangling!

## Main installation instructions

- Install:
  - `pip install omnipy-examples`
- Run example scripts:
  - Example: `omnipy-examples isajson`
  - For help on the command line interface: `omnipy-examples --help`
  - For help on a particular example: `omnipy-examples isajson --help`

### Output of flow runs

The output will by default appear in the `data` directory, with a timestamp. 

  - It is recommended to install a file viewer that are capable of browsing tar.gz files. 
    For instance, the "File Expander" plugin in PyCharm is excellent for this.
  - To unpack the compressed files of a run on the command line 
    (just make sure to replace the datetime string from this example): 

```
for f in $(ls data/2023_02_03-12_51_51/*.tar.gz); do mkdir ${f%.tar.gz}; tar xfzv $f -C ${f%.tar.gz}; done
```
    
### Run with the Prefect engine

Omnipy is integrated with the powerful [Prefect](https://prefect.io) data flow orchestration library.

- To run an local example using the `prefect` engine, e.g.:
  - `omnipy-examples --engine prefect isajson`
- After completion of some runs, you can check the flow logs and orchestration options in the Prefect UI:
  - `prefect server start`

To set up a kubernetes-based deployment on our NIRD test setup, run e.g.:

- `prefect config set PREFECT_API_URL=https://prefect.fairtracks.sigma2.no/api`
- `prefect deploy -n isajson`

The configuration of this job is found in the file `prefect.yaml`. 

More info on Prefect configuration will come soon...

## Development setup

- Install Poetry:
  - `curl -sSL https://install.python-poetry.org | python3 -`

- Install dependencies:
  - `poetry install --with dev`

- Update all dependencies:
  - `poetry update`

- Update single dependency, e.g.:
  - `poetry update omnipy`

- If a dependency is not updated to the latest version available on Pypi, you might need to clear
  the pip cache of poetry:
  - `poetry cache clear pypi --all`

### For mypy support in PyCharm

- In PyCharm, install "Mypy" plugin (not "Mypy (Official)")
  - `which mypy` to get path to mypy binary
  - In the PyCharm settings for the mypy plugin:
    - Select the mypy binary 
    - Select `pyproject.toml` as the mypy config file

### For automatic formatting and linting

I have added my typical setup for automatic formatting and linting. The main alternative is to use black, which is easier to set up, but it does 
not have as many options. I am not fully happy with my config, but I at least like it better than black. 

- In PyCharm -> File Watchers:
  - Click arrow down icon
  - Select `pycharm-file-watchers.xml`


```
[OMNIPY]  Tue Aug 27 15:39:30 2024 - INFO: Finished running "task-transpose-dicts-2-lists-annoying-wombat"! [omnipy.log.registry.RunStateRegistry]
[OMNIPY]  Tue Aug 27 15:39:30 2024 - INFO: Writing dataset as a gzipped tarpack to "/Users/sveinugu/PycharmProjects/omnipy_examples/outputs/2024_08_27-15_39_30/02_task_transpose_dicts_2_lists.tar.gz" [omnipy.compute.task.TaskWithMixins]
[OMNIPY]  Tue Aug 27 15:39:30 2024 - INFO: Finished running "func-flow-transpose-dicts-of-lists-of-dicts-2-lists-of-dicts-banana-antelope"! [omnipy.log.registry.RunStateRegistry]
[OMNIPY]  Tue Aug 27 15:39:30 2024 - INFO: Writing dataset as a gzipped tarpack to "/Users/sveinugu/PycharmProjects/omnipy_examples/outputs/2024_08_27-15_39_30/03_func_flow_transpose_dicts_of_lists_of_dicts_2_lists_of_dicts.tar.gz" [omnipy.compute.flow.FuncFlowWithMixins]
[OMNIPY]  Tue Aug 27 15:39:30 2024 - INFO: Initialized "func-flow-flatten-nested-json-incredible-bobcat" [omnipy.log.registry.RunStateRegistry]
[OMNIPY]  Tue Aug 27 15:39:30 2024 - INFO: Started running "func-flow-flatten-nested-json-incredible-bobcat"... [omnipy.log.registry.RunStateRegistry]
[OMNIPY]  Tue Aug 27 15:39:30 2024 - INFO: Initialized "task-flatten-outer-level-of-all-data-files-axiomatic-ape" [omnipy.log.registry.RunStateRegistry]
[OMNIPY]  Tue Aug 27 15:39:30 2024 - INFO: Started running "task-flatten-outer-level-of-all-data-files-axiomatic-ape"... [omnipy.log.registry.RunStateRegistry]
[OMNIPY]  Tue Aug 27 15:39:30 2024 - INFO: Finished running "task-flatten-outer-level-of-all-data-files-axiomatic-ape"! [omnipy.log.registry.RunStateRegistry]
```