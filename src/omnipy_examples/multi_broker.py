from typing import Callable, Optional, TypeAlias

from omnipy.modules.json.datasets import JsonDataset
from omnipy.modules.json.models import JsonModel
from pydantic import BaseModel

IsaJsonModel: TypeAlias = JsonModel
IsaJsonDataset: TypeAlias = JsonDataset
ExtendedIsaJsonDataset: TypeAlias = JsonDataset

JsonPath: TypeAlias = str


class FilteringRule(BaseModel):
    key: JsonPath
    value: str


class TargetRepository(BaseModel):
    name: str
    api_url: str
    filtering_rules: list[FilteringRule]
    file_submitter: Optional[Callable]


TargetRepository(
    name='ENA',
    api_url='https://oajsfkjas',
    filtering_rules=[
        FilteringRule(
            key='investigation.studies.assays.technologyType.annotationValue',
            value='nucleotide sequencing')
    ],
    file_submitter=None)


class Credential(BaseModel):
    token: str


def broker_isa_json_to_multi_repos(dataset: IsaJsonDataset,
                                   target_repositories: list[TargetRepository],
                                   credentials: Credential) -> ExtendedIsaJsonDataset:
    ...
