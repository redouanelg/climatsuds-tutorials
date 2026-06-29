#!/usr/bin/env python3
"""Validate tutorials.json against the ClimatSuds tag scheme.

Run locally:   python scripts/validate_tutorials.py
CI runs this before publishing; a non-zero exit fails the Pages build.

Every tag must come from the controlled vocabulary below, organised by facet
(section / dataset / source-type / variable / region). To introduce a new
dataset, region, variable, etc., add it to VOCAB here in the same commit.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "tutorials.json"

# --- Controlled vocabulary (extend here when adding new content) -------------
VOCAB = {
    "section":     {"data-access", "getting-started", "analysis", "visualization", "modeling"},
    "dataset":     {"era5", "imerg", "ghcn"},
    "source-type": {"reanalysis", "satellite", "station-observations"},
    "variable":    {"temperature", "precipitation"},
    "region":      {"global", "africa", "europe", "asia", "americas", "oceania", "antarctica"},
}
TAG_FACET = {tag: facet for facet, tags in VOCAB.items() for tag in tags}

MAX_TAGS = 5
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")  # lowercase kebab-case


def validate():
    errors = []

    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return [f"{MANIFEST} not found"]
    except json.JSONDecodeError as e:
        return [f"tutorials.json is not valid JSON: {e}"]

    if not isinstance(data, dict) or not isinstance(data.get("tutorials"), list):
        return ['top level must be an object with a "tutorials" array']

    seen_ids = set()
    for i, t in enumerate(data["tutorials"]):
        loc = f'entry #{i} (id={t.get("id", "?")})'

        # required common fields (tags handled per-type below)
        for key in ("id", "type", "lang", "title", "desc"):
            if key not in t:
                errors.append(f"{loc}: missing required field '{key}'")

        # id
        tid = t.get("id")
        if isinstance(tid, str):
            if not SLUG.match(tid):
                errors.append(f"{loc}: id must be lowercase kebab-case")
            if tid in seen_ids:
                errors.append(f"{loc}: duplicate id '{tid}'")
            seen_ids.add(tid)

        # type + the field it implies
        ttype = t.get("type")
        if ttype not in ("notebook", "video"):
            errors.append(f'{loc}: type must be "notebook" or "video" (got {ttype!r})')
        elif ttype == "notebook":
            nb = t.get("notebook")
            if not nb:
                errors.append(f"{loc}: notebooks need a 'notebook' path")
            elif not (ROOT / nb).is_file():
                errors.append(f"{loc}: notebook file not found: {nb}")
            if "tags" not in t:
                errors.append(f"{loc}: notebooks need a 'tags' list")
            else:
                errors.extend(_validate_tags(t["tags"], loc))
        elif ttype == "video":
            if not t.get("canalu"):
                errors.append(f"{loc}: videos need a 'canalu' URL")
            if t.get("tags"):  # absent or empty is fine — videos carry no tags
                errors.append(f"{loc}: videos must not have tags (omit the field)")

        # lang
        if t.get("lang") not in ("en", "fr"):
            errors.append(f'{loc}: lang must be "en" or "fr"')

        # bilingual title/desc
        for key in ("title", "desc"):
            val = t.get(key)
            if isinstance(val, dict):
                for code in ("en", "fr"):
                    if not (isinstance(val.get(code), str) and val[code].strip()):
                        errors.append(f"{loc}: {key}.{code} must be a non-empty string")
            elif key in t:
                errors.append(f"{loc}: {key} must be an object with 'en' and 'fr'")

    return errors


def _validate_tags(tags, loc):
    errs = []
    if not isinstance(tags, list):
        return [f"{loc}: tags must be a list"]
    if not (1 <= len(tags) <= MAX_TAGS):
        errs.append(f"{loc}: must have 1–{MAX_TAGS} tags (has {len(tags)})")
    if len(tags) != len(set(tags)):
        errs.append(f"{loc}: duplicate tags {sorted(t for t in set(tags) if tags.count(t) > 1)}")

    sections = 0
    for tag in tags:
        if not isinstance(tag, str) or not SLUG.match(tag):
            errs.append(f"{loc}: tag {tag!r} must be lowercase kebab-case")
            continue
        facet = TAG_FACET.get(tag)
        if facet is None:
            errs.append(f"{loc}: unknown tag '{tag}' — add it to VOCAB in "
                        f"scripts/validate_tutorials.py, or fix the tag")
        elif facet == "section":
            sections += 1

    if sections != 1:
        errs.append(f"{loc}: must have exactly one 'section' tag "
                    f"({sorted(VOCAB['section'])}); found {sections}")
    return errs


def main():
    errors = validate()
    if errors:
        print("tutorials.json validation FAILED:\n")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    n = len(json.loads(MANIFEST.read_text(encoding="utf-8"))["tutorials"])
    print(f"tutorials.json OK — {n} entries, all tags valid")


if __name__ == "__main__":
    main()
