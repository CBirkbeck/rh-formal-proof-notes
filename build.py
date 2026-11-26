#!/usr/bin/env python3
"""Build the static pages from one text file per item.

Usage: python3 -I build.py ITEMS_DIR OUT_DIR [TALLY.json]

The environment variable DISCUSS_REPO (https://github.com/OWNER/REPO) turns on the links to the issue forms.
TALLY.json, written by tally.py, gives for each item how many readers said "known", "new" or "summary wrong".

An item file has header lines `key: value` (id, title, area, list, ai, astra, human_issue; `lean:` and `lit:`
may repeat), a blank line, then sections headed `## Name`. Sections named in TWISTY are rendered closed.
Nothing here reads the network. The repository names below are the only configuration.
"""
import html
import json
import os
import pathlib
import re
import sys

LEAN_REPO = "https://github.com/leanprover-community/riemann-hypothesis"
LEAN_COMMIT = "40e56bab026552e089d7afcfeff08d2defb9c005"
DISCUSS_REPO = os.environ.get("DISCUSS_REPO", "").rstrip("/")
TALLY = {}
LISTS = [
    ("results", "Results that may be of independent interest",
     "Statements inside the formal proof that the checks did not find in the literature, or found only in a "
     "weaker or different form."),
    ("routes", "Known theorems reached by another route",
     "Places where the formal proof supplies a standard theorem, or a case of one, by an argument that may "
     "differ from the published proof."),
]
TWISTY = {"How the formal proof goes", "Key steps", "What was checked, and what was not",
          "Nearest published work", "Second opinion"}
ORDER = ["Statement", "Why it might matter", "What the checks found", "Nearest published work", "Second opinion",
         "How the formal proof goes", "Key steps", "What was checked, and what was not"]


def inline(text):
    """Escape, then render `code`, **bold**, *italic* and [text](url)."""
    out, pos = [], 0
    for m in re.finditer(r"`([^`]+)`|\*\*([^*]+)\*\*|\[([^\]]+)\]\((https?://[^)\s]+)\)|\*([^*\s][^*]*)\*", text):
        out.append(html.escape(text[pos:m.start()]))
        if m.group(1) is not None:
            out.append("<code>" + html.escape(m.group(1)) + "</code>")
        elif m.group(2) is not None:
            out.append("<strong>" + html.escape(m.group(2)) + "</strong>")
        elif m.group(3) is not None:
            out.append('<a href="%s">%s</a>' % (html.escape(m.group(4), quote=True), html.escape(m.group(3))))
        else:
            out.append("<em>" + html.escape(m.group(5)) + "</em>")
        pos = m.end()
    out.append(html.escape(text[pos:]))
    return "".join(out)


def blocks(body):
    """Paragraphs and `- ` lists to HTML."""
    out, para, items = [], [], []

    def flush():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()
        if items:
            out.append("<ul>" + "".join("<li>" + inline(i) + "</li>" for i in items) + "</ul>")
            items.clear()

    for line in body.splitlines():
        s = line.rstrip()
        if not s.strip():
            flush()
        elif s.lstrip().startswith("- "):
            if para:
                flush()
            items.append(s.lstrip()[2:])
        elif items and line.startswith("  "):
            items[-1] += " " + s.strip()
        else:
            if items:
                flush()
            para.append(s.strip())
    flush()
    return "\n".join(out)


def parse(path):
    head, lean, lit, sections, cur = {}, [], [], {}, None
    lines = path.read_text(encoding="utf-8").splitlines()
    i = 0
    while i < len(lines) and lines[i].strip() and not lines[i].startswith("## "):
        key, _, val = lines[i].partition(":")
        key, val = key.strip(), val.strip()
        if key == "lean":
            lean.append([p.strip() for p in val.split("|")])
        elif key == "lit":
            lit.append(val)
        else:
            head[key] = val
        i += 1
    for line in lines[i:]:
        if line.startswith("## "):
            cur = line[3:].strip()
            sections[cur] = []
        elif cur is not None:
            sections[cur].append(line)
    return head, lean, lit, {k: "\n".join(v).strip() for k, v in sections.items()}


