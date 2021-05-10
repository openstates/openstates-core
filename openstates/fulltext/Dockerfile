FROM python:3.7-slim
LABEL maintainer="James Turk <james@openstates.org>"

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONIOENCODING 'utf-8'
ENV LANG 'C.UTF-8'

RUN apt update && apt install -y --no-install-recommends \
      libgdal-dev \
      poppler-utils \
      antiword \
      tesseract-ocr

ADD . /opt/text-extraction
WORKDIR /opt/text-extraction
RUN set -ex \
    && pip install poetry \
    && poetry install

ENTRYPOINT ["poetry", "run", "python", "./text_extract.py"]
