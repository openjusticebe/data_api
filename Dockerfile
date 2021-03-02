FROM python:3.8-slim-buster

ARG ENV="dev"
ENV ENV=${ENV} \
  PG_DSN=${PG_DSN} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.1.4

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y \
    pandoc \
    texlive \
    texlive-latex-extra 

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app
COPY poetry.lock pyproject.toml /app/
COPY . /app
RUN poetry config virtualenvs.create false && \
    poetry install $(test $ENV == "prod" && echo "--no-dev") --no-interaction --no-ansi


EXPOSE 5000
ENTRYPOINT ["poetry", "run", "api"]
