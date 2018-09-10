Bollywood workshop
==================

This repository contains all the files required to follow the Bollywood
workshop presented at PyCon India 2018.

Installation
------------

To run the materials during the workshop, you need a Jupyter notebook
with recent versions of pandas, matplotlib, bokeh, gensim and scikit-learn.

The set up instructions to create such an environment are listed next.

- Download [Miniconda](https://conda.io/miniconda.html) for Python 3.6 and your architecture (probably 64-bits)
- Add Miniconda path to your system path: `export PATH=<path-to-miniconda>:$PATH`
- Clone repository: `git clone git@github.com:datapythonista/bollywood_workshop.git`
- Change to the repository directory: `cd bollywood_workshop`
- Create your conda environment: `conda env create`
- Activate the environment: `source activate bollywood`
- Change to the notebooks directory: `cd notebooks`
- Run the jupyter notebook server: `jupyter notebook`

scraping
--------

The scraping subproject is not presented during the workshop, but its source it's
included in this repo. It is a `scrapy` project that obtains the main datasets used
during the workshop from the Internet Movie Database (imdb.com).

To run the project

- Change to the scrapy project directory: `cd scraping/bollywood`
- Start the crawler `scrapy crawl imdb -o ../../notebooks/data/movies.json`
