# napsanalyser

## What's this?

A set of code to download, index, and extract the PM2.5 speciation data provided by the Environment and Climate Change Canada Data Catalogue.

## Required system

Python and Jupyter Lab are required to run the code in this repository.

## How to use

Run the notebooks in notebooks/ directory in this order to extract the dataset into CSV files.

- [download_PM25_data.ipynb](./notebooks/download_PM25_data.ipynb)
- [index_PM25_data.ipynb](./notebooks/index_PM25_data.ipynb)
- [extract_PM25_data.ipynb](./notebooks/extract_PM25_data.ipynb)

If you want to extract the data in a format of the input for a source apportionment software, use [extract_for_source_apportionment.ipynb](./notebooks/extract_for_source_apportionment.ipynb) after running all three notebooks above.
