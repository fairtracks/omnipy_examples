from omnipy import runtime
from omnipy_examples.main import chatgpt, dagsim, encode, gff, isajson, uniprot
from prefect import flow as prefect_flow


@prefect_flow
def dagsim_prefect():
    runtime.config.engine = 'prefect'
    dagsim()


@prefect_flow
def encode_prefect():
    runtime.config.engine = 'prefect'
    encode()


@prefect_flow
def gff_prefect():
    runtime.config.engine = 'prefect'
    gff()


@prefect_flow
def isajson_prefect():
    runtime.config.engine = 'prefect'
    isajson()


@prefect_flow
def uniprot_prefect():
    runtime.config.engine = 'prefect'
    uniprot()


@prefect_flow
def chatgpt_prefect():
    runtime.config.engine = 'prefect'
    chatgpt()


# isajson_prefect.deploy(
#     'isajson', work_pool_name='kubernetes-agent', image='fairtracks/omnipy-examples:latest')
#
# if __name__ == "__main__":
#     isajson_prefect.serve(name="isajson-prefect-deployment")
