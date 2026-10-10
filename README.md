# Europa Universalis IV Achievement Tracker

A small, self-contained tracker for **Europa Universalis IV** achievements. A Python pipeline collects achievement data from Steam and the community wiki, merges it into a single dataset, and generates a standalone HTML page for browsing and tracking achievements.

> Unofficial fan project. Not affiliated with or endorsed by Paradox Interactive or Valve. Europa Universalis IV and its achievements are the property of their respective owners.

<!-- TODO: add a screenshot or GIF of the tracker page here, e.g. ![Tracker screenshot](docs/screenshot.png) -->

## Features

<!-- VERIFY: keep only the features that the page really has, and add the ones that are missing -->

- Complete list of EU4 achievements with their descriptions and requirements
- Data from two sources (Steam and the wiki) merged into one dataset
- Single static HTML file: no server, database or build step needed to use it
- Reproducible data pipeline: rerun the scripts to refresh the data after a new DLC or patch

## How it works

```
steam.html ─┐
            ├─> scrape.py ──> achievements.json ──> full_builder.py ──> eu4_achievement_tracker_steam.html
wiki.html  ─┘
```

<!-- VERIFY: confirm this flow. Does scrape.py read the saved steam.html / wiki.html files or download the pages itself? Does full_builder.py write the final HTML? -->

1. **Collect:** `scrape.py` extracts achievement data from the Steam achievements page and the wiki page.
2. **Merge & build:** `full_builder.py` combines the data and produces the final tracker page.
3. **Use:** open `eu4_achievement_tracker_steam.html` in a browser.

## Repository structure

| File | Purpose |
| --- | --- |
| `scrape.py` | Extracts achievement data from the source pages |
| `full_builder.py` | Builds the final dataset / HTML tracker |
| `achievements.json` | Collected achievement data |
| `eu4_achievement_tracker_steam.html` | The generated, standalone tracker page |

<!-- VERIFY: correct the descriptions above if any file does something different -->

## Getting started

### Just use the tracker

Open `eu4_achievement_tracker_steam.html` in any modern browser.

### Rebuild the data

Requirements: Python 3.10+ and the packages used by the scripts.

```bash
git clone https://github.com/thatsalgoritma/Europa-Universalis-4-Achievement-Tracker.git
cd Europa-Universalis-4-Achievement-Tracker

# <!-- VERIFY: list the real dependencies, e.g. requests, beautifulsoup4, and add a requirements.txt -->
pip install -r requirements.txt

python scrape.py
python full_builder.py
```

## Tech stack

- Python (data collection and generation)
- HTML, CSS, JavaScript (tracker interface)
- JSON (data format)

<!-- VERIFY: add libraries you actually used (e.g. BeautifulSoup, requests) -->

## Notes on data sources

Achievement names and descriptions come from Steam and the community wiki. Please respect the terms of use and robots rules of these sites when refreshing the data, and avoid sending frequent automated requests.

## Roadmap


## License
