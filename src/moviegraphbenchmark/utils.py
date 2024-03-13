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


def move_recursively_overwrite(src, dst):
    """Circumvent shutil failing to overwrite dirs by overwriting contents."""
    # dir exists try to move all inner files and overwrite
    if os.path.exists(dst) and os.path.isdir(src):
        for inner in os.listdir(src):
            move_recursively_overwrite(
                os.path.join(src, inner), os.path.join(dst, inner)
            )
    else:
        shutil.move(src, dst)


def download_github_folder(
    dl_path: str,
    version: str,
    base_url: str = "https://github.com/ScaDS/MovieGraphBenchmark/archive/refs/tags/",
):
    url = f"{base_url}v{version}.zip"
    if not os.path.exists(dl_path):
        os.makedirs(dl_path)
    output_path = download_file(url=url, dl_path=dl_path)
    with zipfile.ZipFile(output_path, "r") as zip_ref:
        zip_ref.extractall(dl_path)
    os.remove(output_path)

    # move everything inside data folder
    zip_folder = list(glob(os.path.join(dl_path, "MovieGraphBenchmark-*")))[0]
    new_data_path = os.path.join(zip_folder, "data")
    for file_or_dir in os.listdir(new_data_path):
        move_recursively_overwrite(
            os.path.join(new_data_path, file_or_dir), os.path.join(dl_path, file_or_dir)
        )

    # remove everything else
    shutil.rmtree(zip_folder)
