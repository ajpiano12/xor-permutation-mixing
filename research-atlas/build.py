# /// script
# requires-python = ">=3.10"
# dependencies = ["pypandoc-binary==1.15"]
# ///
"""Build portable atlas data and HTML evidence pages from the research repository."""

import csv
import gzip
import hashlib
import html
from io import StringIO
import json
from pathlib import Path
import posixpath
import re
from urllib.parse import urlsplit

import pypandoc

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DIST = HERE / "dist"
CATALOG = HERE / "topics.json"
DOCUMENTS = (
    "README.md", "FOUR_BIT_COUNT.md", "LARGER_BITS.md", "CIRCUIT_INPUT.md", "FAST_TABLE_PROOF.md",
    "research/LITERATURE_REVIEW.md", "research/GROUP_COUNTS.md", "research/FIVE_BIT_COUNT.md",
    "research/ALGORITHMIC_PRIOR_ART.md", "research/HIGHER_CENSUS.md", "research/RATES_AND_LITERATURE.md",
    "research/QUADRATIC_CERTIFICATE.md", "research/TRIPLE_ROUNDS.md",
    "research/TRIPLE_MOMENT.md", "research/TRIPLE_LOWER.md", "research/INVERSE_TRIPLE_RATE.md",
    "research/BRIEF_AND_PROGRESS.md", "research/POWER_CERTIFICATE.md", "research/STRUCTURED_SMALL_ERROR.md",
    "research/SPECTRAL_CERTIFICATE.md", "research/POLYNOMIAL_UPDATE.md", "research/SMALL_ERROR_DATA.md",
)
PROGRAMS = ("mixing.py", "exact_four_bit.py", "four_bit_obstructions.py", "sample_four_bit.py",
            "verify_rate_bins.py", "classify_mixing.py", "fast_mixing.py", "parallel_mixing.c", "parity_screen.py",
            "group_mixing.py", "higher_census.py", "quadratic_mixing.py", "inverse_triples.py",
            "research/group_counts.py", "research/triple_moment.py", "research/triple_lower.py", "research/triple_probe.py", "research/rate_probe.py",
            "power_mixing.py", "research/spectral_certificate.py", "research/structured_probe.py",
            "research/small_error_census.py")
DATA = ("results/summary.csv", "results/permutations.csv", "results/four_bit/summary.json",
        "results/four_bit/samples.csv", "results/four_bit/convergence.png",
        "results/higher_three_bit.csv", "results/triple_probe.csv", "results/small_error_times.csv")
COMPRESS = {"results/permutations.csv", "results/four_bit/samples.csv"}


def asset_url(source):
    if source in DOCUMENTS:
        return "library/" + Path(source).stem.lower() + ".html"
    if source in PROGRAMS:
        return "library/" + Path(source).name + ".html"
    if source in DATA:
        return "library/" + source + (".gz" if source in COMPRESS else "")
    if source in ("research-atlas/", "research-atlas/dist/index.html"):
        return "index.html"
    raise ValueError(f"No atlas asset for repository link {source}")


def local_link(href, relative_to="", source_dir=""):
    url = urlsplit(href)
    if url.scheme in ("http", "https", "mailto") or not url.path:
        return href
    if url.scheme or url.netloc:
        raise ValueError(f"Unsupported link {href}")
    path = posixpath.normpath(posixpath.join(source_dir, url.path))
    if path == "research-atlas":
        path += "/"
    target = posixpath.relpath(asset_url(path), relative_to or ".")
    return target + ("#" + url.fragment if url.fragment else "")


