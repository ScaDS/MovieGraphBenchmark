import os
import shutil
from glob import glob
import zipfile
import requests
import sys


def download_file(url: str, dl_path: str, chunk_size: int = 1024):
    filename = os.path.basename(url)
    header = requests.head(url)
    output_path = os.path.join(dl_path, filename)
    try:
        filesize = int(header.headers["Content-Length"])
    except KeyError:
        filesize = int(header.raw.info()["Content-Length"])
    try:
        from tqdm import tqdm  # noqa: autoimport

        with requests.get(url, stream=True) as r, open(output_path, "wb") as f, tqdm(
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
        with requests.get(url, stream=True) as r, open(output_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)
    return output_path

def _remove_file_or_dir(path: str):
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)

def download_github_folder(
    dl_path: str,
    version: str,
    base_url: str = "https://github.com/ScaDS/MovieGraphBenchmark/archive/refs/tags/",
):
    # url = f"{base_url}v{version}.zip"
    url = "https://cloud.scadsai.uni-leipzig.de/index.php/s/4WwwG7yHWPAiNnc/download/ScadsMovieGraphBenchmark1_2.zip"
    print("=== USING TEMPORARY URL ===")
    if not os.path.exists(dl_path):
        os.makedirs(dl_path)
    output_path = download_file(url=url, dl_path=dl_path)
    with zipfile.ZipFile(output_path, "r") as zip_ref:
        zip_ref.extractall(dl_path)
    os.remove(output_path)

    # remove everything except data folder
    zip_folder = os.path.join(dl_path,os.listdir(dl_path)[0])
    for rootfile in glob(os.path.join(zip_folder, ".*")):
        _remove_file_or_dir(rootfile)
    for rootfile in glob(os.path.join(zip_folder, "*")):
        if not rootfile.endswith("data"):
            _remove_file_or_dir(rootfile)
    shutil.move(os.path.join(zip_folder, "data"), os.path.join(dl_path, "data"))
    shutil.rmtree(zip_folder)
