FROM prefecthq/prefect:2-latest

RUN pip install omnipy_examples
RUN sudo locale-gen de_DE.UTF-8 && sudo locale-gen en_US.UTF-8 && sudo update-locale LANG=en_US.UTF-8
