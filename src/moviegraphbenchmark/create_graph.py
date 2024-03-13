import ast
import logging
import os
from typing import List, Set, Tuple, Optional

import click

from moviegraphbenchmark.get_imdb_data import download_if_needed
from moviegraphbenchmark.utils import download_github_folder
import moviegraphbenchmark

DTYPE_DOUBLE = "<http://www.w3.org/2001/XMLSchema#double>"
DTYPE_NON_NEG_INT = "<http://www.w3.org/2001/XMLSchema#nonNegativeInteger>"
DTYPE_US_DOLLER = "<http://dbpedia.org/datatype/usDollar>"
DTYPE_DATE = "<http://www.w3.org/2001/XMLSchema#date>"

BENCHMARK_RESOURCE_PREFIX = "https://www.scads.de/movieBenchmark/resource/IMDB/"
BENCHMARK_ONTOLOGY_PREFIX = "https://www.scads.de/movieBenchmark/ontology/"

property_dict = {
    "birthYear": "http://dbpedia.org/ontology/birthYear",
    "deathYear": "http://dbpedia.org/ontology/deathYear",
    "episodeNumber": "http://dbpedia.org/ontology/episodeNumber",
    "seasonNumber": "http://dbpedia.org/ontology/seasonNumber",
    "endYear": "https://www.scads.de/movieBenchmark/ontology/endYear",
    "genres": "https://www.scads.de/movieBenchmark/ontology/genre_list",
    "isAdult": "https://www.scads.de/movieBenchmark/ontology/isAdult",
    "primaryName": "https://www.scads.de/movieBenchmark/ontology/name",
    "originalTitle": "https://www.scads.de/movieBenchmark/ontology/originalTitle",
    "primaryProfession": "https://www.scads.de/movieBenchmark/ontology/primaryProfessions",
    "runtimeMinutes": "https://www.scads.de/movieBenchmark/ontology/runtimeMinutes",
    "startYear": "https://www.scads.de/movieBenchmark/ontology/startYear",
    "primaryTitle": "https://www.scads.de/movieBenchmark/ontology/title",
    "episodeOf": "https://www.scads.de/movieBenchmark/ontology/is_episode_of",
    "participatedIn": "https://www.scads.de/movieBenchmark/ontology/participated_in",
    "knownForTitles": "https://www.scads.de/movieBenchmark/ontology/participated_in",
    "type": "http://www.w3.org/1999/02/22-rdf-syntax-ns#type",
}

FILM_TYPE = "http://dbpedia.org/ontology/Film"
TV_EPISODE_TYPE = "http://dbpedia.org/ontology/TelevisionEpisode"
TV_SHOW_TYPE = "http://dbpedia.org/ontology/TelevisionShow"
PERSON_TYPE = "http://xmlns.com/foaf/0.1/Person"

logger = logging.getLogger("moviegraphbenchmark")


def get_allowed(path: str) -> Set[str]:
    with open(path, "r", encoding="utf8") as in_file:
        return {line.strip() for line in in_file}


def get_excluded(path: str) -> Set[Tuple[str, str]]:
    with open(path, "r", encoding="utf8") as in_file:
        return {
            (line.strip().split("\t")[0], line.strip().split("\t")[1])
            for line in in_file
        }


def _should_write(
    s: str, o: str, allowed: Set[str], exclude: Set[Tuple[str, str]]
) -> bool:
    if (s.startswith("nm") or s.startswith("tt")) and (
        o.startswith("nm") or o.startswith("tt")
    ):
        if (s, o) in exclude:
            return False
        if s in allowed and o in allowed:
            return True
        else:
            return False
    elif s.startswith("nm") or s.startswith("tt"):
        if s in allowed:
            return True
        else:
            return False
    elif o.startswith("nm") or o.startswith("tt"):
        if o in allowed:
            return True
        else:
            return False
    return False


def _add_dtype(obj: str, dtype: Optional[str] = None) -> str:
    if dtype is None:
        return obj
    return '"' + obj + '"^^' + dtype


def _sanity_check(value) -> bool:
    if value is None or value == "":
        return False
    return True


def _normalize_year(year: str) -> str:
    return year + "-01-01"


