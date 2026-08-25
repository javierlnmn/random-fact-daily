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

To run the app, use Docker Compose to execute the two services, both from the same image:

- `web` applies the migrations, registers the daily schedule, then serves the
  site with gunicorn on port 8000.
- `qcluster` runs the Django Q worker, which picks the fact of the day at
  midnight.

To build and run:

```sh
cp .env.example .env   # then set the real values
docker compose up -d --build
```

## Scraping

`manage.py scrape_facts` takes an extractor and a storage class, both by class
name:

```sh
uv run python manage.py scrape_facts ScienceFocus121FactsExtractor DBStorage
```

In the container:

```sh
docker compose exec web python manage.py scrape_facts ScienceFocus121FactsExtractor DBStorage
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
