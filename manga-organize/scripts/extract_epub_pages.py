#!/usr/bin/env python3
"""Preview or extract original raster pages from a simple image-only EPUB, in spine order."""
import argparse
import json
from pathlib import Path
import posixpath
import shutil
import sys
from urllib.parse import unquote, urlsplit
from zipfile import ZipFile

from lxml import etree

from comicapi.book import open_book
from pack_cbz import IMAGE_FORMATS

XHTML = "{http://www.w3.org/1999/xhtml}"
SVG = "{http://www.w3.org/2000/svg}"
XLINK_HREF = "{http://www.w3.org/1999/xlink}href"
WRAPPERS = {XHTML + tag for tag in ("body", "div", "p", "span", "section", "figure")} | {SVG + "svg"}


def raster_member(archive, resource):
    if Path(resource).suffix.lower() in IMAGE_FORMATS:
        archive.getinfo(resource)
        return resource
    parser = etree.XMLParser(resolve_entities=False, no_network=True)
    with archive.open(resource) as document:
        root = etree.parse(document, parser).getroot()
    body = root.find(XHTML + "body") if root.tag == XHTML + "html" else root
    if body is None or body.tag not in {XHTML + "body", SVG + "svg"}:
        raise ValueError(f"Unsupported EPUB page document: {resource}")
    if any(text.strip() for text in body.itertext()):
        raise ValueError(f"Page contains text in addition to its image: {resource}")

    refs = []
    for element in body.iter():
        if isinstance(element, etree._Comment):
            continue
        if "transform" in element.attrib or "{http://www.w3.org/XML/1998/namespace}base" in element.attrib:
            raise ValueError(f"Page uses a transform or a base URL: {resource}")
        if element.tag == XHTML + "img":
            if element.get("srcset"):
                raise ValueError(f"Page has alternate image sources: {resource}")
            refs.append(element.get("src"))
        elif element.tag == SVG + "image":
            refs.append(element.get("href") or element.get(XLINK_HREF))
        elif element.tag not in WRAPPERS:
            raise ValueError(f"Unsupported page element in {resource}: {element.tag}")
    if len(refs) != 1 or not refs[0]:
        raise ValueError(f"Page must reference exactly one raster image: {resource}")

    link = urlsplit(refs[0])
    decoded = unquote(link.path)
    if link.scheme or link.netloc or link.query or link.fragment or decoded.startswith("/") or "\\" in decoded:
        raise ValueError(f"Page image is not a simple local resource: {resource}")
    member = posixpath.normpath(posixpath.join(posixpath.dirname(resource), decoded))
    if member == ".." or member.startswith("../") or Path(member).suffix.lower() not in IMAGE_FORMATS:
        raise ValueError(f"Unsupported raster resource in {resource}")
    archive.getinfo(member)
    return member


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("epub", type=Path)
    parser.add_argument("pages", type=Path, help="Existing empty directory for original page images")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    created = []
    try:
        if args.pages.is_symlink() or not args.pages.is_dir() or any(args.pages.iterdir()):
            raise ValueError("Choose a real, empty page staging directory.")
        book = open_book(args.epub)
        if book.format != "epub":
            raise ValueError("The input is not EPUB.")
        if not book.capabilities.copy_write:
            raise ValueError(book.capabilities.reason or "Unsupported EPUB package.")
        units = book.units()
        if not units:
            raise ValueError("The EPUB has no reading units.")
        width = max(4, len(str(len(units))))
        with ZipFile(args.epub) as archive:
            plan = []
            for index, unit in enumerate(units, 1):
                resource = raster_member(archive, unit.resource)
                plan.append({
                    "spine": unit.resource,
                    "resource": resource,
                    "page": f"{index:0{width}d}{Path(resource).suffix.lower()}",
                })
            if args.apply:
                for item in plan:
                    path = args.pages / item["page"]
                    with archive.open(item["resource"]) as src, path.open("xb") as dst:
                        created.append(path)
                        shutil.copyfileobj(src, dst)
        print(json.dumps({"written": args.apply, "page_count": len(plan), "pages": plan}, ensure_ascii=False, indent=2))
    except (OSError, ValueError, KeyError, etree.XMLSyntaxError) as exc:
        for path in created:
            path.unlink()
        print(f"extract_epub_pages: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
