# Random Fact Daily

A random fact every day.

## Development

Run it on the host machine. No Docker.

```sh
uv sync
uv run playwright install chromium   # only for manage.py scrape_facts
uv run python manage.py tailwind install
uv run python manage.py migrate
```

Then start two processes:

```sh
uv run python manage.py tailwind start
uv run python manage.py runserver
```

## Production

One image, no Docker Compose. The `.env` file stays out of the image and is
given at run time.

```sh
docker build -t random-fact-daily .

docker run -d --name random-fact-daily \
  --env-file .env \
  -p 8000:8000 \
  -v random-fact-daily-db:/app/db \
  --memory=384m --cpus=0.5 \
  --restart unless-stopped \
  random-fact-daily
```

The container runs `migrate` and then gunicorn. Static files are built during
the image build and served by whitenoise.

Scrape facts:

```sh
docker exec random-fact-daily python manage.py scrape_facts
```
