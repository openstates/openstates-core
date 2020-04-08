FROM python:3.7

RUN apt update && apt install -y libgdal-dev
RUN pip install poetry

ADD . /opt/openstates-core
WORKDIR /opt/openstates-core
RUN poetry install

ENTRYPOINT ["poetry", "run"]
