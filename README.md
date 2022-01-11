# Dataset License
Due to licensing we are not allowed to distribute the IMDB datasets (more info on their license can be found [here](https://help.imdb.com/article/imdb/general-information/can-i-use-imdb-data-in-my-software/G5JTRESSHJBBHTGX?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=3aefe545-f8d3-4562-976a-e5eb47d1bb18&pf_rd_r=2TNAA9FRS3TJWM3AEQ2X&pf_rd_s=center-1&pf_rd_t=60601&pf_rd_i=interfaces&ref_=fea_mn_lk1#))
What we can do is let you build the IMDB side of the entity resolution datasets yourself. Please be aware, that the mentioned license applies to the IMDB data you produce.

# Dependencies
The only dependency is `requests`, although with `tqdm` you will have nice progress bars (this is optional).

# Getting the data 
The TMDB and TVDB datasets are already provided in this repo and where created from the public APIs of [TheMovieDB](https://www.themoviedb.org/documentation/api) and [TVDB](https://www.thetvdb.com/api-information). What you have to do is create the IMDB data.

If you love one-liners and trust random people on the internet (that promise to be nice) you can simply run:
```bash
curl -sSL https://raw.githubusercontent.com/ScaDS/MovieGraphBenchmark/master/src/main.py | python3 -
```

This will download this repo, execute `python src/create_graph.py`, which downloads the IMDB data and creates the missing datasets. Furthermore it cleans up and only leaves a `ScaDSMovieGraphBenchmark` in your current directory with the datasets.

You can also specify a specific directory where data should go:

```bash
curl -sSL https://raw.githubusercontent.com/ScaDS/MovieGraphBenchmark/master/src/main.py | python3 - mypath/benchmarkfolder
```

If you don't like piping scripts from the internet (or you use windows) you can do the steps by yourself:
```
git clone https://github.com/ScaDS/MovieGraphBenchmark.git
cd MovieGraphBenchmark
python3 src/creath_graph.py
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
