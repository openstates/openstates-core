FROM python:3.9-slim
LABEL maintainer="James Turk <dev@jamesturk.net>"

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONIOENCODING 'utf-8'
ENV LANG 'C.UTF-8'
ENV PYTHONPATH ${PYTHONPATH}:.:/opt/os



# text extraction stuff
RUN apt update && apt install -y --no-install-recommends \
      libgdal-dev \
      poppler-utils \
      antiword \
      tesseract-ocr \
      git # install git for forked dependency re: scrapelib

ADD . /opt/os
WORKDIR /opt/os
RUN set -ex \
    && pip install poetry \
    && poetry install

ENTRYPOINT ["poetry", "run"]
