#!/usr/bin/env python3
"""List Internet Archive snapshots of a URL, or diff the visible text of two.

Usage:
    wayback_diff.py <url>                         # list change-only snapshots
    wayback_diff.py <url> <timestamp_a> <timestamp_b>   # diff two captures

Timestamps are the 14-digit values (YYYYMMDDhhmmss) from the listing.
Standard library only.
"""
import sys
import json
import re
import difflib
import urllib.request
import urllib.parse

UA = "Firm Research wayback-diff (research@firm.example)"
CDX = ("http://web.archive.org/cdx/search/cdx?url={url}&output=json"
       "&fl=timestamp,original,statuscode,digest&collapse=digest")
SNAP = "https://web.archive.org/web/{ts}id_/{url}"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", "ignore")


def visible_text(html):
    html = re.sub(r"(?is)<(script|style|noscript).*?</\1>", " ", html)
    text = re.sub(r"(?s)<[^>]+>", " ", html)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"[ \t]+", " ", text)
    lines = [ln.strip() for ln in text.splitlines()]
    return [ln for ln in lines if ln]


def list_snapshots(url):
    rows = json.loads(fetch(CDX.format(url=urllib.parse.quote(url, safe=""))))
    if not rows:
        print("No snapshots found.")
        return
    header, *data = rows
    print(f"{len(data)} change-only snapshots for {url}\n")
    for ts, original, status, digest in data:
        print(f"  {ts}  status={status}")
    print("\nDiff two of them:")
    print(f"  python3 {sys.argv[0]} '{url}' <timestamp_a> <timestamp_b>")


def diff(url, ts_a, ts_b):
    a = visible_text(fetch(SNAP.format(ts=ts_a, url=url)))
    b = visible_text(fetch(SNAP.format(ts=ts_b, url=url)))
    out = difflib.unified_diff(a, b, fromfile=f"{ts_a}", tofile=f"{ts_b}", lineterm="")
    printed = False
    for line in out:
        if line[:1] in "+-" and line[:3] not in ("+++", "---"):
            printed = True
        print(line)
    if not printed:
        print("(no visible-text differences between these two captures)")


def main():
    if len(sys.argv) == 2:
        list_snapshots(sys.argv[1])
    elif len(sys.argv) == 4:
        diff(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
