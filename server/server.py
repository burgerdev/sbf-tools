#!/usr/bin/env python3

import json
import hug
import random


from falcon import HTTPInvalidParam
from falcon import HTTPNotFound


class _Catalog:
    def __init__(self, file):
        self.catalog = json.load(file)
        self.keys = list(self.catalog.keys())
        file.close()

    def __getitem__(self, key):
        return self.catalog[key]


class _Site:
    def __init__(self, file):
        self.file = file

    @property
    def content(self):
        with open(self.file, 'r') as f:
            return f.read()
        

#FIXME waiting for data support in hug
global _catalog
global _site


@hug.get("/questions", versions=1)
def questions(number: hug.types.number):
    number = "{:d}".format(number)
    catalog = _get_catalog()
    if number not in catalog.keys:
        raise HTTPInvalidParam("(out of range)", "number")
    question = catalog[number]
    return question


@hug.get("/random", versions=1)
def rand():
    catalog = _get_catalog()
    key = random.choice(catalog.keys)
    question = catalog[key]
    return question


@hug.get("/site", versions=1, output=hug.output_format.html)
def site():
    site = _get_site()
    if site is None:
        raise HTTPNotFound()
    return site.content


def _get_catalog():
    global _catalog
    return _catalog


def _get_site():
    global _site
    return _site


if __name__ == "__main__":
    global _site
    global _catalog
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=argparse.FileType('r'))
    parser.add_argument("-s", "--site", type=str, default=None,
                        help="index.html to serve on '/v1/site', if needed")
    parser.add_argument("-p", "--port", type=int, default=8000,
                        help="port on which SBF-API will be served")

    args = parser.parse_args()

    _catalog = _Catalog(args.file)
    if args.site is not None:
        _site = _Site(args.site)

    __hug__.serve(port=args.port)
