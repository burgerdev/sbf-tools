#!/usr/bin/env python3

"""
Copyright (C) 2016 Markus Doering

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

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
