# !! Update 2024-02-24 (fixed in 1.1.0) !!
We found that `ent_links` in some cases contained intra-dataset links, which is not immediately noticable by the user.
Another round of clerical review was performed, transitive links, which were previously missed are added and the `ent_links` files now only contain entity links _between_ the datasets. The `721_5fold` directories have been adapted accordingly.
The intra-dataset links are now in `{dataset_name}_intra_ent_links` for each of the three datasets.
What might also not be immediately obvious is that this dataset can be used as multi-source entity resolution task.
We therefore provide a `multi_source_cluster` file with each line consisting of a cluster id and comma-seperated cluster members of the three datasets, which can also include multiple entries for a single dataset.

# Dataset License
Due to licensing we are not allowed to distribute the IMDB datasets (more info on their license can be found [here](https://help.imdb.com/article/imdb/general-information/can-i-use-imdb-data-in-my-software/G5JTRESSHJBBHTGX?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=3aefe545-f8d3-4562-976a-e5eb47d1bb18&pf_rd_r=2TNAA9FRS3TJWM3AEQ2X&pf_rd_s=center-1&pf_rd_t=60601&pf_rd_i=interfaces&ref_=fea_mn_lk1#))
What we can do is let you build the IMDB side of the entity resolution datasets yourself. Please be aware, that the mentioned license applies to the IMDB data you produce.

# Usage
You can simply install the package via pip:
```bash
pip install moviegraphbenchmark
```
and then run
```bash
moviegraphbenchmark
```
which will create the data in the default data path `~/.data/moviegraphbenchmark/data`

You can also define a specific folder if you want with
```bash
moviegraphbenchmark --data-path anotherpath
```

For ease-of-usage in your project you can also use this library for loading the data (this will create the data if it's not present):

```python
from moviegraphbenchmark import load_data
ds = load_data()
# by default this will load `imdb-tmdb`
print(ds.attr_triples_1)

# specify other pair and specific data path
ds = load_data(pair="imdb-tmdb",data_path="anotherpath")

# the dataclass contains all the files loaded as pandas dataframes
print(ds.attr_triples_2)
print(ds.rel_triples_1)
print(ds.rel_triples_2)
print(ds.ent_links)
for fold in ds.folds:
    print(fold)

# the intra-dataset links are stored as tuple of dataframes
print(ds.intra_ent_links[0])
print(ds.intra_ent_links[1])
```

Alternatively this dataset (among others) is also available in [`sylloge`](https://github.com/dobraczka/sylloge).

# Dataset structure
There are 3 entity resolution tasks in this repository: imdb-tmdb, imdb-tvdb, tmdb-tvdb, all contained in the `data` folder. 
The data structure mainly follows the structure used in [OpenEA](https://github.com/nju-websoft/OpenEA).
Each folder contains the information of the knowledge graphs (`attr_triples_*`,`rel_triples_*`) and the gold standard of entity links between the datasets(`ent_links`). The triples are labeled with `1` and `2` where e.g. for imdb-tmdb `1` refers to imdb and `2` to tmdb. The folder 721_5fold contains pre-split entity link folds with 70-20-10 ratio for testing, training, validation.
Furthermore, there exists a file for each dataset with intra-dataset links called `*_intra_ent_links`.
For the binary cases each dataset has a `cluster` file in the respective folder. Each line here is a cluster with comma-seperated members of the cluster. This includes intra- and inter-dataset links.
For the multi-source setting, you can use the `multi_source_cluster` file in the `data` folder.
Using [`sylloge`](https://github.com/dobraczka/sylloge) you can also easily load this dataset as a multi-source task:

```
from sylloge import MovieGraphBenchmark
ds = MovieGraphBenchmark(graph_pair='multi')
```

# Citing
This dataset was first presented in this paper:
```
@inproceedings{EAGERKGCW2021,
  author    = {Daniel Obraczka and
               Jonathan Schuchart and
               Erhard Rahm},
  editor    = {David Chaves-Fraga and
               Anastasia Dimou and
               Pieter Heyvaert and
               Freddy Priyatna and
               Juan Sequeda},
  title     = {Embedding-Assisted Entity Resolution for Knowledge Graphs},
  booktitle = {Proceedings of the 2nd International Workshop on Knowledge Graph Construction co-located with 18th Extended Semantic Web Conference (ESWC 2021), Online, June 5, 2021},
  series    = {{CEUR} Workshop Proceedings},
  volume    = {2873},
  publisher = {CEUR-WS.org},
  year      = {2021},
  url       = {http://ceur-ws.org/Vol-2873/paper8.pdf},
}
```
