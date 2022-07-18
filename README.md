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
for fold in in ds.folds:
    print(fold)
```

# Dataset structure
There are 3 entity resolution tasks in this repository: imdb-tmdb, imdb-tvdb, tmdb-tvdb, all contained in the `data` folder. 
The data structure follows the structure used in [OpenEA](https://github.com/nju-websoft/OpenEA).
Each folder contains the information of the knowledge graphs (`attr_triples_*`,`rel_triples_*`) and the gold standard of entity links (`ent_links`). The triples are labeled with `1` and `2` where e.g. for imdb-tmdb `1` refers to imdb and `2` to tmdb. The folder 721_5fold contains pre-split entity link folds with 70-20-10 ratio for testing, training, validation.

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
