#!/usr/bin/env python3
"""Preview or losslessly pack one volume of local page images into a CBZ."""
import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from zipfile import ZIP_STORED, ZipFile

from PIL import Image

IMAGE_FORMATS = {
    ".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".gif": "GIF",
    ".webp": "WEBP", ".avif": "AVIF",
}


def checked_page(root, name):
    if not isinstance(name, str) or "\\" in name:
        raise ValueError(f"Invalid relative page path: {name!r}")
    relative = PurePosixPath(name)
    if not relative.parts or relative.is_absolute() or ".." in relative.parts or relative.as_posix() != name:
        raise ValueError(f"Invalid relative page path: {name!r}")
    if any(part.startswith(".") for part in relative.parts) or relative.suffix.lower() not in IMAGE_FORMATS:
        raise ValueError(f"Unsupported page path: {name!r}")
    path = root
    for part in relative.parts:
        path = path / part
        if path.is_symlink():
            raise ValueError(f"Page path contains a symbolic link: {path}")
    if not path.is_file():
        raise ValueError(f"Page is not a regular file: {path}")
    return path


def page_paths(root, order):
    if order:
        names = json.loads(order.read_text(encoding="utf-8"))
        if not isinstance(names, list) or not names:
            raise ValueError("The order file must contain a nonempty JSON array of relative image paths.")
        paths = [checked_page(root, name) for name in names]
        if len(set(paths)) != len(paths):
            raise ValueError("The order file lists a page more than once.")
        return paths

    entries = [p for p in root.iterdir() if not p.name.startswith(".")]
    if any(p.is_dir() or p.is_symlink() for p in entries):
        raise ValueError("Nested folders or symbolic links require an explicit page order.")
    if any(p.suffix.lower() not in IMAGE_FORMATS for p in entries):
        raise ValueError("Review non-page files or unsupported images and supply --order.")
    paths = [checked_page(root, p.name) for p in entries]
    if not paths:
        raise ValueError("No supported page images found.")
    if len(paths) == 1:
        return paths
    numbered = [(re.fullmatch(r"(.*?)([0-9]+)", p.stem), p) for p in paths]
    if any(match is None for match, _ in numbered):
        raise ValueError("Page names do not share a numeric sequence. Supply --order.")
    prefixes = {match[1].casefold() for match, _ in numbered}
    sequence = {int(match[2]): path for match, path in numbered}
    if len(prefixes) != 1 or len(sequence) != len(paths):
        raise ValueError("Mixed prefixes or duplicate page numbers. Supply --order.")
    return [sequence[number] for number in sorted(sequence)]


def write_cbz(plan, output):
    with TemporaryDirectory(prefix=".pack-cbz-", dir=output.parent) as tmp:
        draft = Path(tmp) / output.name
        digests = {}
        with ZipFile(draft, "x", compression=ZIP_STORED) as archive:
            for source, entry in plan:
                with source.open("rb") as stream:
                    before = os.fstat(stream.fileno())
                    with Image.open(stream) as page:
                        if page.format != IMAGE_FORMATS[source.suffix.lower()]:
                            raise ValueError(f"Image content does not match its extension: {source}")
                        page.verify()
                    stream.seek(0)
                    digest = hashlib.sha256()
                    with archive.open(entry, "w", force_zip64=before.st_size >= 2**31) as member:
                        while chunk := stream.read(1024 * 1024):
                            member.write(chunk)
                            digest.update(chunk)
                    after = source.stat()
                    if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
                        after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns
                    ):
                        raise ValueError(f"Source image changed while packing: {source}")
                    digests[entry] = digest.hexdigest()
        with ZipFile(draft) as archive:
            if archive.namelist() != list(digests):
                raise ValueError("CBZ reading order changed.")
            for entry, digest in digests.items():
                with archive.open(entry) as member:
                    if hashlib.file_digest(member, "sha256").hexdigest() != digest:
                        raise ValueError(f"CBZ page failed readback: {entry}")
        os.link(draft, output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pages", type=Path, help="Directory containing the page images of one volume")
    parser.add_argument("output", type=Path, help="New .cbz file outside the source directory")
    parser.add_argument("--order", type=Path, help="JSON array of relative page paths, in reading order")
    parser.add_argument("--apply", action="store_true", help="Write the verified CBZ. Default is preview.")
    args = parser.parse_args()
    root = args.pages.expanduser()
    output = args.output.expanduser().absolute()
    try:
        if root.is_symlink() or not root.is_dir():
            raise ValueError("The source must be a real directory.")
        root = root.resolve()
        if output.suffix.lower() != ".cbz" or not output.parent.is_dir() or output.resolve().is_relative_to(root):
            raise ValueError("Choose a .cbz destination in an existing directory outside the source.")
        sidecar = output.with_name(output.name + ".mangatag.json")
        if any(path.exists() or path.is_symlink() for path in (output, sidecar)):
            raise FileExistsError(f"The output or its sidecar already exists: {output}")
        paths = page_paths(root, args.order)
        width = max(4, len(str(len(paths))))
        plan = [(p, f"{index:0{width}d}{p.suffix.lower()}") for index, p in enumerate(paths, 1)]
        if args.apply:
            write_cbz(plan, output)
        print(json.dumps({
            "output": str(output), "written": args.apply, "page_count": len(plan),
            "pages": [{"source": p.relative_to(root).as_posix(), "member": n} for p, n in plan],
        }, ensure_ascii=False, indent=2))
    except (OSError, ValueError, Image.DecompressionBombError) as exc:
        print(f"pack_cbz: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
