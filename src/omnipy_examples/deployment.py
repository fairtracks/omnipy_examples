from omnipy import runtime
from omnipy_examples.main import chatgpt, dagsim, encode, gff, isajson, uniprot
from prefect import flow as prefect_flow

runtime.config.engine = 'prefect'
runtime.config.data.interactive_mode = False


@prefect_flow
def dagsim_prefect():
    dagsim()


@prefect_flow
def encode_prefect():
    encode()


@prefect_flow
def gff_prefect():
    gff()


@prefect_flow
def isajson_prefect():
    isajson()


@prefect_flow
def uniprot_prefect():
    uniprot()


@prefect_flow
def chatgpt_prefect():
    chatgpt()


uniprot_prefect()

# isajson_prefect.deploy(
#     'isajson', work_pool_name='kubernetes-agent', image='fairtracks/omnipy-examples:latest')
#
# if __name__ == "__main__":
#     isajson_prefect.serve(name="isajson-prefect-deployment")
