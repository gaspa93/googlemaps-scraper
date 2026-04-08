# 📍 Google Maps Scraper

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-GPL--3.0-orange.svg)
![GitHub Repo stars](https://img.shields.io/github/stars/gaspa93/googlemaps-scraper?style=flat)
![GitHub last commit](https://img.shields.io/github/last-commit/gaspa93/googlemaps-scraper)

Scrape **recent reviews** from any Google Maps listing — with optional MongoDB monitoring for incremental updates.

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Output Format](#output-format)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Features

| Feature | Description |
|---------|-------------|
| 🚀 **Latest Reviews First** | Extract the most recent reviews, sorted by date |
| 🔄 **Incremental Monitoring** | MongoDB-based diff to track new reviews over time |
| 📊 **Flexible Sorting** | Sort by relevance, newest, highest/lowest rating |
| 🔍 **Place Metadata** | Scrape POI info (address, phone, hours) separately |
| 🐛 **Debug Mode** | Run with visible browser for debugging |
| 🌐 **Source Tracking** | Optionally store the original Google Maps URL |

---

## Installation

### Prerequisites

- **Python ≥ 3.9**
- **ChromeDriver** — [Download here](https://chromedriver.storage.googleapis.com/index.html) (match your Chrome version)

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/gaspa93/googlemaps-scraper.git
cd googlemaps-scraper

# 2. Create a virtual environment
python -m venv scraping-env
source scraping-env/bin/activate  # Windows: scraping-env\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Place ChromeDriver in your PATH or the project directory
```

> **macOS/Linux tip:** `brew install --cask chromedriver`

---

## Quick Start

### Scrape Reviews

```bash
# Basic usage — scrape 50 most recent reviews
python scraper.py --N 50

# Custom input file and output name
python scraper.py --i my_urls.txt --o my_output.csv --N 100

# Sort by highest rating instead of newest
python scraper.py --sort_by highest_rating --N 50
```

**Default input file:** `urls.txt` (one Google Maps URL per line)

### Scrape Place Metadata

```bash
python scraper.py --place --i urls_places.txt --o places.csv
```

---

## Configuration

### Command-Line Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--i` | `urls.txt` | Input file with Google Maps URLs |
| `--o` | `output.csv` | Output CSV filename (saved in `data/`) |
| `--N` | `100` | Number of reviews to retrieve |
| `--place` | `false` | Scrape POI metadata instead of reviews |
| `--debug` | `false` | Show browser window during scraping |
| `--source` | `false` | Include source URL in output |
| `--sort_by` | `newest` | Sort: `most_relevant`, `newest`, `highest_rating`, `lowest_rating` |

### Correct URL Format

```
https://www.google.com/maps/place/.../data=!4m5!3m4!1s...!8m2!3d...!4d...
```

See `urls.txt` for a working example.

---

## Monitoring

Track reviews **over time** with MongoDB:

```bash
# First run — captures all reviews up to today
python monitor.py --i urls.txt --from-date 2024-01-01

# Subsequent runs — only fetches NEW reviews since last run
python monitor.py --i urls.txt
```

The monitor script stores reviews in **MongoDB** and only fetches what's new since the last check — much faster on repeat runs.

> **MongoDB Setup:** See the [official guide](https://www.mongodb.com/docs/manual/installation/)

---

## Output Format

Reviews are saved as CSV with these columns:

| Column | Description |
|--------|-------------|
| `author_name` | Reviewer display name |
| `rating` | Star rating (1–5) |
| `date` | Review date |
| `text` | Full review text |
| `response` | Owner's reply (if any) |
| `source_url` | Original Google Maps URL (if `--source` used) |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **No reviews returned** | Check URL format matches the `urls.txt` example |
| **ChromeDriver errors** | Ensure ChromeDriver version matches your Chrome browser |
| **Blocked by Google** | Use `--debug` to slow scraping; add delays between runs |
| **MongoDB connection failed** | Verify MongoDB is running: `mongod` |

---

## License

Licensed under **GPL-3.0**. See [LICENSE](LICENSE) for details.

---

*README optimized with [Gingiris README Generator](https://gingiris.github.io/github-readme-generator/)*
