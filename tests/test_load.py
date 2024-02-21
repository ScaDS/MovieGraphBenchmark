import pytest
from moviegraphbenchmark import load_data

@pytest.mark.parametrize("pair", [None, "imdb-tmdb","imdb-tvdb","tmdb-tvdb"])
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
    assert not ds.intra_ent_links[0].empty
    assert not ds.intra_ent_links[1].empty
