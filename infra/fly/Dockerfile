FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    PORT=8080 \
    DJANGO_ENV=production

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="/root/.local/bin:${PATH}"

COPY pyproject.toml uv.lock README.md ./
COPY manage.py ./
COPY config ./config
COPY apps ./apps
COPY packages ./packages
COPY templates ./templates
COPY static ./static
COPY media ./media
COPY infra/fly/entrypoint.sh /entrypoint.sh

RUN sed -i 's/\r$//' /entrypoint.sh \
    && chmod +x /entrypoint.sh \
    && uv sync --frozen --no-dev \
    && uv run python -c "import django; print(django.get_version())"

EXPOSE 8080
ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]
