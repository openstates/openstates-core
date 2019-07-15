FROM  ubuntu:bionic
LABEL maintainer="James Turk <james@openstates.org>"

ENV PYTHONIOENCODING 'utf-8'
ENV LANG 'C.UTF-8'
ENV LC_ALL 'C.UTF-8'

ADD . /opt/text-extraction
WORKDIR /opt/text-extraction

RUN apt update && \
        apt install -y software-properties-common libgdal20 poppler-utils && \
        add-apt-repository ppa:deadsnakes/ppa && \
        apt install -y python3-pip python3.7 && \
        pip3 install pipenv
RUN pipenv install

ENTRYPOINT ["pipenv", "run", "python", "./text_extract.py"]
