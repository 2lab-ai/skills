#!/usr/bin/env python3
"""Pure string substitution prompt builder for image-gen2 batch pipeline.

CORE PRINCIPLE (ported from @zarvan_kim pipeline): ZERO runtime LLM calls.
A prompt template (with a `{subject}` placeholder) plus a subject list file
are turned into a list of (subject, final_prompt, output_filename) jobs by
pure Python string formatting only. No model is ever invoked here.

Subject list formats:
  - .txt  : one subject per line (blank lines / `#` comments ignored)
  - .csv  : 'subject' header column, else the first column
  - .json : either ["a","b"] or [{"subject": "a", ...}, ...]
"""
import csv
import json
import re
from pathlib import Path


def slugify(text: str) -> str:
    """Filesystem-safe slug: lower, spaces->_, strip non [a-z0-9_-]."""
    text = text.strip().lower()
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^a-z0-9_-]", "", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text or "subject"


def load_subjects(path: str) -> list[str]:
    """Read subjects from a .txt/.csv/.json file. Returns ordered list of str."""
    p = Path(path).expanduser()
    if not p.exists():
        raise FileNotFoundError(f"Subjects file not found: {p}")
    suffix = p.suffix.lower()

    if suffix == ".json":
        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError("JSON subjects must be a list")
        subjects = []
        for item in data:
            if isinstance(item, str):
                subjects.append(item.strip())
            elif isinstance(item, dict):
                val = item.get("subject")
                if val is None:
                    raise ValueError(f"JSON object missing 'subject' key: {item}")
                subjects.append(str(val).strip())
            else:
                raise ValueError(f"Unsupported JSON item type: {type(item)}")
        return [s for s in subjects if s]

    if suffix == ".csv":
        text = p.read_text(encoding="utf-8")
        reader = csv.reader(text.splitlines())
        rows = [r for r in reader if r and any(c.strip() for c in r)]
        if not rows:
            return []
        header = [c.strip().lower() for c in rows[0]]
        if "subject" in header:
            idx = header.index("subject")
            body = rows[1:]
        else:
            idx = 0
            body = rows  # no header -> first column is data
        return [row[idx].strip() for row in body if len(row) > idx and row[idx].strip()]

    # default: txt, one per line
    lines = p.read_text(encoding="utf-8").splitlines()
    return [
        ln.strip()
        for ln in lines
        if ln.strip() and not ln.strip().startswith("#")
    ]


def build_jobs(
    template: str, subjects: list[str], ext: str = "png"
) -> list[tuple[str, str, str]]:
    """Return list of (subject, final_prompt, filename). Pure substitution."""
    if "{subject}" not in template:
        raise ValueError("Template must contain the '{subject}' placeholder")
    jobs = []
    width = max(3, len(str(len(subjects))))
    for i, subject in enumerate(subjects, start=1):
        prompt = template.replace("{subject}", subject)
        filename = f"{i:0{width}d}_{slugify(subject)}.{ext}"
        jobs.append((subject, prompt, filename))
    return jobs


def load_template(template: str | None, template_file: str | None) -> str:
    if template_file:
        return Path(template_file).expanduser().read_text(encoding="utf-8").strip()
    if template:
        return template
    raise ValueError("Provide --template or --template-file")


if __name__ == "__main__":
    # Self-test / dry-run: print built jobs without generating anything.
    import argparse

    ap = argparse.ArgumentParser(description="Dry-run prompt builder (LLM-free)")
    ap.add_argument("--template")
    ap.add_argument("--template-file")
    ap.add_argument("--subjects", required=True)
    args = ap.parse_args()

    tmpl = load_template(args.template, args.template_file)
    subs = load_subjects(args.subjects)
    jobs = build_jobs(tmpl, subs)
    for subject, prompt, fname in jobs:
        print(f"[{fname}] subject={subject!r}\n  -> {prompt}")
    print(f"\nTotal jobs: {len(jobs)}")
