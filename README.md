# YouTube Scraper
 A Python-based tool that scrapes YouTube video comments using the YouTube Data API, performs sentiment analysis, and filters comments based on user-defined keywords. This application helps users analyze large volumes of comments, identify positive and negative feedback, and export relevant comments to a PDF report for further review.

## Prerequisites

- Python 3.x
- Required Python libraries:
  - `google-api-python-client`
  - `textblob`
  - `fpdf`
  - `getpass`
  - `reportlab` (for handling emojis)

You can install the required libraries using pip:

```sh
pip install google-api-python-client textblob fpdf reportlab
