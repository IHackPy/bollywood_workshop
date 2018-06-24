Bollywood workshop
==================

This repository contains all the files required to follow the Bollywood
workshop presented at PyCon India 2018.

Installation
------------

To be able to install and run the files, you need to follow the next steps:

- Download [Miniconda](https://conda.io/miniconda.html) for Python 3.6 and your architecture (probably 64-bits)
- Add Miniconda path to your system path: `export PATH=<path-to-miniconda>:$PATH`
- Clone repository: `git clone git@github.com:datapythonista/bollywood_workshop.git`
- Change to the repository directory: `cd bollywood_workshop`
- Create your conda environment: `conda env create -f requirements.yaml`
- Activate the environment: `source activate bollywood`
- Change to the notebooks directory: `cd notebooks`
- Run the jupyter notebook server: `jupyter notebook`

scraping
--------

The scraping subproject is a `scrapy` project that obtains the main datasets
from IMBd.

To run the project

- Change to the scrapy project directory: `cd scraping/bollywood`
- Start the crawler `scrapy crawl imdb -o ../../notebooks/data/movies.json`
