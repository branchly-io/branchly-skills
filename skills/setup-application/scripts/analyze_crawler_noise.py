#!/usr/bin/env python3
"""
analyze_crawler_noise.py

Analyse the node HTML that the branchly website_crawler actually ingested and
help you decide what to put in `remove_html_elements`.

WHY
---
Framer/Next + Micado ("mco-*") tourism sites wrap real article text in lots of
site-wide boilerplate: hashed SCSS-module wrapper divs, CTA buttons, skip-links,
and bottom-of-page "recommendation card" teasers (TeaserSlider / TeaserList /
TeaserGrid / TeaserInformation / ParallaxTeaser ...). This pollutes dense
embeddings and distorts retrieval. This script tells you exactly which class
tokens are noise and which wrapper classes are load-bearing (must NOT be stripped).

INPUT
-----
A JSON dump produced by `branchly_list_nodes(data_source_ids=[...])` — i.e. the
persisted spillover file ({"result": "<escaped JSON string>"}).

USAGE
-----
    uv run --with beautifulsoup4 \
        python scripts/analyze_crawler_noise.py /path/to/node_dump.json

No project install is needed. `uv run --with beautifulsoup4` gives an ad-hoc
environment; nothing is pip-installed into the repo.

OUTPUT
------
For each node:
  - raw HTML length vs. cleaned text length (see the "clean vs. raw" ratio:
    tiny clean text at high raw length = noise-heavy).
  - counts of known noise marks.
  - whether key body phrases survive stripping (passes the "did I over-strip?"
    check).
  - ranked residual `class="..."` tokens on <a href> elements -> the exact new
    `[class*="..."]` selectors to append to `remove_html_elements`.
"""

import json
import re
import sys
from collections import Counter

from bs4 import BeautifulSoup

# Noise class tokens that are safe to strip via remove_html_elements
# `[class*="..."]` substring selectors (case-sensitive, matches hashed tokens).
KNOWN_NOISE_MARKS = [
    "BookingButton", "SkipLink", "mco-button", "mco-animation",
    "TeaserSlider", "TeaserList", "TeaserMasonry", "TeaserSingle",
    "TeaserGrid", "TeaserInformation", "ParallaxTeaser", "ListTeaser",
    "cookie", "Cookie", "branchly-", "chat-widget", "chat-embed",
    "search-interface", "footer", "header", "navigation",
]

# Tags stripped unconditionally.
NOISE_TAGS = ["script", "style", "noscript", "svg", "nav", "footer",
              "header", "iframe", "form"]

# Key body phrases to sanity-check survival; pass per-site via CLI if wanted.
DEFAULT_KEY_PHRASES = ["Skischule", "Wanderung", "Pistenspaß"]


def load_node_dump(path: str) -> list:
    with open(path) as f:
        obj = json.loads(f.read())
    # Persisted list_nodes output is {"result": "<escaped json string>"}.
    if "result" in obj:
        inner = obj["result"]
        if isinstance(inner, str):
            obj = json.loads(inner)
        else:
            obj = inner
    return obj.get("items", [])


def clean_text(raw: str):
    """Return (cleaned_text, n_stripped). Strips known noise, keeps body."""
    soup = BeautifulSoup(raw, "html.parser")
    for tag in soup(NOISE_TAGS):
        tag.decompose()
    for el in soup.find_all(True):
        attrs = el.attrs or {}
        cls = " ".join(attrs.get("class") or [])
        if any(mark in cls for mark in KNOWN_NOISE_MARKS):
            el.decompose()
    text = " ".join(soup.get_text(" ", strip=True).split())
    return text


def residual_link_class_tokens(items: list, top_n: int = 20) -> Counter:
    """Rank class tokens appearing on <a href> elements across nodes."""
    counter = Counter()
    for it in items:
        raw = ""
        for text in (it.get("text") or {}).values():
            raw += text
        soup = BeautifulSoup(raw, "html.parser")
        for a in soup.find_all("a", href=True):
            attrs = a.attrs or {}
            for tok in (attrs.get("class") or []):
                # Skip generic hashed SCSS wrapper tokens that legitimately wrap
                # the body content (never strip these). Keep any *novel* token so
                # new noise variants surface as candidates.
                if any(mark in tok for mark in
                       ["module-scss-module", "mco-container", "mco-elements",
                        "Default-module", "Elements-module", "Headline",
                        "Container-module", "Animation-module"]):
                    continue
                counter[tok] += 1
    return counter


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: analyze_crawler_noise.py <node_dump.json> [key_phrase, ...]")
        sys.exit(2)
    path = sys.argv[1]
    key_phrases = sys.argv[2:] or DEFAULT_KEY_PHRASES

    items = load_node_dump(path)
    print(f"nodes in dump: {len(items)}\n")

    noisy = 0
    for it in items:
        title = ((it.get("title") or {}).get("de")
                 or (it.get("title") or {}).get("en") or "?")
        raw = ""
        for text in (it.get("text") or {}).values():
            raw += text
        clean = clean_text(raw)
        marks = [m for m in KNOWN_NOISE_MARKS if m in raw]
        surviving = [p for p in key_phrases if p in clean]
        ratio = len(raw) / max(len(clean), 1)
        flag = "  <-- NOISY" if marks else ""
        print(f"[{title[:48]:48s}] raw={len(raw):7d} clean={len(clean):6d} "
              f"ratio={ratio:5.1f} marks={marks} surv={surviving}{flag}")
        if marks:
            noisy += 1

    print(f"\nnoisy nodes: {noisy}/{len(items)}")
    print("\nresidual class tokens on <a href> elements (ranked):")
    for tok, count in residual_link_class_tokens(items).most_common(20):
        print(f"  {count:4d}  {tok}")
    print("\n→ append new unique noise tokens to `remove_html_elements` as "
          "[class*=\"Tok\"]", end="\n")


if __name__ == "__main__":
    main()