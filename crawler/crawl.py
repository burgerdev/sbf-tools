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

from lxml import etree
from lxml import html
import json
import requests
import os
import io
import pprint

from urllib.parse import urljoin


import logging
LOGGER = logging.getLogger(__name__)


class Question:
    def __init__(self, number: int):
        self.number = int(number)
        self.text = ""
        self.resources = []
        self.answers = []

    def dictify(self):
        return {"type": "question", "number": self.number, "text": self.text,
                "resources": list(map(lambda x: x.dictify(), self.resources)),
                "answers": self.answers}

    def __str__(self):
        return str(self.dictify())


class Image:
    def __init__(self, base, src, alt="", title="", basedir=None):
        self.base = base
        self.alt = alt
        self.title = title
        self.basedir = basedir

        self.src = urljoin(self.base, src)
        name = self.src.split("/")[-1]
        if self.basedir is not None:
            self.target = os.path.join(self.basedir, name)
        else:
            self.target = name
        self.name = name

    def dictify(self):
        return {"type": "image", "remote_addr": self.src,
                "local_addr": self.target}

    def __str__(self):
        return str(self.dictify())


class StateMachine:

    def __init__(self, basedir=None, download=False):
        self._d = dict()
        self._current_question = None
        self._depth = 0
        self._download = download
        self._url = None
        self._basedir = basedir if basedir is not None else "."

    def store_catalog(self, mode="json"):
        catalog = self.catalog(mode=mode)
        with open(os.path.join(self._basedir, "catalog.json"), "w") as f:
            f.write(catalog)

    def catalog(self, mode="json"):
        if mode == "python":
            stream = io.StringIO()
            pprint.pprint(self._d, stream)
            return stream.getvalue()
        elif mode == "json":
            return json.dumps(self._d, sort_keys=True, indent=2)
        else:
            raise NotImplementedError("unknown mode '{}'".format(mode))

    def set_url(self, url):
        self._url = url

    def parse(self, root: etree.Element):
        if len(root) == 0:
            return
        for child in root:
            self.handle_element(child)

    def handle_element(self, elem: etree.Element):
        if elem.tag == "ol":
            self.handle_ol(elem)
        elif elem.tag == "li":
            self.handle_li(elem)
        elif elem.tag == "img":
            self.handle_img(elem)
        else:
            self.handle_other(elem)

    def handle_ol(self, ol: etree.Element):
        self._depth += 1
        n = int(ol.get("start"))

        if self._depth == 1:
            # this is a new question
            self._current_question = Question(int(n))

        self.parse(ol)

        if self._depth == 1:
            dict_ = self._current_question.dictify()
            self._d[dict_["number"]] = dict_

        self._depth -= 1

    def handle_li(self, li: etree.Element):
        if self._depth == 1:
            self._current_question.text = get_text(li)
        elif self._depth == 2:
            self._current_question.answers.append(get_text(li))
        self.parse(li)

    def handle_img(self, img: etree.Element):
        if self._depth < 1:
            # we don't wnat those images
            return

        img = Image(self._url, img.get("src"), alt=img.get("alt"),
                    title=img.get("title"), basedir=self._basedir)
        if self._download:
            req = requests.get(img.src)
            if req.status_code == 200:
                with open(img.target, "wb") as out_file:
                    out_file.write(req.content)
            else:
                LOGGER.error("Error {} while accessing {}".format(
                    req.status_code, img.src))
        self._current_question.resources.append(img)

    def handle_other(self, other: etree.Element):
        self.parse(other)


def get_text(node: etree.Element, stream: io.StringIO=None):
    """
    Extract text from this node and all children until an <ol> occurs
    """
    if stream is None:
        start = True
        stream = io.StringIO()
    else:
        start = False

    def to_xml(s: str):
        s = "" if s is None else s
        return s.encode('ascii', 'xmlcharrefreplace').decode()

    stream.write(to_xml(node.text))
    for child in node:
        if child.tag == "ol":
            break
        get_text(child, stream=stream)

    if start:
        # we are done, return the buffered string
        return stream.getvalue()
    else:
        # we are in a child, append our tail to the total string
        stream.write(to_xml(node.tail))


def main():
    import argparse
    logging.basicConfig()
    LOGGER.setLevel(logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--outputdir", action="store",
                        default="data",
                        help="directory to store crawled questions")
    parser.add_argument("-d", "--download", action="store_true",
                        default=False, help="download images")
    parser.add_argument("-m", "--mode", action="store",
                        default="json", help="output format (python/json)")

    args = parser.parse_args()

    sm = StateMachine(download=args.download, basedir=args.outputdir)

    urls = ["https://www.elwis.de/Freizeitschifffahrt/fuehrerscheininformationen/Fragenkatalog-See/Basisfragen/index.html",
            "https://www.elwis.de/Freizeitschifffahrt/fuehrerscheininformationen/Fragenkatalog-See/See/index.html"]

    for url in urls:
        LOGGER.info("Processing {}".format(url))
        req = requests.get(url)
        if req.status_code != 200:
            LOGGER.error("Error processing {}".format(url))
        else:
            tree = html.parse(io.BytesIO(req.content))
            sm.set_url(url)
            sm.parse(tree.getroot())
    sm.store_catalog(mode=args.mode)

if __name__ == "__main__":
    main()
