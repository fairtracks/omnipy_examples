FROM prefecthq/prefect:2-latest

RUN pip install omnipy_examples
RUN set -eux; \
	apt-get install -y locales
RUN set -eux; \
    echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen; \
    echo "de_DE.UTF-8 UTF-8" >> /etc/locale.gen; \
    locale-gen; \
    update-locale en_us.UTF-8
