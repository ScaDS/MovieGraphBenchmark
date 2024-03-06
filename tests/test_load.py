import pytest
from shutil import copyfile
import pathlib
import random
from typing import Set
from moviegraphbenchmark import load_data
from moviegraphbenchmark.create_graph import (
    get_allowed,
    get_excluded,
    _create_data_path,
    parse_files,
)
import os
from read_allowed import read_allowed_lists_from_resources

(
    allowed_episode,
    allowed_film,
    allowed_name,
    allowed_show,
) = read_allowed_lists_from_resources()


def noop(*args, **kwargs):
    return


def mock_read_row_tuples(path: str, exclusion: str, allowed: Set[str]):
    if "name.basics.tsv" in path:
        for ent in allowed_name:
            yield [
                ent,
                "example mcexampleface",
                "1990",
                "2000",
                "dummy",
                "mocker the movie",
            ]
    if "title.basics.tsv" in path:
        for ent in allowed_film:
            yield [
                ent,
                "movie",
                "mocker the movie",
                "mtm",
                "1",
                "1990",
                "2000",
                "222",
                "fiction",
            ]
        for ent in allowed_show:
            yield [
                ent,
                "show",
                "mocker the show",
                "mtm",
                "1",
                "1990",
                "2000",
                "222",
                "fiction",
            ]
    if "title.episode.tsv" in path:
        for ent in allowed_episode:
            yield [
                ent,
                random.choice(allowed_show),
                "1",
                "3",
            ]
    if "title.principals.tsv" in path:
        for ent in allowed_name:
            episode_or_show_or_movie = random.choice(
                [allowed_episode, allowed_film, allowed_show]
            )
            yield [ent, "", random.choice(episode_or_show_or_movie)]


@pytest.mark.slow
def test_create_graph_existing_download(monkeypatch):
    data_path, _ = _create_data_path()
    imdb_path = os.path.join(data_path, "imdb")
    allowed = get_allowed(os.path.join(data_path, "imdb", "allowed"))
    exclude = get_excluded(os.path.join(data_path, "imdb", "exclude"))
    cleaned_attr, rel_trips = parse_files(imdb_path, allowed, exclude)
    assert len(cleaned_attr) == 20800
    assert len(rel_trips) == 17507


@pytest.mark.slow
@pytest.mark.parametrize("pair", [None, "imdb-tmdb", "imdb-tvdb", "tmdb-tvdb"])
def test_load(pair):
    if pair is None:
        ds = load_data()
    else:
        ds = load_data(pair=pair)
    assert not ds.attr_triples_1.empty
    assert not ds.attr_triples_2.empty
    assert not ds.rel_triples_1.empty
    assert not ds.rel_triples_2.empty
    for fold in ds.folds:
        assert not fold.test_links.empty
        assert not fold.train_links.empty
        assert not fold.valid_links.empty
    assert not ds.ent_links.empty


def copy_existing_data(data_path):
    def _create_old_new_data_path(old_data_path, new_data_path, name):
        return os.path.join(old_data_path, name), os.path.join(new_data_path, name)

    def _copy_old_new(old_path, new_path, file_name):
        if not os.path.exists(new_path):
            os.makedirs(new_path)
        copyfile(os.path.join(old_path, file_name), os.path.join(new_path, file_name))

    orig_data = pathlib.Path(__file__).parent.parent.joinpath("data").absolute()
    orig_imdb_path, new_imdb_path = _create_old_new_data_path(
        orig_data, data_path, "imdb"
    )
    _copy_old_new(orig_imdb_path, new_imdb_path, "allowed")
    _copy_old_new(orig_imdb_path, new_imdb_path, "exclude")

    for task_folder in ["imdb-tmdb", "imdb-tvdb", "tmdb-tvdb"]:
        orig_task_path, new_task_path = _create_old_new_data_path(
            orig_data, data_path, task_folder
        )
        for fold_folder in range(1, 6):
            old_fold, new_fold = _create_old_new_data_path(
                orig_task_path,
                new_task_path,
                os.path.join("721_5fold", str(fold_folder)),
            )
            for links in ["test_links", "train_links", "valid_links"]:
                _copy_old_new(old_fold, new_fold, links)

        if task_folder == "tmdb-tvdb":
            _copy_old_new(orig_task_path, new_task_path, "attr_triples_1")
            _copy_old_new(orig_task_path, new_task_path, "rel_triples_1")
        _copy_old_new(orig_task_path, new_task_path, "attr_triples_2")
        _copy_old_new(orig_task_path, new_task_path, "rel_triples_2")
        _copy_old_new(orig_task_path, new_task_path, "ent_links")


@pytest.mark.parametrize("pair", [None, "imdb-tmdb", "imdb-tvdb", "tmdb-tvdb"])
def test_load_mocked_downloads(pair, monkeypatch, tmpdir):
    data_path = tmpdir.mkdir("data")
    copy_existing_data(data_path)
    monkeypatch.setattr("moviegraphbenchmark.create_graph.download_if_needed", noop)
    monkeypatch.setattr("moviegraphbenchmark.create_graph._download_data", noop)
    monkeypatch.setattr(
        "moviegraphbenchmark.create_graph._read_row_tuples", mock_read_row_tuples
    )
    if pair is None:
        ds = load_data(data_path=data_path)
    else:
        ds = load_data(pair=pair, data_path=data_path)
    assert not ds.attr_triples_1.empty
    assert not ds.attr_triples_2.empty
    assert not ds.rel_triples_1.empty
    assert not ds.rel_triples_2.empty
    for fold in ds.folds:
        assert not fold.test_links.empty
        assert not fold.train_links.empty
        assert not fold.valid_links.empty
    assert not ds.ent_links.empty
