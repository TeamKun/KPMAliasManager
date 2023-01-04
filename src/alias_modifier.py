from os import path
from os import getcwd

import ijson
import git

import global_constants


def init_file_if_not_exists():
    if path.exists(global_constants.ALIASES_PATH):
        return
    with open(global_constants.ALIASES_PATH, "w", encoding="utf-8") as f:
        f.write("{}")


def is_alias_exists(alias_name):
    with open(global_constants.ALIASES_PATH, "r") as f:
        for prefix, event, value in ijson.parse(f):
            if event.startswith("map_key") and value == alias_name:
                return True

    return False


def add_alias(alias_name, query):
    size = path.getsize(global_constants.ALIASES_PATH)

    with open(global_constants.ALIASES_PATH, "r+") as f:
        if size > 4:
            f.seek(size - 2)
            f.write(",\n")
        else:
            f.seek(size - 2)
            f.write("\n")

        f.write(f'    "{alias_name}": "{query}"\n}}')

    commit_and_push_aliases(alias_name)


def commit_and_push_aliases(alias_name):
    repo = git.Repo(getcwd())
    repo.git.add(global_constants.ALIASES_PATH)
    repo.git.commit(message="Added new alias of \"{alias_name}\"".format(alias_name=alias_name))
    repo.git.push()