def write_if_changed(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = content.encode() if isinstance(content, str) else content
    if not path.exists() or path.read_bytes() != data:
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_bytes(data)
        tmp.replace(path)


def write_output(url, text):
    write_if_changed(DIST / url, text)


def result_fields(data):
    summary = json.loads(data["results/four_bit/summary.json"])
    counts = {}
    for row in csv.DictReader(StringIO(data["results/summary.csv"].decode())):
        if row["epsilon_exact"] == "1/4":
            name = row["status"]
            counts[name] = counts.get(name, 0) + int(row["permutations"])
    total = sum(counts.values())
    if total != 40320:
        raise ValueError("The three-bit census at ε=1/4 must account for all 8! tables")
    last = str(summary["profile_rounds"])
    return dict(threeTotal=f"{total:,}", threeMix=f"{counts['mixing']:,}",
                threeDisconnected=f"{counts['disconnected']:,}", threePeriodic=f"{counts['periodic']:,}",
                threePercent=f"{counts['mixing']/total:.0%}", fourTotal=f"{summary['draws']:,}",
                fourMix=f"{summary['status_counts']['mixing']:,}",
                fourCurves=f"{summary['distinct_exact_profiles_through_round'][last]:,}",
                fourProfileRounds=last)


def reader_page(title, contents, filename, kind, headings=()):
    toc_items = "".join(f'<li><a href="#{html.escape(anchor)}">{html.escape(name)}</a></li>'
                        for anchor, name in headings)
    toc = (f'<nav class="toc" aria-label="Sections"><h2>On this page</h2><ul>{toc_items}</ul></nav>'
           if toc_items else "")
    name = html.escape(filename)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#122f35"><title>{html.escape(title)} · Difference Atlas</title>
<link rel="icon" href="../mark.svg"><link rel="stylesheet" href="../reader.css"></head>
<body><a class="skip" href="#document">Skip to document</a><header><div class="bar">
<a class="brand" href="../index.html#map"><img src="../mark.svg" width="33" height="33" alt="">Difference Atlas</a>
<nav aria-label="Atlas"><a href="../index.html#map">Research map</a><a href="../index.html#library">Proof library</a></nav>
</div></header><div class="layout"><aside><div class="meta">{kind}</div>
<p class="filename">{name}</p><a download="{name}" href="raw/{name}">Download source</a>{toc}</aside>
<main id="document" tabindex="-1">{contents}</main></div></body></html>
"""


def render_document(filename, source, url):
    # Pandoc emits native MathML. The browser needs no scripts, fonts or network to typeset formulas.
    body = pypandoc.convert_text(source, to="html5", format="gfm+tex_math_dollars",
                                 extra_args=["--mathml", "--wrap=none", "--no-highlight"])
    def rewrite(match):
        attr, href = match.groups()
        return f'{attr}="{html.escape(local_link(html.unescape(href), "library", posixpath.dirname(filename)), quote=True)}"'
    body = re.sub(r'\b(href|src)="([^"]*)"', rewrite, body)
    headings = [(anchor, html.unescape(re.sub("<[^>]+>", "", label)))
                for anchor, label in re.findall(r'<h2 id="([^"]+)">(.*?)</h2>', body, re.S)]
    title = source.splitlines()[0].removeprefix("# ")
    write_output(url, reader_page(title, body, Path(filename).name, "Research note", headings))
    write_output("library/raw/" + Path(filename).name, source)


def catalog_for_site(data, fields):
    # Expanding only explicit placeholders keeps source links and provenance notes under editorial control.
    catalog = json.loads(re.sub(r"\$\{(\w+)\}", lambda token: fields[token[1]], data))
    branch_ids = {b["id"] for b in catalog["branches"]}
    source_ids = {s["id"] for s in catalog["sources"]}
    for collection in ("branches", "topics", "sources"):
        ids = [v["id"] for v in catalog[collection]]
        if len(ids) != len(set(ids)):
            raise ValueError(f"Duplicate IDs in {collection}")
    for topic in catalog["topics"]:
        if topic["branch"] not in branch_ids or not set(topic["sourceIds"]) <= source_ids:
            raise ValueError(f"Unknown branch or source in {topic['id']}")
        for resource in topic["resources"]:
            resource["href"] = local_link(resource["href"])
    return catalog


def main():
    blobs = {name: (ROOT / name).read_bytes() for name in (*DOCUMENTS, *PROGRAMS, *DATA)}
    catalog_text = CATALOG.read_text()
    catalog = catalog_for_site(catalog_text, result_fields(blobs))
    digest = hashlib.sha256(catalog_text.encode())
    for name, content in blobs.items():
        digest.update(name.encode() + b"\0" + hashlib.sha256(content).digest())
        if name in DOCUMENTS:
            render_document(name, content.decode(), asset_url(name))
        elif name in PROGRAMS:
            markup = f"<h1>{html.escape(name)}</h1><pre><code>{html.escape(content.decode())}</code></pre>"
            write_output(asset_url(name), reader_page(name, markup, Path(name).name, "Source code"))
            write_output("library/raw/" + Path(name).name, content)
        else:
            write_output(asset_url(name), gzip.compress(content, mtime=0) if name in COMPRESS else content)
    # A renamed section in a proof must surface before a refreshed topic links to it.
    anchors = {}
    for topic in catalog["topics"]:
        for resource in topic["resources"]:
            url = urlsplit(resource["href"])
            if url.scheme:
                continue
            file = DIST / url.path
            if not file.is_file():
                raise ValueError(f"Missing evidence in {topic['id']}: {resource['href']}")
            if url.fragment and file.suffix == ".html":
                if file not in anchors:
                    anchors[file] = set(re.findall(r'\bid="([^"]+)"', file.read_text()))
                if url.fragment not in anchors[file]:
                    raise ValueError(f"Missing section in {topic['id']}: {resource['href']}")
    catalog["snapshot"] = {"date": catalog.pop("reviewed"), "revision": digest.hexdigest()[:10]}
    output = json.dumps(catalog, ensure_ascii=False, indent=2).replace("</", "<\\/")
    write_output("data.js", "window.ATLAS = " + output + ";\n")
    print(f"Built {len(catalog['topics'])} topics, {len(DOCUMENTS)} research notes and {len(PROGRAMS)} code pages.")


if __name__ == "__main__":
    main()
