#!/usr/bin/env python3
"""
analyze_node_noise.py — general, dependency-free analyzer for tuning a
branchly crawler's `remove_html_elements` selectors.

WHY
---
Crawled node HTML almost always contains site-wide boilerplate (header, nav,
footer, cookie banner, teaser/CTA blocks, hashed CSS-module wrappers). This
pollutes embeddings and hurts retrieval. This script analyzes the HTML the
crawler actually ingested and tells you:

  1. which class tokens / tags appear on EVERY (or nearly every) page — the
     definition of boilerplate — and how much text each carries,
  2. a simulated cleaning: raw vs. clean text size per node (noise ratio),
  3. an over-strip guard: whether your key body phrases survive cleaning,
  4. the exact `[class*="..."]` selectors worth appending to
     `remove_html_elements`.

It is deliberately site-agnostic: nothing is hardcoded to any framework.
Anything that appears on many pages with substantial text is a boilerplate
candidate; verify candidates before stripping (see the over-strip guard).

INPUT
-----
Any of:
  - a JSON dump from `branchly_list_nodes(data_source_ids=[...])` — handles the
    persisted spillover shape `{"result": "<escaped json string>"}`. Nodes are
    read from `items`, each node's HTML from any string field (usually
    `text.<locale>`).
  - one or more raw HTML files (.html),
  - raw HTML on stdin.

USAGE
-----
    python3 scripts/analyze_node_noise.py node_dump.json
    python3 scripts/analyze_node_noise.py page1.html page2.html
    cat page.html | python3 scripts/analyze_node_noise.py

Options:
    --phrases "Phrase 1" "Phrase 2"   key body phrases that MUST survive
                                      cleaning (over-strip guard)
    --frequency 0.7                   candidate threshold: class token on >=70%
                                      of documents (default 0.7)
    --json                            machine-readable JSON output

Pure Python 3 standard library — no pip installs, no uv, no node packages.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from html.parser import HTMLParser

# Tags that never carry useful body content.
NOISE_TAGS = {"script", "style", "noscript", "svg", "iframe", "template"}
STRUCTURAL_TAGS = {"nav", "footer", "header", "aside", "form"}

# Tokens whose *presence* alone marks an element as boilerplate (universal).
UNIVERSAL_NOISE_TOKENS = ("cookie", "consent", "chat-widget", "branchly")

# Hashed CSS-module wrapper tokens (e.g. `Header-module__xYz12`) that wrap the
# real body content — never suggest stripping these.
WRAPPER_TOKEN_RE = re.compile(r"(^|[-_])module(__|$)|^[A-Za-z]+-module")


class DocParser(HTMLParser):
    """Builds a lightweight element tree using only the stdlib parser."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = {"tag": "#root", "classes": [], "children": [], "text": ""}
        self.stack = [self.root]
        self._in_script = 0

    def handle_starttag(self, tag, attrs):
        classes = []
        for k, v in attrs:
            if k == "class" and v:
                classes = v.split()
        node = {"tag": tag, "classes": classes, "children": [], "text": ""}
        self.stack[-1]["children"].append(node)
        if tag in NOISE_TAGS or self._in_script:
            self._in_script += 1
        elif tag not in ("br", "img", "hr", "input", "meta", "link"):
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if self._in_script and tag in NOISE_TAGS:
            pass  # self-closing script/style is unusual; treat as closed

    def handle_endtag(self, tag):
        if tag in NOISE_TAGS and self._in_script:
            self._in_script -= 1
        # pop back to a matching open tag if present (tolerant of bad HTML)
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i]["tag"] == tag:
                del self.stack[i:]
                break

    def handle_data(self, data):
        if self._in_script:
            return
        self.stack[-1]["text"] += data


def _strip_noise(node, tokens_lower, remove_structural):
    """Return (text, removed_chars) after removing noise subtrees in place."""
    kept_children = []
    removed = 0
    for child in node["children"]:
        cls = " ".join(child["classes"])
        cls_lower = cls.lower()
        drop = (
            child["tag"] in NOISE_TAGS
            or any(tok in cls_lower for tok in tokens_lower)
            or (remove_structural and child["tag"] in STRUCTURAL_TAGS)
        )
        if drop:
            removed += len(_all_text(child))
        else:
            sub_text, sub_removed = _strip_noise(
                child, tokens_lower, remove_structural
            )
            removed += sub_removed
            kept_children.append(child)
    node["children"] = kept_children
    text = node["text"] + " ".join(_all_text(c) for c in kept_children)
    return " ".join(text.split()), removed


def _all_text(node):
    return node["text"] + "".join(_all_text(c) for c in node["children"])


def _walk(node):
    yield node
    for c in node["children"]:
        yield from _walk(c)


def parse_html(raw: str):
    p = DocParser()
    try:
        p.feed(raw)
        p.close()
    except Exception:
        pass
    return p.root


def load_documents(args) -> list:
    """Return list of {"label", "html"} from node dump, files, or stdin."""
    paths = [a for a in args if not a.startswith("-")]
    flags = [a for a in args if a.startswith("-")]
    if "--help" in flags or "-h" in flags:
        print(__doc__)
        sys.exit(0)
    docs = []
    if not paths:
        raw = sys.stdin.read()
        if raw.strip():
            docs.append({"label": "<stdin>", "html": raw})
        return docs
    for path in paths:
        with open(path, encoding="utf-8", errors="replace") as f:
            content = f.read()
        if path.endswith(".json") or content.lstrip()[:1] in "{[":
            docs.extend(_docs_from_node_dump(content, path))
        else:
            docs.append({"label": path, "html": content})
    return docs


