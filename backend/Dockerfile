FROM python:3.12.2

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV POETRY_VERSION=1.3.1
ENV PYTHONPATH "${PYTHONPATH}:/code"

RUN pip install pandas "poetry==$POETRY_VERSION"

WORKDIR /code
COPY . /code

RUN apt update -y && apt install ffmpeg -y

RUN poetry config installer.max-workers 10
RUN poetry install --no-dev --no-interaction --no-ansi
