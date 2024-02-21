import logging
import os
from dataclasses import dataclass
from typing import List, Tuple, Optional

from moviegraphbenchmark.create_graph import _create_graph_data

logger = logging.getLogger("moviegraphbenchmark")

try:
    import pandas as pd
except ImportError:
    logger.error("Please install pandas for loading data: pip install pandas")


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
    intra_ent_links: Optional[Tuple[pd.DataFrame, pd.DataFrame]] = None


def _read(path, names):
    return pd.read_csv(
        path,
        header=None,
        names=names,
        sep="\t",
        encoding="utf8",
        dtype=str,
    )


def load_data(pair: str = "imdb-tmdb", data_path: Optional[str] = None) -> ERData:
    data_path = _create_graph_data(data_path)
    data_pair = pair.split("-")
    logger.info(f"Loading from data path: {data_path}")
    pair_path = os.path.join(data_path, pair)
    triple_columns = ["head", "relation", "tail"]
    link_columns = ["left", "right"]
    attr_1 = _read(os.path.join(pair_path, "attr_triples_1"), triple_columns)
    attr_2 = _read(os.path.join(pair_path, "attr_triples_2"), triple_columns)
    rel_1 = _read(os.path.join(pair_path, "rel_triples_1"), triple_columns)
    rel_2 = _read(os.path.join(pair_path, "rel_triples_2"), triple_columns)
    ent_links = _read(os.path.join(pair_path, "ent_links"), link_columns)
    intra_ent_left = _read(
        os.path.join(data_path, f"{data_pair[0]}_intra_ent_links"), [f"{data_pair[0]}_left", f"{data_pair[0]}_right"]
    )
    intra_ent_right = _read(
        os.path.join(data_path, f"{data_pair[1]}_intra_ent_links"), [f"{data_pair[1]}_left", f"{data_pair[1]}_right"]
    )
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
        intra_ent_links=(intra_ent_left, intra_ent_right),
    )
