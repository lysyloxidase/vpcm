"""Verify DOI references in Markdown files through CrossRef."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Iterable
from pathlib import Path

DOI_RE = re.compile(r"10\.[0-9]{4,9}/[^\s\]\),;]+")


def iter_markdown_files(root: Path) -> Iterable[Path]:
    """Yield Markdown files under a root path."""

    if root.is_file():
        yield root
        return
    yield from sorted(root.rglob("*.md"))


def extract_dois(root: Path) -> list[str]:
    """Extract unique DOI strings from Markdown docs."""

    dois: set[str] = set()
    for path in iter_markdown_files(root):
        text = path.read_text(encoding="utf-8")
        for match in DOI_RE.finditer(text):
            dois.add(match.group(0).rstrip("."))
    return sorted(dois)


def verify_doi(doi: str, timeout: float = 20.0) -> bool:
    """Return whether CrossRef can resolve a DOI."""

    encoded = urllib.parse.quote(doi, safe="")
    request = urllib.request.Request(
        f"https://api.crossref.org/works/{encoded}",
        headers={"User-Agent": "vpcm-doi-check/0.1 (mailto:maintainers@example.org)"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status == 200
    except urllib.error.HTTPError as exc:
        print(f"DOI failed ({exc.code}): {doi}", file=sys.stderr)
    except urllib.error.URLError as exc:
        print(f"DOI request error ({exc.reason}): {doi}", file=sys.stderr)
    return False


def main() -> int:
    """Run DOI verification."""

    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, help="Markdown file or directory")
    parser.add_argument(
        "--offline-report",
        type=Path,
        default=None,
        help="Write extracted DOI JSON without calling CrossRef.",
    )
    args = parser.parse_args()

    dois = extract_dois(args.root)
    if args.offline_report is not None:
        args.offline_report.write_text(
            json.dumps(dois, indent=2) + "\n",
            encoding="utf-8",
        )
        return 0

    failed = [doi for doi in dois if not verify_doi(doi)]
    if failed:
        print("Failed DOI verification:", file=sys.stderr)
        for doi in failed:
            print(f"- {doi}", file=sys.stderr)
        return 1
    print(f"Verified {len(dois)} DOI references.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
