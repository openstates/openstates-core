FROM python:3.13-slim
LABEL maintainer="Jesse Mortenson <Jesse.Mortenson@sai360.com>"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONIOENCODING='utf-8'
ENV LANG='C.UTF-8'

# text extraction stuff
# install git for forked dependency re: scrapelib
# and gitPython uses it
RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends \
      libgdal-dev \
      poppler-utils \
      antiword \
      tesseract-ocr \
      git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/os

# use the image's python rather than downloading the one pinned in .python-version
ENV UV_PYTHON=/usr/local/bin/python3
ENV UV_PYTHON_DOWNLOADS=never
ENV UV_NO_CACHE=1
COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /uvx /bin/

WORKDIR /opt/os
ADD pyproject.toml /opt/os/
ADD uv.lock /opt/os/
ADD .python-version /opt/os/
RUN uv sync -q --locked --no-install-project \
    && apt-get autoremove -y -qq \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ADD . /opt/os
RUN uv sync -q --locked

# deps are baked in above; skip re-syncing on every `uv run`
ENV UV_NO_SYNC=1

ENTRYPOINT ["uv", "run"]