def lean_link(name, path, line, what):
    url = "%s/blob/%s/%s" % (LEAN_REPO, LEAN_COMMIT, path)
    if line.isdigit():
        url += "#L" + line
    return '<li><a href="%s"><code>%s</code></a> <span class="what">%s</span><br><span class="path">%s</span></li>' % (
        html.escape(url, quote=True), html.escape(name), inline(what), html.escape(path))


def chip(kind, text):
    cls = re.sub(r"[^a-z]+", "-", text.lower()).strip("-")
    return '<span class="chip %s %s">%s</span>' % (kind, cls, html.escape(text))


CSS = """
:root{--fg:#1c1c1c;--mute:#5d6470;--line:#d9dde3;--bg:#fff;--soft:#f5f6f8;--link:#1f4fa3}
@media (prefers-color-scheme:dark){:root{--fg:#e7e9ec;--mute:#9aa3ad;--line:#343a42;--bg:#15171a;--soft:#1e2125;--link:#8ab4ff}}
body{font:16px/1.55 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;color:var(--fg);background:var(--bg);margin:0}
main{max-width:860px;margin:0 auto;padding:28px 20px 80px}
a{color:var(--link)} h1{font-size:1.7rem;margin:.2em 0 .4em} h2{font-size:1.2rem;margin:1.6em 0 .4em}
h3{font-size:1.05rem;margin:1.2em 0 .3em} code{background:var(--soft);padding:.05em .3em;border-radius:4px;font-size:.92em}
.lede{color:var(--mute)} .card{border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:12px 0;background:var(--bg)}
.card h3{margin:0 0 .2em} .card p{margin:.3em 0} .meta{color:var(--mute);font-size:.9rem}
.chip{display:inline-block;font-size:.78rem;padding:.1em .6em;border-radius:999px;border:1px solid var(--line);margin:0 .35em .2em 0;background:var(--soft)}
.chip.ai{border-color:#7c93c6} .chip.astra{border-color:#b08fc7} .chip.human{border-color:#6fae84}
details{border:1px solid var(--line);border-radius:8px;margin:10px 0;padding:0 14px;background:var(--bg)}
details>summary{cursor:pointer;font-weight:600;padding:10px 0} details[open]>summary{border-bottom:1px solid var(--line);margin-bottom:8px}
ul.lean{list-style:none;padding:0} ul.lean li{margin:.5em 0} .path{color:var(--mute);font-size:.82rem;word-break:break-all} .what{color:var(--mute)}
.note{background:var(--soft);border-left:3px solid var(--line);padding:10px 14px;border-radius:6px;font-size:.95rem}
.actions a{display:inline-block;margin:.3em .6em .3em 0;padding:.35em .8em;border:1px solid var(--line);border-radius:8px;text-decoration:none}
footer{color:var(--mute);font-size:.88rem;margin-top:3em;border-top:1px solid var(--line);padding-top:1em}
"""


def page(title, body):
    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>%s</title>"
            "<style>%s</style></head><body><main>%s</main></body></html>") % (html.escape(title), CSS, body)


FOOT = ("<footer>Every summary and verdict on these pages was written by AI models reading the Lean source and the "
        "literature, and has not been checked by a specialist unless a comment says so. The formal proof belongs to "
        "its author; these pages link to it and describe it, and copy none of it.</footer>")


def discuss(head, kind):
    if not DISCUSS_REPO:
        return ""
    new = DISCUSS_REPO + "/issues/new?template="
    if kind == "index":
        links = ['<a href="%snew-item.yml">Propose an item</a>' % new,
                 '<a href="%s/issues">What readers have said</a>' % DISCUSS_REPO]
    else:
        item = html.escape(head.get("id", ""), quote=True)
        links = ['<a href="%sknown.yml&amp;item=%s&amp;title=%%5B%s%%5D+known%%3A+">This is known: give the reference</a>'
                 % (new, item, item),
                 '<a href="%snew.yml&amp;item=%s&amp;title=%%5B%s%%5D+new%%3A+">I think this is new</a>' % (new, item, item),
                 '<a href="%scorrection.yml&amp;item=%s&amp;title=%%5B%s%%5D+correction%%3A+">The summary is wrong</a>'
                 % (new, item, item),
                 '<a href="%s/issues?q=is%%3Aissue+%s+in%%3Atitle%%2Cbody">What readers have said</a>'
                 % (DISCUSS_REPO, item)]
    return '<p class="actions">' + " ".join(links) + "</p>"


