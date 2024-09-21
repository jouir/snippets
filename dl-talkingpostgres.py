#!/usr/bin/env python
# Download Talking Postgres podcast
# https://talkingpostgres.com/

import json
import os
import feedparser
import requests
from time import mktime
from unidecode import unidecode

from pprint import pprint


def convert_title(title):
    """Replace special characters in a title"""
    m = {
        ")": "",
        "(": "",
        "_": "-",
        "&": "",
        " ": "-",
        "'": "",
        "/": "",
        ":": "",
        "--": "-",
    }
    for i in m:
        title = title.replace(i, m[i])
    title = unidecode(title)
    return title.lower()


def download(url, filename, timestamp):
    print(f"Downloading {url} to {filename}")
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    os.utime(filename, (timestamp, timestamp))


def main():
    feed = feedparser.parse("https://feeds.transistor.fm/talkingpostgres")

    for entry in feed["entries"]:
        title = convert_title(entry["title"])
        timestamp = entry["published_parsed"]
        date = f"{timestamp.tm_year:04}-{timestamp.tm_mon:02}-{timestamp.tm_mday:02}"
        url = None

        for link in entry["links"]:
            if link["type"] == "audio/mpeg":
                url = link["href"]

        if not url:
            print("Could not find url")
            pprint(entry)
            continue

        filename = f"{date}-{title}.mp3"
        if not os.path.isfile(filename):
            try:
                download(url, filename, mktime(timestamp))
            except KeyboardInterrupt:
                if os.path.isfile(filename):
                    os.unlink(filename)
                break


if __name__ == "__main__":
    main()
