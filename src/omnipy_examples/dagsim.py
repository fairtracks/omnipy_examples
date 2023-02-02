from omnipy.compute.flow import LinearFlowTemplate
from omnipy.modules.general.tasks import import_directory
from omnipy.modules.json.datasets import JsonDictOfDictsOfAnyDataset
from omnipy.modules.raw.tasks import modify_datafile_contents

# from omnipy.modules.r_stat import r

# Regex patterns for parsing
#     variable_pattern = re.compile(r"  type discrete \[ \d+ \] \{ (.+) \};\s*")
#     prior_probability_pattern_1 = re.compile(
#         r"probability \( ([^|]+) \) \{\s*")
#     prior_probability_pattern_2 = re.compile(r"  table (.+);\s*")
#     conditional_probability_pattern_1 = (
#         re.compile(r"probability \( (.+) \| (.+) \) \{\s*"))
#     conditional_probability_pattern_2 = re.compile(r"  \((.+)\) (.+);\s*")

# @TaskTemplate
# def import_dag_from_bnlearn(dag_name: str):
#     r('chooseCRANmirror(ind = 1)')
#     r('install.binaries("bnlearn")')
#     r('library(bnlearn)')
#     # r('install.packages("https://www.bnlearn.com/releases/bnlearn_latest.tar.gz", '
#     #   'repos = NULL, type = "source")')


def convert_to_json(contents: str, **kwargs: object):
    contents = contents.replace('\n', '')
    return f'"{contents}"'


@LinearFlowTemplate(
    import_directory.refine(
        name='import_and_convert_bif_files_to_json',
        fixed_params=dict(include_suffixes=('.bif',)),
    ),
    modify_datafile_contents.refine(
        name='modify_bif_files',
        fixed_params=dict(modify_contents_func=convert_to_json),
    ),
)
def import_and_convert_bif_files_to_json(dir_path: str) -> JsonDictOfDictsOfAnyDataset:
    ...
