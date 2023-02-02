#!/usr/bin/env python
"""Run all the example scripts, in a logical order with sleep time in between."""
import runpy
import time


def rest():
    """Sleep a second to be nice to Raindrop's API."""
    print("Resting...", end="", flush=True)
    time.sleep(1)
    print()


def run(path_name):
    """Run the py script at the specified path, waiting afterwards."""
    runpy.run_path(path_name=path_name)
    rest()


# Order: the first 3 are READ-ONLY, followed by Collection examples and then Raindrop ones.
run("examples/list_authorised_user.py")
run("examples/list_collections.py")
run("examples/list_tags.py")
run("examples/create_collection.py")
run("examples/edit_collection.py")
run("examples/create_raindrop_file.py")
run("examples/create_raindrop_link.py")
run("examples/edit_raindrop.py")
run("examples/search_raindrop.py")
