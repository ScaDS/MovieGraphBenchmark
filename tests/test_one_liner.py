import os
import sys

from main import main
from pytest import approx

sys.path.append("src")


def line_count(path: str) -> int:
    with open(path, "r") as in_file:
        return len(in_file.readlines())


def check_data(folder_name):
    for ds_pair in ["imdb-tmdb", "imdb-tvdb", "tmdb-tvdb"]:
        assert os.path.exists(folder_name)
        ds_path = os.path.join(folder_name, ds_pair)
        for fold in range(1, 6):
            fold_path = os.path.join(ds_path, "721_5fold", str(fold))
            test_links = line_count(os.path.join(fold_path, "test_links"))
            train_links = line_count(os.path.join(fold_path, "train_links"))
            valid_links = line_count(os.path.join(fold_path, "valid_links"))
            total_links = test_links + train_links + valid_links
            assert test_links == approx(total_links * 0.7, abs=1)
            assert train_links == approx(total_links * 0.2, abs=1)
            assert valid_links == approx(total_links * 0.1, abs=1)
        # basically just testing if the files are there and not empty
        for file_name in [
            "attr_triples_1",
            "attr_triples_2",
            "rel_triples_1",
            "rel_triples_2",
        ]:
            assert line_count(os.path.join(ds_path, file_name)) > 10000


def test(tmpdir):
    folder_path = os.path.join(tmpdir, "myfolder")
    main(folder_path)
    check_data(folder_path)
