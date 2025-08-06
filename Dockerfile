FROM python:3.12-bookworm
WORKDIR /app

RUN apt-get update && apt-get install -y build-essential
RUN pip3 install poetry

COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root --no-directory

COPY . .

CMD ["./entrypoint.sh"]

EXPOSE 8000