def create_trips(
    s: str,
    p: str,
    o: str,
    multiple_possible: bool,
    allowed: Set[str],
    exclude: Set[Tuple[str, str]],
    dtype: Optional[str] = None,
) -> List[Tuple[str, str, str]]:
    if not (_sanity_check(s) and _sanity_check(p) and _sanity_check(o)):
        return []
    if p == "titleType":
        if o in {"movie", "short", "tvMovie", "tvShort"} or "video" in o:
            o = FILM_TYPE
        elif o == "tvEpisode":
            o = TV_EPISODE_TYPE
        else:
            o = TV_SHOW_TYPE
        p = property_dict["type"]
    else:
        try:
            p = property_dict[p]
        except KeyError:
            logger.debug((s, p, o))
            return []

    trips = []
    if not (s == "\\N" or o == "\\N"):
        if "Year" in p:
            o = _normalize_year(o)
        if multiple_possible:
            if o.startswith("["):
                o_list = ast.literal_eval(o)
            else:
                o_list = [o]
            for obj in o_list:
                if _should_write(s, obj, allowed, exclude):
                    if s.startswith("nm") or s.startswith("tt"):
                        s = BENCHMARK_RESOURCE_PREFIX + s
                    if obj.startswith("nm") or obj.startswith("tt"):
                        obj = BENCHMARK_RESOURCE_PREFIX + obj
                    trips.append((s, p, _add_dtype(obj, dtype)))
        else:
            if _should_write(s, o, allowed, exclude):
                if s.startswith("nm") or s.startswith("tt"):
                    s = BENCHMARK_RESOURCE_PREFIX + s
                if o.startswith("nm") or o.startswith("tt"):
                    o = BENCHMARK_RESOURCE_PREFIX + o
                trips.append((s, p, _add_dtype(o, dtype)))
    return trips


def handle_name_basics(
    path: str, allowed: Set[str], exclude: Set[Tuple[str, str]]
) -> Tuple[List[Tuple[str, str, str]], List[Tuple[str, str, str]]]:
    attr_trips = []
    rel_trips = []
    with open(path, "r", encoding="utf8") as in_file:
        for line in in_file:
            if not line.startswith("nconst\t"):
                row = line.strip().split("\t")
                if row[0] in allowed:
                    attr_trips.extend(
                        create_trips(
                            s=row[0],
                            p="primaryName",
                            o=row[1],
                            multiple_possible=False,
                            allowed=allowed,
                            exclude=exclude,
                        )
                    )
                    attr_trips.extend(
                        create_trips(
                            s=row[0],
                            p="birthYear",
                            o=row[2],
                            multiple_possible=False,
                            allowed=allowed,
                            exclude=exclude,
                            dtype=DTYPE_DATE,
                        )
                    )
                    attr_trips.extend(
                        create_trips(
                            s=row[0],
                            p="deathYear",
                            o=row[3],
                            multiple_possible=False,
                            allowed=allowed,
                            exclude=exclude,
                            dtype=DTYPE_DATE,
                        )
                    )
                    attr_trips.extend(
                        create_trips(
                            s=row[0],
                            p="primaryProfession",
                            o=row[4],
                            multiple_possible=True,
                            allowed=allowed,
                            exclude=exclude,
                        )
                    )
                    rel_trips.extend(
                        create_trips(
                            s=row[0],
                            p="knownForTitles",
                            o=row[5],
                            multiple_possible=True,
                            allowed=allowed,
                            exclude=exclude,
                        )
                    )
                    rel_trips.append(
                        (
                            BENCHMARK_RESOURCE_PREFIX + row[0],
                            property_dict["type"],
                            PERSON_TYPE,
                        )
                    )
    return attr_trips, rel_trips


