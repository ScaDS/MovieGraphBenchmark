import os
import requests
import sys

def download_file(url: str, dl_path: str, chunk_size: int = 1024):
    filename = os.path.basename(url)
    header = requests.head(url)
    try:
        filesize = int(header.headers["Content-Length"])
    except KeyError:
        filesize = int(header.raw.info()["Content-Length"])
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
