FROM python:3.12-slim as builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV POETRY_VERSION=1.7.1
RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /app
COPY pyproject.toml poetry.lock ./
COPY croco-reviewer/croco_reviewer ./croco-reviewer/croco_reviewer

RUN poetry config virtualenvs.in-project true && \
    poetry install --only main --no-interaction --no-ansi

FROM python:3.12-slim

# Копируем виртуальное окружение из builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Копируем исходный код
WORKDIR /app
COPY --from=builder /app/croco-reviewer/croco_reviewer ./croco-reviewer/croco_reviewer

# Указываем порт и команду для запуска
EXPOSE 8000
CMD ["uvicorn", "croco-reviewer.croco_reviewer.main:app", "--host", "0.0.0.0", "--port", "8000"]