def handle_title_basics(
    path: str, allowed: Set[str], exclude: Set[Tuple[str, str]]
) -> Tuple[List[Tuple[str, str, str]], List[Tuple[str, str, str]]]:
    attr_trips = []
    rel_trips = []
    with open(path, "r", encoding="utf8") as in_file:
        for line in in_file:
            if not line.startswith("tconst\t"):
                row = line.strip().split("\t")
                if row[0] in allowed:
                    rel_trips.extend(
                        create_trips(
                            s=row[0],
                            p="titleType",
                            o=row[1],
                            multiple_possible=False,
                            allowed=allowed,
                            exclude=exclude,
                        )
                    )
                    attr_trips.extend(
                        create_trips(
                            s=row[0],
                            p="primaryTitle",
                            o=row[2],
                            multiple_possible=False,
                            allowed=allowed,
                            exclude=exclude,
                        )
                    )
                    attr_trips.extend(
                        create_trips(
                            s=row[0],
                            p="originalTitle",
                            o=row[3],
                            multiple_possible=False,
                            allowed=allowed,
                            exclude=exclude,
                        )
                    )
                    attr_trips.extend(
                        create_trips(
                            s=row[0],
                            p="isAdult",
                            o=row[4],
                            multiple_possible=False,
                            allowed=allowed,
                            exclude=exclude,
                        )
                    )
                    attr_trips.extend(
                        create_trips(
                            s=row[0],
                            p="startYear",
                            o=row[5],
                            multiple_possible=False,
                            allowed=allowed,
                            exclude=exclude,
                            dtype=DTYPE_DATE,
                        )
                    )
                    attr_trips.extend(
                        create_trips(
                            s=row[0],
                            p="endYear",
                            o=row[6],
                            multiple_possible=False,
                            allowed=allowed,
                            exclude=exclude,
                            dtype=DTYPE_DATE,
                        )
                    )
                    attr_trips.extend(
                        create_trips(
                            s=row[0],
                            p="runtimeMinutes",
                            o=row[7],
                            multiple_possible=False,
                            allowed=allowed,
                            exclude=exclude,
                        )
                    )
                    attr_trips.extend(
                        create_trips(
                            s=row[0],
                            p="genres",
                            o=row[8],
                            multiple_possible=False,
                            allowed=allowed,
                            exclude=exclude,
                        )
                    )
    return attr_trips, rel_trips


def handle_title_crew(
    path: str, allowed: Set[str], exclude: Set[Tuple[str, str]]
) -> Tuple[List[Tuple[str, str, str]], List[Tuple[str, str, str]]]:
    rel_trips = []
    with open(path, "r", encoding="utf8") as in_file:
        for line in in_file:
            if not line.startswith("tconst\t"):
                row = line.strip().split("\t")
                if row[0] in allowed:
                    rel_trips.extend(
                        create_trips(
                            s=row[0],
                            p="participatedIn",
                            o=row[1],
                            multiple_possible=True,
                            allowed=allowed,
                            exclude=exclude,
                        )
                    )
                    rel_trips.extend(
                        create_trips(
                            s=row[0],
                            p="participatedIn",
                            o=row[2],
                            multiple_possible=True,
                            allowed=allowed,
                            exclude=exclude,
                        )
                    )
    return [], rel_trips


def handle_title_episode(
    path: str, allowed: Set[str], exclude: Set[Tuple[str, str]]
) -> Tuple[List[Tuple[str, str, str]], List[Tuple[str, str, str]]]:
    attr_trips = []
    rel_trips = []
    with open(path, "r", encoding="utf8") as in_file:
        for line in in_file:
            if not line.startswith("tconst\t"):
                row = line.strip().split("\t")
                if row[1] in allowed:
                    rel_trips.extend(
                        create_trips(
                            s=row[0],
                            p="episodeOf",
                            o=row[1],
                            multiple_possible=False,
                            allowed=allowed,
                            exclude=exclude,
                        )
                    )
                    rel_trips.extend(
                        create_trips(
                            s=row[0],
                            p="titleType",
                            o="tvEpisode",
                            multiple_possible=False,
                            allowed=allowed,
                            exclude=exclude,
                        )
                    )
                    attr_trips.extend(
                        create_trips(
                            s=row[0],
                            p="seasonNumber",
                            o=row[2],
                            multiple_possible=False,
                            allowed=allowed,
                            exclude=exclude,
                            dtype=DTYPE_NON_NEG_INT,
                        )
                    )
                    attr_trips.extend(
                        create_trips(
                            s=row[0],
                            p="episodeNumber",
                            o=row[3],
                            multiple_possible=False,
                            allowed=allowed,
                            exclude=exclude,
                            dtype=DTYPE_NON_NEG_INT,
                        )
                    )
    return attr_trips, rel_trips


def handle_title_principals(
    path: str, allowed: Set[str], exclude: Set[Tuple[str, str]]
) -> Tuple[List[Tuple[str, str, str]], List[Tuple[str, str, str]]]:
    attr_trips: List[Tuple[str, str, str]] = []
    rel_trips = []
    with open(path, "r", encoding="utf8") as in_file:
        for line in in_file:
            if not line.startswith("tconst\t"):
                row = line.strip().split("\t")
                if row[0] in allowed:
                    rel_trips.extend(
                        create_trips(
                            s=row[2],
                            p="participatedIn",
                            o=row[0],
                            multiple_possible=False,
                            allowed=allowed,
                            exclude=exclude,
                        )
                    )
    return attr_trips, rel_trips


