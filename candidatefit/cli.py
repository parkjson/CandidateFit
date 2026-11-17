"""
cli.py
====================================
``candidatefit RESUME POSTING [POSTING ...]``: score a resume against one or
more job postings.
"""

import argparse
import json
import sys

from .readers import read_text
from .score import PREFERRED, score


def format_report(report, title=None):
    lines = []
    if title:
        lines.append(title)
    lines.append(f"Fit score: {report.score}/100")
    lines.append(
        f"  skills {round(100 * report.skill_coverage)}%"
        f" · keywords {round(100 * report.keyword_coverage)}%"
    )

    def tag(r):
        return " (preferred)" if r.weight <= PREFERRED else ""

    if report.matched:
        lines.append(f"\nMatched ({len(report.matched)}/{len(report.requirements)}):")
        for r in report.matched:
            via = f"  via {', '.join(r.matched_by)}" if len(r.skills) > 1 else ""
            lines.append(f"  + {r.label}{tag(r)}{via}")
    if report.missing:
        lines.append(f"\nMissing ({len(report.missing)}):")
        for r in report.missing:
            lines.append(f"  - {r.label}{tag(r)}")
    if not report.requirements:
        lines.append("\nNo known skills found in the posting; score is keywords only.")
    if report.keywords_missing:
        lines.append(
            "\nPosting keywords your resume doesn't use: "
            + ", ".join(report.keywords_missing)
        )
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="candidatefit",
        description="Score how well your resume fits a job posting.",
    )
    parser.add_argument("resume", help="resume file (.txt, .md, .html or .pdf)")
    parser.add_argument(
        "postings", nargs="+", help="job posting file(s) (.txt, .md, .html or .pdf)"
    )
    parser.add_argument("--json", action="store_true", help="print JSON instead")
    args = parser.parse_args(argv)

    resume = read_text(args.resume)
    results = []
    for path in args.postings:
        results.append((path, score(resume, read_text(path))))

    if args.json:
        out = [dict(posting=p, **r.to_dict()) for p, r in results]
        json.dump(out[0] if len(out) == 1 else out, sys.stdout, indent=2)
        print()
    else:
        # Best fit first when comparing several postings.
        results.sort(key=lambda pr: -pr[1].score)
        many = len(results) > 1
        print("\n\n".join(format_report(r, p if many else None) for p, r in results))
    return 0


if __name__ == "__main__":
    sys.exit(main())
