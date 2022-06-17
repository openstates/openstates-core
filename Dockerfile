FROM python:3.9-slim
LABEL maintainer="James Turk <dev@jamesturk.net>"

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONIOENCODING 'utf-8'
ENV LANG 'C.UTF-8'

# text extraction stuff
RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends \
      libgdal-dev \
      poppler-utils \
      antiword \
      tesseract-ocr \
      git # install git for forked dependency re: scrapelib

ADD . /opt/os
WORKDIR /opt/os
RUN pip --no-cache-dir --disable-pip-version-check install poetry \
    && poetry install \
    && rm -r /root/.cache/pypoetry/cache /root/.cache/pypoetry/artifacts/

ENTRYPOINT ["poetry", "run"]