def _dedup(trips: List[Tuple[str, str, str]]) -> List[Tuple[str, str, str]]:
    d = []
    for t in trips:
        if t not in d:
            d.append(t)
    return d


def parse_files(
    imdb_dir: str, allowed: Set[str], exclude: Set[Tuple[str, str]]
) -> Tuple[List[Tuple[str, str, str]], List[Tuple[str, str, str]]]:
    file_handler_dict = {
        "name.basics.tsv": handle_name_basics,
        "title.basics.tsv": handle_title_basics,
        # "title.crew.tsv": handle_title_crew,
        "title.episode.tsv": handle_title_episode,
        "title.principals.tsv": handle_title_principals,
    }
    # collect triples
    rel_trips = []
    attr_trips = []
    # use tqdm if available
    try:
        from tqdm import tqdm

        for filename, handle_fun in tqdm(
            file_handler_dict.items(), desc="Creating triples"
        ):
            tmp_a, tmp_r = handle_fun(
                os.path.join(imdb_dir, filename), allowed, exclude
            )
            attr_trips.extend(tmp_a)
            rel_trips.extend(tmp_r)
    except ImportError:
        for filename, handle_fun in file_handler_dict.items():
            tmp_a, tmp_r = handle_fun(
                os.path.join(imdb_dir, filename), allowed, exclude
            )
            attr_trips.extend(tmp_a)
            rel_trips.extend(tmp_r)

    # ignore attr trips that do not show up in rel trips
    rel_ids = set()
    for r in rel_trips:
        rel_ids.add(r[0])
        rel_ids.add(r[2])
    cleaned_attr = [a for a in attr_trips if a[0] in rel_ids]
    return _dedup(cleaned_attr), _dedup(rel_trips)


def write_files(
    cleaned_attr: List[Tuple[str, str, str]],
    rel_trips: List[Tuple[str, str, str]],
    out_folder: str,
):
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    with open(
        os.path.join(out_folder, "attr_triples_1"), "w", encoding="utf8"
    ) as out_writer_attr:
        for t in cleaned_attr:
            out_writer_attr.write("\t".join(t) + "\n")
    with open(
        os.path.join(out_folder, "rel_triples_1"), "w", encoding="utf8"
    ) as out_writer_rel:
        for t in rel_trips:
            out_writer_rel.write("\t".join(t) + "\n")


def _data_path() -> str:
    file_path = os.path.abspath(__file__)
    repo_path = os.path.split(os.path.split(os.path.split(file_path)[0])[0])[0]
    data_path = os.path.join(repo_path, "data")
    # if repo was cloned this exists
    if os.path.exists(data_path):
        return data_path
    else:
        # else we use pystow
        try:
            import pystow

            data_path = pystow.join("moviegraphbenchmark", "data")
        except ImportError:
            logger.error("Please install pystow: pip install pystow")
    return data_path


def _create_graph_data(data_path: Optional[str] = None) -> str:
    """(Download and) create benchmark data on specified path.

    :param data_path: Path where data should be stored.
    :return: data_path
    """
    if data_path is None:
        data_path = _data_path()
    # check if data was already created
    if os.path.exists(os.path.join(data_path, "imdb-tmdb", "rel_triples_1")):
        if not os.path.exists(os.path.join(data_path, "imdb_intra_ent_links")):
            logger.info(f"Old data already present in {data_path}, will update...")
        else:
            logger.info(f"Data already present in {data_path}")
            return data_path
    logger.info(f"Using data path: {data_path}")
    if not os.path.exists(os.path.join(data_path, "imdb_intra_ent_links")):
        download_github_folder(data_path, moviegraphbenchmark.__version__)
    imdb_path = os.path.join(data_path, "imdb")
    download_if_needed(imdb_path)
    allowed = get_allowed(os.path.join(data_path, "imdb", "allowed"))
    exclude = get_excluded(os.path.join(data_path, "imdb", "exclude"))
    cleaned_attr, rel_trips = parse_files(imdb_path, allowed, exclude)
    write_files(cleaned_attr, rel_trips, os.path.join(data_path, "imdb-tmdb"))
    write_files(cleaned_attr, rel_trips, os.path.join(data_path, "imdb-tvdb"))
    return data_path


@click.command
@click.option("--data-path", default=None, help="Path where data is stored")
def create_graph_data(data_path: Optional[str] = None):
    """(Download and) create benchmark data on specified path.

    :param data_path: Path where data should be stored.
    """
    _create_graph_data(data_path)


if __name__ == "__main__":
    create_graph_data()
