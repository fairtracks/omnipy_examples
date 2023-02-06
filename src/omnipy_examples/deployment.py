from omnipy import runtime
from omnipy_examples.main import isajson
from prefect import flow as prefect_flow


@prefect_flow
def isajson_prefect():
    runtime.config.engine = 'prefect'
    isajson()
