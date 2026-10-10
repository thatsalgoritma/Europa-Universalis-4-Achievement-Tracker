# Europa Universalis IV Achievement Tracker

A standalone, offline-friendly tracker for **Europa Universalis IV** achievements. A Python script merges achievement details from the community wiki with global unlock rates from Steam and generates a single HTML page where you can track your own progress, filter by difficulty, and sort by how rare each achievement is.

> Unofficial fan project. Not affiliated with or endorsed by Paradox Interactive or Valve. Europa Universalis IV and its achievements belong to their respective owners.

<!-- TODO: add a screenshot of the tracker page, e.g. ![Tracker screenshot](docs/screenshot.png) -->

## Features

- Achievement list with name, description, and wiki difficulty (Very Easy → Insane)
- Steam global unlock percentage for each achievement, with sorting from rarest to most common
- Four statuses per achievement: not started, queued, in progress, completed
- Progress bar and tabs: all, not completed, queue (queued + in progress), completed
- Search by name or description, filter by difficulty, sort by name, rarity, or difficulty
- Highlights the rarest achievement you have completed
- One-click link to the wiki page for each achievement
- Progress is stored in your browser (`localStorage`); no account or server needed
- Responsive layout for desktop and mobile

The interface language is Turkish.

## How it works

```
wiki.html ─┐
           ├─> full_builder.py ──> achievements.json
steam.html ┘                   └─> eu4_achievement_tracker_steam.html
```

1. `full_builder.py` parses a saved copy of the wiki achievements page (name, description, difficulty) and a saved copy of the Steam global achievements page (unlock percentages) with BeautifulSoup.
2. Achievements are matched by a normalized name (lowercase, letters and digits only).
3. The merged data is written to `achievements.json` and embedded into an HTML template, producing the standalone tracker page.

## Getting started

### Use the tracker

Open `eu4_achievement_tracker_steam.html` in a modern browser.

### Rebuild the data

The source pages are not stored in this repository. Save them yourself (browser: *Save page as… → HTML only*) into the project folder:

| Save as | Source |
| --- | --- |
| `wiki.html` | https://eu4.paradoxwikis.com/Achievements |
| `steam.html` | https://steamcommunity.com/stats/236850/achievements/ |

Then run:

```bash
git clone https://github.com/thatsalgoritma/Europa-Universalis-4-Achievement-Tracker.git
cd Europa-Universalis-4-Achievement-Tracker

pip install -r requirements.txt
python full_builder.py
```

Open the regenerated `eu4_achievement_tracker_steam.html`. If the wiki or Steam changes its page structure, the parsing rules in `full_builder.py` may need to be adjusted.

## Repository structure

| File | Purpose |
| --- | --- |
| `full_builder.py` | Parses the saved pages, merges the data, and generates the tracker |
| `achievements.json` | Merged achievement data (generated) |
| `eu4_achievement_tracker_steam.html` | The standalone tracker page (generated) |
| `requirements.txt` | Python dependencies |

## Tech stack

- Python 3, BeautifulSoup4
- HTML, CSS, vanilla JavaScript (no framework, no build step)

## Known limitations

- Steam percentages are matched to wiki entries by name; achievements whose names differ between the two sources may not match.
- Data is a snapshot of the saved pages and must be rebuilt after new DLCs or patches.
- Progress lives in one browser's `localStorage`; clearing site data or switching browsers resets it.
- Google Fonts are loaded from the network; the page falls back to system fonts when offline.

## Data and legal notes

Achievement names, descriptions, and statistics come from the community wiki and Steam and remain the property of their owners. This repository only contains the code and a generated data snapshot for personal, non-commercial use. Please respect the terms of use of both sites when collecting data.

## License

The source code is released under the [MIT License](LICENSE). The MIT license covers the code only, not the game content or third-party data.
