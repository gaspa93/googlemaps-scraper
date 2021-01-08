# Google Maps Scraper
Scraper of Google Maps reviews.
The code allows to extract the **most recent** reviews starting from the url of a specific Point Of Interest (POI) in Google Maps.
An additional extension helps to monitor and incrementally store the reviews in a MongoDB instance.

## Installation
Follow these steps to use the scraper:
- Download Chromedrive from [here](https://chromedriver.storage.googleapis.com/index.html?path=2.45/).
- Install Python packages from requirements file, either using pip, conda or virtualenv:

        conda create --name scraping python=3.6 --file requirements.txt

**Note**: Python >= 3.6 is required.

## Basic Usage
The scraper.py script needs two main parameters as input:
- `--i`: input file name, containing a list of urls that point to Google Maps place reviews (default: _urls.txt_)
- `--N`: number of reviews to retrieve, starting from the most recent (default: 100)

Example:

  `python scraper.py --N 50`

generates a csv file containing last 50 reviews of places present in _urls.txt_

In current implementation, the CSV file is handled as an external function, so if you want to change path and/or name of output file, you need to modify that function.

Additionally, other parameters can be provided:
- `--place`: boolean value that allows to scrape POI metadata instead of reviews (default: false)
- `--debug`: boolean value that allows to run the browser using the graphical interface (default: false)
- `--source`: boolean value that allows to store source URL as additional field in CSV (default: false)

## Monitoring functionality
The monitor.py script can be used to have an incremental scraper and override the limitation about the number of reviews that can be retrieved.
The only additional requirement is to install MongoDB on your laptop: you can find a detailed guide on the [official site](https://docs.mongodb.com/manual/installation/)

The script takes two input:
- `--i`: same as scraper.py script
- `--from-date`: string date in the format YYYY-MM-DD, gives the minimum date that the scraper tries to obtain

The main idea is to **periodically** run the script to obtain latest reviews: the scraper stores them in MongoDB up to get either the latest review of previous run or the day indicated in the input parameter. 

## Notes
Url must be provided as expected, you can check the example file urls.txt to have an idea of what is a correct url.
If you want to generate the correct url:
1. Go to Google Maps and look for a specific place;
2. Click on the number of reviews in the parenthesis;
3. Save the url that is generated from the latest interaction.

For a basic description of logic and approach about this software development, have a look at the [Medium post](https://towardsdatascience.com/scraping-google-maps-reviews-in-python-2b153c655fc2)
