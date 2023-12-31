FROM python:3.10.11-alpine

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.2.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1

RUN apk update && apk add --no-cache \
            --allow-untrusted \
            --repository \
            http://dl-3.alpinelinux.org/alpine/edge/testing \
            hdf5 \
            hdf5-dev \
            build-base

RUN pip install tensorflow-io-gcs-filesystem

RUN pip install "poetry==$POETRY_VERSION"

COPY poetry.lock pyproject.toml /src/
WORKDIR /src

RUN poetry config virtualenvs.create false && poetry install --no-dev --no-ansi

RUN apk --no-cache del build-base

COPY . /src
