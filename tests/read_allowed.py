import pathlib
import os

def read_allowed_lists_from_resources():
    res_path = pathlib.Path(__file__).parent.joinpath("resources").absolute()
    allowed_lists = []
    for allowed in ["allowed_episode","allowed_film", "allowed_name", "allowed_show"]:
        with open(os.path.join(res_path, allowed), "r") as in_file:
            allowed_lists.append([line.strip() for line in in_file])
    return allowed_lists
