import logging
import os
import zipfile
from dataclasses import dataclass
from typing import List

from .create_graph import create_graph_data
from .utils import download_file

logger = logging.getLogger(__name__)

try:
    import pandas as pd
except ImportError:
    logger.error("Please install pandas for loading data: pip install pandas")


PREPARED_DATA_URI = "https://cloud.scadsai.uni-leipzig.de/index.php/s/a6gW3AgQpJCELmc/download/ScadsMovieGraphBenchmark.zip"


@dataclass
class Fold:
    train_links: pd.DataFrame
    test_links: pd.DataFrame
    valid_links: pd.DataFrame


@dataclass
class ERData:
    attr_triples_1: pd.DataFrame
    attr_triples_2: pd.DataFrame
    rel_triples_1: pd.DataFrame
    rel_triples_2: pd.DataFrame
    ent_links: pd.DataFrame
    folds: List[Fold]


def _download_and_create(data_path: str):
    if not os.path.exists(data_path):
        os.makedirs(data_path)
    download_file(PREPARED_DATA_URI, data_path)
    zip_path = os.path.join(data_path, "ScadsMovieGraphBenchmark.zip")
    with zipfile.ZipFile(zip_path
        , "r"
    ) as zip_ref:
        zip_ref.extractall(data_path)
    create_graph_data(os.path.join(data_path, "data"))
    os.remove(zip_path)


def _read(path, names):
    return pd.read_csv(
        path,
        header=None,
        names=names,
        sep="\t",
        encoding="utf8",
        dtype=str,
    )


def load_data(pair: str, data_path: str) -> ERData:
    pair_path = os.path.join(data_path, "data", pair)
    if not os.path.exists(pair_path):
        _download_and_create(data_path)
    triple_columns = ["head", "relation", "tail"]
    link_columns = ["left", "right"]
    attr_1 = _read(os.path.join(pair_path, "attr_triples_1"), triple_columns)
    attr_2 = _read(os.path.join(pair_path, "attr_triples_2"), triple_columns)
    rel_1 = _read(os.path.join(pair_path, "rel_triples_1"), triple_columns)
    rel_2 = _read(os.path.join(pair_path, "rel_triples_2"), triple_columns)
    ent_links = _read(os.path.join(pair_path, "ent_links"), link_columns)
    folds = []
    for fold in range(1, 6):
        folds.append(
            Fold(
                train_links=_read(
                    os.path.join(pair_path, "721_5fold", str(fold), "train_links"),
                    link_columns,
                ),
                test_links=_read(
                    os.path.join(pair_path, "721_5fold", str(fold), "test_links"),
                    link_columns,
                ),
                valid_links=_read(
                    os.path.join(pair_path, "721_5fold", str(fold), "valid_links"),
                    link_columns,
                ),
            )
        )
    return ERData(
        attr_triples_1=attr_1,
        attr_triples_2=attr_2,
        rel_triples_1=rel_1,
        rel_triples_2=rel_2,
        ent_links=ent_links,
        folds=folds,
    )
