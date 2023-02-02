# omnipy-examples

Example projects that that makes use of the omnipy package for type-driven, scalable and interoperable data wrangling!

## Main installation instructions

- Install Poetry:
  - `curl -sSL https://install.python-poetry.org | python3 -`
- Install Python 3.10 through e.g. Conda, or directly in your IDE:
  - `conda create -env myenv python=3.10`
  - `conda activate myenv`
- Install dependencies
  - `poetry install`
- Run example scripts
  - `scripts/uniprot_example` or `python scripts/uniprot_example.py`
- Output will appear in the `data` directory with a timestamp. 
  - It is recommended to install a file viewer that are capable of browsing tar.gz files. For instance, the "File Expander" plugin in PyCharm is 
    excellent for this

### Development setup

- Install dependencies:
  - `poetry install --with dev`

## For mypy support in PyCharm

- In PyCharm, install "Mypy" plugin (not "Mypy (Official)")
  - `which mypy` to get path to mypy binary
  - In the PyCharm settings for the mypy plugin:
    - Select the mypy binary 
    - Select `pyproject.toml` as the mypy config file

## For automatic formatting and linting

I have added my typical setup for automatic formatting and linting. The main alternative is to use black, which is easier to set up, but it does 
not have as many options. I am not fully happy with my config, but I at least like it better than black. 

- In PyCharm -> File Watchers:
  - Click arrow down icon
  - Select `watchers.xml`
