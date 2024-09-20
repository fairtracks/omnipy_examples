ARG PREFECT_VERSION=2.20.7
ARG PYTHON_VERSION=3.12

FROM prefecthq/prefect:$PREFECT_VERSION-python$PYTHON_VERSION-kubernetes

RUN pip install omnipy_examples
# RUN pip uninstall omnipy_examples -y
RUN set -eux; \
	apt-get update; \
	apt-get install -y --no-install-recommends \
            locales; \
            apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
	        rm -rf /var/lib/apt/lists/*;
RUN set -eux; \
    echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen; \
    echo "de_DE.UTF-8 UTF-8" >> /etc/locale.gen; \
    locale-gen; \
    update-locale en_us.UTF-8;
RUN ln -sf /usr/local/lib/python$PYTHON_VERSION/site-packages /opt/prefect/src
