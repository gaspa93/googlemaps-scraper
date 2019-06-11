# Google Maps Scraper
Scraper of Google Maps reviews.
The code allows to extract the **most recent** reviews starting from the url of POI reviews.


## Installation
Follow these steps to use the scraper:
- Download Chromedrive from [here](https://chromedriver.storage.googleapis.com/index.html?path=2.45/).
- Install Python packages from requirements file, either using pip, conda or virtualenv:

        `conda create --name scraping python=3.6 --file requirements.txt`

**Note**: Python >= 3.6 is required. 

## Usage
The scraper takes two parameters in input:
- `--i`: input file, containing a list of urls that point to Google Maps place reviews (default: _urls.txt_).
- `--N`: the number of reviews we want to retrieve, starting from the most recent (default: 100).

Example:

  `python scraper.py --N 50`
 
generates a csv file containing last 50 reviews of places present in _urls.txt_

The _config.json_ file allows to set the directory to store output csv, as well as their filenames.
