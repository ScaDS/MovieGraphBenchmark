import gzip
import os
import shutil
import sys

import requests

uris = {
    "https://datasets.imdbws.com/name.basics.tsv.gz": "name.basics.tsv",
    "https://datasets.imdbws.com/title.basics.tsv.gz": "title.basics.tsv",
    # "https://datasets.imdbws.com/title.crew.tsv.gz": "title.crew.tsv",
    "https://datasets.imdbws.com/title.episode.tsv.gz": "title.episode.tsv",
    "https://datasets.imdbws.com/title.principals.tsv.gz": "title.principals.tsv",
}


def download_file(url, dl_path, chunk_size=1024):
    filename = os.path.basename(url)
    filesize = int(requests.head(url).headers["Content-Length"])
    try:
        from tqdm import tqdm  # noqa: autoimport

        with requests.get(url, stream=True) as r, open(
            os.path.join(dl_path, filename), "wb"
        ) as f, tqdm(
            unit="B",
            unit_scale=True,
            unit_divisor=1024,
            total=filesize,
            file=sys.stdout,
            desc=filename,
        ) as progress:
            for chunk in r.iter_content(chunk_size=chunk_size):
                datasize = f.write(chunk)
                progress.update(datasize)
    except ImportError:
        with requests.get(url, stream=True) as r, open(
            os.path.join(dl_path, filename), "wb"
        ) as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)


def unzip(filepath):
    with gzip.open(filepath + ".gz", "rb") as f_in:
        with open(filepath, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)


def download_if_needed(imdb_path):
    os.makedirs(imdb_path, exist_ok=True)
    for u, p in uris.items():
        filepath = os.path.join(imdb_path, p)
        if not os.path.isfile(filepath):
            print(f"Did not find {filepath}, therefore downloading")
            download_file(u, imdb_path)
            print("Unpacking gz archive")
            unzip(filepath)
            os.remove(filepath + ".gz")
