import sys
import ast
import os
from tqdm import tqdm
from get_imdb_data import download_if_needed

DTYPE_YEAR = "<http://www.w3.org/2001/XMLSchema#gYear>"
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
    "genre_list": "https://www.scads.de/movieBenchmark/ontology/genre_list",
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


def get_allowed(path):
    with open(path, "r") as in_file:
        return set([line.strip() for line in in_file])


def _should_write(s, o, allowed):
    if s.startswith("nm") or s.startswith("tt"):
        if s in allowed:
            return True
    if o.startswith("nm") or o.startswith("tt"):
        if o in allowed:
            return True
    return False


def _add_dtype(obj, dtype):
    if dtype is None:
        return obj
    return '"' + obj + '"^^' + dtype


def write_trips(s, p, o, multiple_possible, allowed, dtype=None):
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
            print(s, p, o)
            return []

    trips = []
    if not (s == "\\N" or o == "\\N"):
        if multiple_possible:
            if o.startswith("["):
                o_list = ast.literal_eval(o)
            else:
                o_list = o.split(",")
            for obj in o_list:
                if _should_write(s, obj, allowed):
                    if s.startswith("nm") or s.startswith("tt"):
                        s = BENCHMARK_RESOURCE_PREFIX + s
                    if obj.startswith("nm") or obj.startswith("tt"):
                        obj = BENCHMARK_RESOURCE_PREFIX + obj
                    trips.append([s, p, _add_dtype(obj, dtype)])
        else:
            if _should_write(s, o, allowed):
                if s.startswith("nm") or s.startswith("tt"):
                    s = BENCHMARK_RESOURCE_PREFIX + s
                if o.startswith("nm") or o.startswith("tt"):
                    o = BENCHMARK_RESOURCE_PREFIX + o
                trips.append([s, p, _add_dtype(o, dtype)])
    return trips


def handle_name_basics(path, allowed):
    attr_trips = []
    rel_trips = []
    with open(path, "r") as in_file:
        for line in in_file:
            if not line.startswith("nconst\t"):
                row = line.strip().split("\t")
                if row[0] in allowed:
                    attr_trips.extend(
                        write_trips(row[0], "primaryName", row[1], False, allowed)
                    )
                    attr_trips.extend(
                        write_trips(
                            row[0], "birthYear", row[2], False, allowed, DTYPE_YEAR
                        )
                    )
                    attr_trips.extend(
                        write_trips(
                            row[0], "deathYear", row[3], False, allowed, DTYPE_YEAR
                        )
                    )
                    attr_trips.extend(
                        write_trips(row[0], "primaryProfession", row[4], True, allowed)
                    )
                    rel_trips.extend(
                        write_trips(row[0], "knownForTitles", row[5], True, allowed)
                    )
                    rel_trips.append(
                        [
                            BENCHMARK_RESOURCE_PREFIX + row[0],
                            property_dict["type"],
                            PERSON_TYPE,
                        ]
                    )
    return attr_trips, rel_trips


def handle_title_basics(path, allowed):
    attr_trips = []
    with open(path, "r") as in_file:
        for line in in_file:
            if not line.startswith("tconst\t"):
                row = line.strip().split("\t")
                if row[0] in allowed:
                    attr_trips.extend(
                        write_trips(row[0], "titleType", row[1], False, allowed)
                    )
                    attr_trips.extend(
                        write_trips(row[0], "primaryTitle", row[2], False, allowed)
                    )
                    attr_trips.extend(
                        write_trips(row[0], "originalTitle", row[3], False, allowed)
                    )
                    attr_trips.extend(
                        write_trips(row[0], "isAdult", row[4], False, allowed)
                    )
                    attr_trips.extend(
                        write_trips(
                            row[0], "startYear", row[5], False, allowed, DTYPE_YEAR
                        )
                    )
                    attr_trips.extend(
                        write_trips(
                            row[0], "endYear", row[6], False, allowed, DTYPE_YEAR
                        )
                    )
                    attr_trips.extend(
                        write_trips(row[0], "runtimeMinutes", row[7], False, allowed,)
                    )
                    # attr_trips.extend(
                    #     write_trips(row[0], "genres", row[7], False, allowed)
                    # )
    return attr_trips, []


