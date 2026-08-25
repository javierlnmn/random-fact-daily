FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.12.5 /uv /bin/uv

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/app/.venv/bin:$PATH

RUN apt-get update && apt-get install -y --no-install-recommends \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

RUN playwright install --with-deps chromium

COPY . .

# Placeholders that only let the Django checks pass during the build
RUN export SECRET_KEY=build CSRF_TRUSTED_ORIGINS=http://build \
    && python manage.py tailwind install \
    && python manage.py tailwind build \
    && python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && gunicorn randomfactdaily.wsgi:application --bind 0.0.0.0:8000 --workers 1 --threads 2"]
