from omnipy import runtime
from omnipy_examples.main import chatgpt, isajson
from prefect import flow as prefect_flow


@prefect_flow
def isajson_prefect():
    runtime.config.engine = 'prefect'
    isajson()


@prefect_flow
def chatgpt_prefect():
    runtime.config.engine = 'prefect'
    chatgpt()


# isajson_prefect.deploy(
#     'isajson', work_pool_name='kubernetes-agent', image='fairtracks/omnipy-examples:latest')
#
# if __name__ == "__main__":
#     isajson_prefect.serve(name="isajson-prefect-deployment")