def handle_title_crew(path, allowed):
    rel_trips = []
    with open(path, "r") as in_file:
        for line in in_file:
            if not line.startswith("tconst\t"):
                row = line.strip().split("\t")
                if row[0] in allowed:
                    rel_trips.extend(
                        write_trips(row[0], "participatedIn", row[1], True, allowed)
                    )
                    rel_trips.extend(
                        write_trips(row[0], "participatedIn", row[2], True, allowed)
                    )
    return [], rel_trips


def handle_title_episode(path, allowed):
    attr_trips = []
    rel_trips = []
    with open(path, "r") as in_file:
        for line in in_file:
            if not line.startswith("tconst\t"):
                row = line.strip().split("\t")
                if row[1] in allowed:
                    rel_trips.extend(
                        write_trips(row[0], "episodeOf", row[1], False, allowed)
                    )
                    attr_trips.extend(
                        write_trips(
                            row[0],
                            "seasonNumber",
                            row[2],
                            False,
                            allowed,
                            DTYPE_NON_NEG_INT,
                        )
                    )
                    attr_trips.extend(
                        write_trips(
                            row[0],
                            "episodeNumber",
                            row[3],
                            False,
                            allowed,
                            DTYPE_NON_NEG_INT,
                        )
                    )
    return attr_trips, rel_trips


def handle_title_principals(path, allowed):
    attr_trips = []
    rel_trips = []
    with open(path, "r") as in_file:
        for line in in_file:
            if not line.startswith("tconst\t"):
                row = line.strip().split("\t")
                if row[0] in allowed:
                    rel_trips.extend(
                        write_trips(row[2], "participatedIn", row[0], False, allowed)
                    )
                    # attr_trips.extend(
                    #     write_trips(row[2], "ordering", row[1], False, allowed)
                    # )
                    # attr_trips.extend(
                    #     write_trips(row[2], "category", row[3], False, allowed)
                    # )
                    # attr_trips.extend(
                    #     write_trips(row[2], "job", row[4], False, allowed)
                    # )
                    # attr_trips.extend(
                    #     write_trips(row[2], "characters", row[5], True, allowed)
                    # )
    return attr_trips, rel_trips


def parse_files_write_trips(imdb_dir, allowed, out_folder):
    file_handler_dict = {
        "name.basics.tsv": handle_name_basics,
        "title.basics.tsv": handle_title_basics,
        # "title.crew.tsv": handle_title_crew,
        "title.episode.tsv": handle_title_episode,
        "title.principals.tsv": handle_title_principals,
    }
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    # collect triples
    rel_trips = []
    attr_trips = []
    for filename, handle_fun in tqdm(
        file_handler_dict.items(), desc="Creating triples"
    ):
        tmp_a, tmp_r = handle_fun(os.path.join(imdb_dir, filename), allowed)
        attr_trips.extend(tmp_a)
        rel_trips.extend(tmp_r)

    # ignore attr trips that do not show up in rel trips
    rel_ids = set()
    for r in rel_trips:
        rel_ids.add(r[0])
        rel_ids.add(r[2])
    cleaned_attr = [a for a in attr_trips if a[0] in rel_ids]
    with open(os.path.join(out_folder, "attr_triples_1"), "w") as out_writer_attr:
        for t in cleaned_attr:
            out_writer_attr.write("\t".join(t) + "\n")
    with open(os.path.join(out_folder, "rel_triples_1"), "w") as out_writer_rel:
        for t in rel_trips:
            out_writer_rel.write("\t".join(t) + "\n")


if __name__ == "__main__":
    download_if_needed()
    imdb_path = os.path.join("data", "imdb")
    allowed_ids = [
        os.path.join("data", "imdb", "allowedIMDBTMDB"),
        os.path.join("data", "imdb", "allowedIMDBTVDB"),
    ]
    output_folders = [
        os.path.join("data", "imdb-tmdb"),
        os.path.join("data", "imdb-tvdb"),
    ]
    for ids_path, output in zip(allowed_ids, output_folders):
        allowed = get_allowed(ids_path)
        parse_files_write_trips(imdb_path, allowed, output)
