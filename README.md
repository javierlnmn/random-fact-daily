# Random Fact Daily

A Django site that shows a random fact every day.

The facts come from public web pages. A management command scrapes them into the
database. An extractor reads one site, a formatter cleans the text, and a
storage class writes the result. See
[Scraping](#scraping) for more info.

## Development

Run it on the host machine. No Docker.

```sh
uv sync
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

The container runs `migrate` and then gunicorn.

## Scraping

`manage.py scrape_facts` takes an extractor and a storage class, both by class
name:

```sh
uv run python manage.py scrape_facts ScienceFocus121FactsExtractor DBStorage
```

In the container:

```sh
docker exec random-fact-daily python manage.py scrape_facts ScienceFocus121FactsExtractor DBStorage
```

Extractors, from `facts/scraping/extractors/`:

| Class | Needs Chromium |
| --- | --- |
| `ScienceFocus121FactsExtractor` | no |
| `TodayInterestingFactsAdultsExtractor` | no |
| `HooRayHeroesAnimalsFunFactsExtractor` | yes |
| `HooRayHeroesMythBustingFunFactsExtractor` | yes |

`DBStorage` is the only storage class.

Options:

| Option | Effect |
| --- | --- |
| `--formatter <Class>` | Use `DefaultFactFormatter` or `HoorayHeroesFactFormatter` instead of the extractor default. |
| `--override` | Replace facts whose identifier already exists. |
| `--delete` | Delete the scraped facts instead of saving them. `--override` is ignored. |

The two HooRayHeroes extractors drive a headless browser with playwright. The
image installs Chromium during the build. On the host, install it once:

```sh
uv run playwright install chromium
```
