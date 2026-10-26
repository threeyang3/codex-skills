#!/usr/bin/env python3
"""Check course-pack provenance, material integrity, lecture coverage and Markdown links.

Python 3.9+ standard library only. This checks structure, not mathematical correctness.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit


REQUIRED_MANIFEST_COLUMNS = {
    "lecture", "role", "original_path", "source_url", "target_path", "status"
}
VALID_STATUSES = {"downloaded", "unavailable"}


def prose(text: str) -> str:
    """Mask fenced and inline code while preserving line count."""
    lines = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence):
                fence = None
            lines.append("")
        elif marker:
            fence = marker[1]
            lines.append("")
        else:
            lines.append(re.sub(r"(`+).*?\1", "", line))
    return "\n".join(lines)


def verify(root: Path, expected_notes: int | None = None,
           expected_lectures: set[str] | None = None) -> list[str]:
    root = root.resolve()
    errors: list[str] = []

    def local_path(raw: str) -> Path:
        candidate = (root / raw).resolve()
        if Path(raw).is_absolute() or not candidate.is_relative_to(root):
            raise ValueError(f"path escapes course pack: {raw}")
        return candidate

    resources: set[Path] = set()
    unavailable = 0
    manifest_lectures: set[str] = set()
    manifest = root / "source_manifest.tsv"
    try:
        with manifest.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            fields = set(reader.fieldnames or [])
            missing = REQUIRED_MANIFEST_COLUMNS - fields
            if missing:
                errors.append(f"manifest missing columns: {sorted(missing)}")
            if not missing:
                for number, row in enumerate(reader, 2):
                    lecture = (row.get("lecture") or "").strip()
                    role = (row.get("role") or "").strip()
                    source_url = (row.get("source_url") or "").strip()
                    original_path = (row.get("original_path") or "").strip()
                    status = (row.get("status") or "").strip()
                    target_path = (row.get("target_path") or "").strip()

                    if not lecture or not role or not source_url or not original_path:
                        errors.append(
                            f"manifest line {number}: lecture, role, original_path and source_url must be non-empty"
                        )
                    if lecture:
                        manifest_lectures.add(lecture)
                    if not status:
                        errors.append(f"manifest line {number}: empty status")
                        continue
                    if status not in VALID_STATUSES:
                        errors.append(f"manifest line {number}: invalid status {status!r}")
                        continue
                    if status == "unavailable":
                        unavailable += 1
                        if target_path:
                            errors.append(
                                f"manifest line {number}: unavailable material must have an empty target_path"
                            )
                        continue
                    if not target_path:
                        errors.append(f"manifest line {number}: downloaded material has empty target_path")
                        continue
                    try:
                        target = local_path(target_path)
                        resources.add(target)
                        if not target.is_file():
                            errors.append(f"missing material: {target_path}")
                    except ValueError as exc:
                        errors.append(str(exc))
    except (OSError, UnicodeError, csv.Error) as exc:
        errors.append(f"cannot read manifest: {exc}")

    if expected_lectures is not None:
        missing_lectures = expected_lectures - manifest_lectures
        unexpected_lectures = manifest_lectures - expected_lectures
        if missing_lectures:
            errors.append(f"manifest missing expected lectures: {sorted(missing_lectures)}")
        if unexpected_lectures:
            errors.append(f"manifest has unexpected lectures: {sorted(unexpected_lectures)}")

    checksums: dict[Path, str] = {}
    try:
        checksum_file = root / "checksums.sha256"
        for number, line in enumerate(checksum_file.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            match = re.fullmatch(r"([a-fA-F0-9]{64}) [ *](.+)", line)
            if not match:
                errors.append(f"invalid checksum line {number}")
                continue
            try:
                target = local_path(match[2])
            except ValueError as exc:
                errors.append(str(exc))
                continue
            if target in checksums:
                errors.append(f"duplicate checksum: {match[2]}")
            checksums[target] = match[1].lower()
            if not target.is_file():
                errors.append(f"checksum file missing: {match[2]}")
            else:
                hasher = hashlib.sha256()
                with target.open("rb") as handle:
                    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                        hasher.update(chunk)
                if hasher.hexdigest() != match[1].lower():
                    errors.append(f"checksum mismatch: {match[2]}")
    except (OSError, UnicodeError) as exc:
        errors.append(f"cannot verify checksums: {exc}")

    for path in sorted(resources - checksums.keys()):
        errors.append(f"manifest target lacks checksum: {path.relative_to(root)}")
    for path in sorted(checksums.keys() - resources):
        errors.append(f"checksum target absent from manifest: {path.relative_to(root)}")

    notes_dir = root / "notes"
    notes = sorted(notes_dir.rglob("Lecture-*.md"))
    if not notes:
        errors.append("no notes/Lecture-*.md files found")
    if expected_notes is not None and len(notes) != expected_notes:
        errors.append(f"expected {expected_notes} notes, found {len(notes)}")

    note_lectures = {path.stem.split("_", 1)[0] for path in notes}
    if expected_lectures is not None:
        missing_notes = expected_lectures - note_lectures
        unexpected_notes = note_lectures - expected_lectures
        if missing_notes:
            errors.append(f"missing lecture notes: {sorted(missing_notes)}")
        if unexpected_notes:
            errors.append(f"unexpected lecture notes: {sorted(unexpected_notes)}")
    if expected_lectures is None:
        available_lectures = {
            lecture for lecture in manifest_lectures
            if any((row_status := status) == "downloaded" for status in [])
        }
        # Without an externally supplied scope, at least ensure every lecture with
        # a downloaded manifest row has a corresponding note; unavailable-only
        # lectures may legitimately have no note yet.
        downloaded_lectures: set[str] = set()
        try:
            with manifest.open(encoding="utf-8-sig", newline="") as handle:
                for row in csv.DictReader(handle, delimiter="\t"):
                    if (row.get("status") or "").strip() == "downloaded":
                        downloaded_lectures.add((row.get("lecture") or "").strip())
        except (OSError, UnicodeError, csv.Error):
            pass
        missing_notes = downloaded_lectures - note_lectures
        if missing_notes:
            errors.append(f"downloaded lectures missing notes: {sorted(missing_notes)}")

    markdown = sorted(set(root.glob("*.md")) | set(notes_dir.rglob("*.md")))
    bodies = {path: prose(path.read_text(encoding="utf-8")) for path in markdown}
    for path, body in bodies.items():
        label = path.relative_to(root)
        for raw in re.findall(r"\[\[([^\]\n]+)\]\]", body):
            destination = raw.split("|", 1)[0]
            name, _, anchor = destination.partition("#")
            if not name:
                matches = [path]
            elif "/" in name:
                relative_name = name if name.endswith(".md") else name + ".md"
                candidates = (path.parent / relative_name, notes_dir / relative_name, root / relative_name)
                matches = list({candidate.resolve() for candidate in candidates if candidate.resolve() in bodies})
            else:
                matches = [candidate for candidate in bodies if candidate.stem == name.removesuffix(".md")]
            if len(matches) != 1:
                errors.append(f"{label}: missing/ambiguous wiki target {destination}")
            elif anchor:
                titles = set(re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", bodies[matches[0]], re.MULTILINE))
                if anchor not in titles:
                    errors.append(f"{label}: missing wiki heading {destination}")

        for raw in re.findall(r"\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+\"[^\"]*\")?\s*\)", body):
            target = raw.strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            try:
                resolved = (path.parent / unquote(parsed.path)).resolve()
                if not resolved.is_relative_to(root):
                    errors.append(f"{label}: link escapes course pack {target}")
                elif not resolved.exists():
                    errors.append(f"{label}: missing relative link {target}")
            except (OSError, ValueError) as exc:
                errors.append(f"{label}: invalid link {target}: {exc}")

        display_open = False
        for number, line in enumerate(body.splitlines(), 1):
            inline_count = 0
            for match in re.finditer(r"(?<!\\)(\$\$|\$)", line):
                if match[0] == "$$":
                    display_open = not display_open
                elif not display_open:
                    inline_count += 1
            if inline_count % 2:
                errors.append(f"{label}:{number}: unbalanced inline math (escape currency dollars)")
        if display_open:
            errors.append(f"{label}: unbalanced display math")

    print(f"Checked {len(notes)} lecture notes, {len(resources)} unique materials; {unavailable} unavailable source rows")
    return errors


def parse_lecture_list(value: str | None) -> set[str] | None:
    if value is None:
        return None
    return {item.strip() for item in value.split(",") if item.strip()}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", type=Path, help="course pack root")
    parser.add_argument("--expected-notes", type=int, help="optional expected note count")
    parser.add_argument(
        "--expected-lectures",
        help="comma-separated lecture IDs from the course inventory, e.g. Lecture-01,Lecture-02",
    )
    args = parser.parse_args()
    errors = verify(args.root, args.expected_notes, parse_lecture_list(args.expected_lectures))
    for error in errors:
        print(f"ERROR: {error}")
    if not errors:
        print("OK: manifest, SHA-256, lecture coverage, local links and math delimiters")
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
