# Dataset License
Due to licensing we are not allowed to distribute the IMDB datasets (more info on their license can be found [here](https://help.imdb.com/article/imdb/general-information/can-i-use-imdb-data-in-my-software/G5JTRESSHJBBHTGX?pf_rd_m=A2FGELUUNOQJNL&pf_rd_p=3aefe545-f8d3-4562-976a-e5eb47d1bb18&pf_rd_r=2TNAA9FRS3TJWM3AEQ2X&pf_rd_s=center-1&pf_rd_t=60601&pf_rd_i=interfaces&ref_=fea_mn_lk1#))
What we can do is let you build the IMDB side of the entity resolution datasets yourself. Please be aware, that the mentioned license applies to the IMDB data you produce.

# Creating IMDB data
The TMDB and TVDB datasets are already provided and where created from the public APIs of [TheMovieDB](https://www.themoviedb.org/documentation/api) and [TVDB](https://www.thetvdb.com/api-information).
Running `python src/create_graph.py` downloads the IMDB data and creates the missing datasets.

# Dataset structure
There are 3 entity resolution tasks in this repository: imdb-tmdb, imdb-tvdb, tmdb-tvdb, all contained in the `data` folder. 
The data structure follows the structure used in [OpenEA](https://github.com/nju-websoft/OpenEA).
Each folder contains the information of the knowledge graphs (`attr_triples_*`,`rel_triples_*`) and the gold standard of entity links (`ent_links`). The triples are labeled with `1` and `2` where e.g. for imdb-tmdb `1` refers to imdb and `2` to tmdb. The folder 721_5fold contains pre-split entity link folds with 70-20-10 ratio for testing, training, validation.