def chips(head):
    out = []
    if head.get("ai"):
        out.append(chip("ai", "First reading: " + head["ai"]))
    if head.get("astra"):
        out.append(chip("astra", "Second opinion: " + head["astra"]))
    said = TALLY.get(head.get("id", ""), {})
    words = [("known", "known"), ("new", "new"), ("correction", "summary wrong")]
    parts = ["%d %s" % (said[k], w) for k, w in words if said.get(k)]
    if parts:
        out.append(chip("human", "Readers: " + ", ".join(parts)))
    return "".join(out)


def main(items_dir, out_dir, tally=None):
    if tally and pathlib.Path(tally).exists():
        TALLY.update(json.loads(pathlib.Path(tally).read_text(encoding="utf-8")))
    out = pathlib.Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    items = []
    for path in sorted(pathlib.Path(items_dir).glob("*.md")):
        if path.name.endswith(".notes.md"):
            continue
        head, lean, lit, sections = parse(path)
        if "id" not in head or "title" not in head:
            print("skipped (no id or title):", path.name)
            continue
        head.setdefault("list", "results" if head["id"].startswith("A") else "routes")
        items.append((head, lean, lit, sections))
        body = ['<p><a href="index.html">All items</a></p>', "<h1>%s</h1>" % inline(head["title"]),
                '<p class="meta">%s · %s</p>' % (html.escape(head["id"]), html.escape(head.get("area", ""))),
                "<p>%s</p>" % chips(head), discuss(head, "item")]
        if lean:
            body.append("<h2>In the Lean source</h2><ul class=\"lean\">%s</ul>" % "".join(
                lean_link(*(l + ["", "", "", ""])[:4]) for l in lean))
        names = [n for n in ORDER if n in sections] + [n for n in sections if n not in ORDER]
        for name in names:
            content = blocks(sections[name])
            if name == "Nearest published work" and lit:
                content += "<ul>" + "".join("<li>" + inline(x) + "</li>" for x in lit) + "</ul>"
            if name in TWISTY:
                body.append("<details><summary>%s</summary>%s</details>" % (html.escape(name), content))
            else:
                body.append("<h2>%s</h2>%s" % (html.escape(name), content))
        body.append(FOOT)
        (out / (head["id"] + ".html")).write_text(page(head["title"], "\n".join(body)), encoding="utf-8")
    body = ["<h1>Inside the formal proof: what may be new</h1>",
            '<p class="lede">Results and arguments found inside the formal Lean proof of the Riemann hypothesis for '
            "Dirichlet L-functions, each with a link to the Lean code, a plain-language account of what it says and "
            "how its proof goes, and what two AI models make of its novelty. Say what you know: is it new, is it in "
            "the literature, is the summary wrong?</p>", discuss({}, "index")]
    for key, title, lede in LISTS:
        group = [it for it in items if it[0]["list"] == key]
        if not group:
            continue
        body.append("<h2>%s</h2><p class=\"lede\">%s</p>" % (html.escape(title), html.escape(lede)))
        for head, lean, lit, sections in group:
            first = sections.get("Statement", "").split("\n\n")[0]
            body.append('<div class="card"><h3><a href="%s.html">%s</a></h3><p class="meta">%s · %s</p><p>%s</p>'
                        "<p>%s</p></div>" % (html.escape(head["id"]), inline(head["title"]), html.escape(head["id"]),
                                             html.escape(head.get("area", "")), chips(head),
                                             inline(" ".join(first.split())[:420])))
    body.append(FOOT)
    (out / "index.html").write_text(page("Inside the formal proof: what may be new", "\n".join(body)),
                                    encoding="utf-8")
    print("built", len(items), "items into", out)


if __name__ == "__main__":
    main(*sys.argv[1:4])
