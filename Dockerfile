FROM python:3.12.7-alpine

ENV PYTHONUNBUFFERED 1
WORKDIR /app

COPY pyproject.toml .
COPY uv.lock .
RUN pip install --no-cache-dir uv
RUN uv sync

COPY . .

ADD .env.docker /app/.env

RUN uv run alembic upgrade head

CMD uv run gunicorn main:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 --workers 8
