import gzip
import logging
import os
import shutil
import sys
from moviegraphbenchmark.utils import download_file

import requests

uris = {
    "https://web.archive.org/web/20200717014821/https://datasets.imdbws.com/name.basics.tsv.gz": "name.basics.tsv",
    "https://web.archive.org/web/20200717014801/https://datasets.imdbws.com/title.basics.tsv.gz": "title.basics.tsv",
    # "https://datasets.imdbws.com/title.crew.tsv.gz": "title.crew.tsv",
    "https://web.archive.org/web/20200717014920/https://datasets.imdbws.com/title.episode.tsv.gz": "title.episode.tsv",
    "https://web.archive.org/web/20200717014706/https://datasets.imdbws.com/title.principals.tsv.gz": "title.principals.tsv",
}


logger = logging.getLogger(__name__)

def unzip(filepath: str):
    with gzip.open(filepath + ".gz", "rb") as f_in:
        with open(filepath, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)


def download_if_needed(imdb_path: str):
    os.makedirs(imdb_path, exist_ok=True)
    for u, p in uris.items():
        filepath = os.path.join(imdb_path, p)
        if not os.path.isfile(filepath):
            logger.info(f"Did not find {filepath}, therefore downloading")
            download_file(u, imdb_path)
            logger.info("Unpacking gz archive")
            unzip(filepath)
            os.remove(filepath + ".gz")
