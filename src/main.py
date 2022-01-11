import os
import shutil
import sys
from pathlib import Path


def main(folder_loc: str = "ScaDSMovieGraphBenchmark"):
    target_loc = Path(folder_loc)
    # create target paths parents if they don't exist
    if not target_loc.parent == Path(".") and not os.path.exists(target_loc.parent):
        os.makedirs(target_loc.parent)
    print("Downloading repo")
    os.system("git clone https://github.com/ScaDS/MovieGraphBenchmark.git")
    os.chdir("MovieGraphBenchmark")
    print("Creating IMDB data")
    os.system("python3 src/create_graph.py")
    print("Cleanup")
    os.chdir("..")
    shutil.move("MovieGraphBenchmark/data", target_loc)
    shutil.rmtree("MovieGraphBenchmark")
    print("Done!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
