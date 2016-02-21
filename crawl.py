#!/usr/bin/env python

from lxml import etree
from lxml import html
import json
import requests
import os
import sys
import io
import pprint

from urllib.parse import urljoin


local = "data"


def log2(msg: str):
    print(msg, file=sys.stderr)


class Question:
    def __init__(self, number: int):
        self.number = number
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
    def __init__(self, base, src, alt="", title=""):
        self.base = base
        self.alt = alt
        self.title = title
        self.adjust_source(src)

    def adjust_source(self, relative_src):
        self.src = urljoin(self.base, relative_src)
        name = self.src.split("/")[-1]
        self.target = os.path.join(local, name)

    def dictify(self):
        return {"type": "image", "remote_addr": self.src,
                "local_addr": self.target}

    def __str__(self):
        return str(self.dictify())


class StateMachine:

    def __init__(self, download=False):
        self._d = dict()
        self._current_question = None
        self._depth = 0
        self._download = download
        self._url = None

    def catalog(self, mode="json"):
        if mode == "python":
            stream = io.StringIO()
            pprint.pprint(self._d, stream)
            return stream.getvalue()
        elif mode == "json":
            return json.dumps(self._d)
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
        n = ol.get("start")

        if self._depth == 1:
            # this is a new question
            self._current_question = Question(int(n))

        self.parse(ol)

        if self._depth == 1:
            dict_ = self._current_question.dictify()
            self._d[self._current_question.number] = dict_

        self._depth -= 1

    def handle_li(self, li: etree.Element):
        if self._depth == 1:
            self._current_question.text = self.parse_text(li.text)
        elif self._depth == 2:
            self._current_question.answers.append(self.parse_text(li.text))
        self.parse(li)

    def handle_img(self, img: etree.Element):
        if self._depth < 1:
            # we don't wnat those images
            return

        img = Image(self._url, img.get("src"), alt=img.get("alt"),
                    title=img.get("title"))
        if self._download:
            req = requests.get(img.src)
            if req.status_code == 200:
                with open(img.target, "wb") as out_file:
                    out_file.write(req.content)
            else:
                log2("Error {} while accessing {}".format(req.status_code,
                                                          img.src),
                     file=sys.stderr)
        self._current_question.resources.append(img)

    def handle_other(self, other: etree.Element):
        self.parse(other)

    def parse_text(self, text: str):
        return text


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="+", type=argparse.FileType('r'))
    parser.add_argument("-o", "--output", type=argparse.FileType('w'),
                        default=sys.stdout)
    parser.add_argument("-d", "--download", action="store_true",
                        default=False, help="download images")
    parser.add_argument("-m", "--mode", action="store",
                        default="json", help="output format (python/json)")

    args = parser.parse_args()

    def log(msg: str):
        print(msg, file=args.output)

    sm = StateMachine(download=args.download)

    urls = ["https://www.elwis.de/Freizeitschifffahrt/fuehrerscheininformationen/Fragenkatalog-See/Basisfragen/index.html",
            "https://www.elwis.de/Freizeitschifffahrt/fuehrerscheininformationen/Fragenkatalog-See/See/index.html"]
    
#    for file in args.file:
#        log2("Processing {}".format(file.name))
#        tree = parse(file)
#        sm.parse(tree.getroot())

    for url in urls:
        log2("Processing {}".format(url))
        req = requests.get(url)
        if req.status_code != 200:
            log2("Error processing {}".format(url))
        else:
            tree = html.parse(io.BytesIO(req.content))
            sm.set_url(url)
            sm.parse(tree.getroot())
        
    args.output.write(sm.catalog(mode=args.mode))

if __name__ == "__main__":
    main()
