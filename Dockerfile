FROM python:3.8

ENV PYTHONUNBUFFERED=1

RUN mkdir /code
WORKDIR /code

COPY pyproject.toml /code/
COPY poetry.lock /code/
RUN pip install "poetry==1.1.7"
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi

COPY . /code/