def _docs_from_node_dump(content: str, label: str) -> list:
    obj = json.loads(content)
    # Persisted list_nodes output is {"result": "<escaped json string>"}.
    if isinstance(obj, dict) and isinstance(obj.get("result"), str):
        obj = json.loads(obj["result"])
    items = obj.get("items", obj) if isinstance(obj, dict) else obj
    docs = []
    for it in items:
        html = ""
        for field in ("text", "content", "html", "body"):
            v = it.get(field)
            if isinstance(v, dict):  # e.g. {"de": "...", "en": "..."}
                html += " ".join(str(x) for x in v.values())
            elif isinstance(v, str):
                html += v
        title = it.get("title")
        if isinstance(title, dict):
            title = next(iter(title.values()), None)
        docs.append({"label": str(title or it.get("id") or "?"), "html": html})
    if not docs:
        raise SystemExit(f"no nodes found in {label}")
    return docs


def analyze(docs, phrases, freq_threshold):
    n_docs = len(docs)
    roots = [(d, parse_html(d["html"])) for d in docs]

    # 1) class-token frequency + text volume across documents
    token_docs = defaultdict(set)          # token -> set of doc indexes
    token_chars = Counter()                # token -> total text chars inside
    for idx, (_, root) in enumerate(roots):
        doc_chars = len(_all_text(root))
        for el in _walk(root):
            if not el["classes"]:
                continue
            # Element-level guards: an element carrying a hashed CSS-module
            # wrapper token, or holding most of the page's text, is a main
            # content container — never treat its tokens as boilerplate.
            if any(WRAPPER_TOKEN_RE.search(t) for t in el["classes"]):
                continue
            if doc_chars and len(_all_text(el)) > 0.6 * doc_chars:
                continue
            for tok in el["classes"]:
                if not tok or WRAPPER_TOKEN_RE.search(tok):
                    continue  # hashed wrapper token wraps the body — never strip
                token_docs[tok].add(idx)
                token_chars[tok] += len(_all_text(el))

    candidates = []
    for tok, docset in token_docs.items():
        frac = len(docset) / n_docs
        if frac >= freq_threshold and token_chars[tok] > 0:
            candidates.append({
                "token": tok,
                "docs": len(docset),
                "fraction": round(frac, 2),
                "chars": token_chars[tok],
            })
    candidates.sort(key=lambda c: -c["chars"])

    # 2) simulated cleaning per document, using structural tags + universal
    #    tokens + the top candidates from this very corpus
    tokens_lower = {c["token"].lower() for c in candidates} | set(
        t.lower() for t in UNIVERSAL_NOISE_TOKENS
    )
    per_doc = []
    total_raw = total_clean = 0
    for d, root in roots:
        raw_text = " ".join(_all_text(root).split())
        clean, _ = _strip_noise(root, tokens_lower, remove_structural=True)
        per_doc.append({
            "label": d["label"],
            "raw_chars": len(raw_text),
            "clean_chars": len(clean),
            "ratio": round(len(raw_text) / max(len(clean), 1), 2),
        })
        total_raw += len(raw_text)
        total_clean += len(clean)

    # 3) over-strip guard
    full_clean = " ".join(
        _all_text(_reparse_cleaned(d["html"], tokens_lower)) for d in docs
    )
    surviving = [p for p in phrases if p.lower() in full_clean.lower()]
    missing = [p for p in phrases if p not in surviving]

    return {
        "documents": n_docs,
        "total_raw_chars": total_raw,
        "total_clean_chars": total_clean,
        "noise_ratio": round(total_raw / max(total_clean, 1), 2),
        "boilerplate_candidates": candidates,
        "per_document": per_doc,
        "phrase_survival": {"surviving": surviving, "missing": missing},
    }


def _reparse_cleaned(raw, tokens_lower):
    """Re-parse raw HTML and return the root node with noise removed."""
    root = parse_html(raw)
    _strip_noise(root, tokens_lower, remove_structural=True)
    return root


def main():
    argv = sys.argv[1:]
    phrases = []
    freq = 0.7
    as_json = "--json" in argv
    args = []
    i = 0
    while i < len(argv):
        if argv[i] == "--phrases":
            i += 1
            while i < len(argv) and not argv[i].startswith("--"):
                phrases.append(argv[i])
                i += 1
        elif argv[i] == "--frequency":
            i += 1
            freq = float(argv[i]); i += 1
        else:
            args.append(argv[i]); i += 1
    docs = load_documents(args)
    if not docs:
        print("no input: pass a node_dump.json, HTML files, or pipe HTML to stdin",
              file=sys.stderr)
        sys.exit(2)
    result = analyze(docs, phrases, freq)

    if as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    r = result
    print(f"documents analyzed : {r['documents']}")
    print(f"text raw / clean   : {r['total_raw_chars']} / {r['total_clean_chars']} chars"
          f"  (noise ratio {r['noise_ratio']}x)")
    if phrases:
        print(f"phrase survival    : OK={r['phrase_survival']['surviving']}"
              f"  MISSING={r['phrase_survival']['missing']}")
    print("\nnoisiest documents (raw vs clean):")
    for d in sorted(r["per_document"], key=lambda x: -x["ratio"])[:10]:
        print(f"  {d['ratio']:6.1f}x  raw={d['raw_chars']:7d} clean={d['clean_chars']:6d}  {d['label'][:60]}")
    print(f"\nboilerplate candidates (on >= {int(freq * 100)}% of documents, ranked by text volume):")
    print("  → append to remove_html_elements as [class*=\"Token\"]")
    for c in r["boilerplate_candidates"][:25]:
        print(f"  {c['fraction']:4.0%} of docs  {c['chars']:8d} chars  {c['token']}")
    print("\nverify candidates first: re-run with --phrases \"<key body phrase>\" and")
    print("confirm your phrases survive; never strip hashed '-module' wrapper tokens.")


if __name__ == "__main__":
    main()
