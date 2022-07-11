FROM python:3.9-slim
LABEL maintainer="James Turk <dev@jamesturk.net>"

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONIOENCODING 'utf-8'
ENV LANG 'C.UTF-8'

# text extraction stuff
# install git for forked dependency re: scrapelib
RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends \
      libgdal-dev \
      poppler-utils \
      antiword \
      tesseract-ocr \
      git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ADD pyproject.toml /opt/os
ADD poetry.lock /opt/os
WORKDIR /opt/os
RUN pip --no-cache-dir --disable-pip-version-check install poetry \
    && poetry install -q --no-root \
    && apt-get -y -qq remove \
      git \
    && apt-get autoremove -y -qq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ADD . /opt/os
RUN poetry install -q \
    && rm -r /root/.cache/pypoetry/cache /root/.cache/pypoetry/artifacts/ \

ENTRYPOINT ["poetry", "run"]
