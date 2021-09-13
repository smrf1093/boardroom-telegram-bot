FROM python:3.8
RUN apt update -y && apt install libpq-dev python3-dev -y
ENV PYTHONUNBUFFERED=1

RUN mkdir /code
WORKDIR /code

COPY . /code/
RUN pip install "poetry==1.1.7"
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-ansi