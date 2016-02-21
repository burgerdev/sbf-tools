#!/usr/bin/env python3

import os
import json
import hug
from falcon import HTTPInvalidParam

_catalog = None
_env = "SBF_FILE"


@hug.get("/questions", versions=1)
def questions(number: hug.types.number):
    number = "{:d}".format(number)
    catalog = _get_catalog()
    if number not in catalog:
        raise HTTPInvalidParam("(out of range)", "number")
    question = catalog[number]
    return question


def _get_catalog():
    global _catalog
    if _catalog is None:
        _fill_catalog()
    return _catalog


def _fill_catalog():
    global _catalog
    if os.environ[_env] == "":
        raise RuntimeError("need environment variable {}".format(_env))
    with open(os.environ[_env], "r") as file:
        _catalog = json.load(file)

if __name__ == "__main__":
    _fill_catalog()
    __hug__.serve()
