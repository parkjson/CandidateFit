# CandidateFit

![License](https://img.shields.io/github/license/parkjson/CandidateFit)
![Build Status](https://github.com/parkjson/CandidateFit/actions/workflows/build.yml/badge.svg)
[![codecov](https://codecov.io/gh/parkjson/CandidateFit/branch/main/graph/badge.svg?token=X5BN0AAOZ1)](https://codecov.io/gh/parkjson/CandidateFit)

Scores how well your resume fits a job posting, and shows what's missing.

```
$ candidatefit resume.pdf posting.html
Fit score: 82/100
  skills 100% · keywords 12%

Matched (2/2):
  + Python / Java / C / C++ / C#  via Python, Java
  + Test Automation

Posting keywords your resume doesn't use: applications, defects, complex,
developers, evaluate, technologies, language
```

Runs locally with no API key, and the same inputs always give the same score.

## Install

```
pip install "candidatefit[pdf] @ git+https://github.com/parkjson/CandidateFit"
```

Drop `[pdf]` if your resume isn't a PDF.

## Usage

```
candidatefit RESUME POSTING [POSTING ...] [--json]
```

- **RESUME / POSTING:** `.txt`, `.md`, `.html` or `.pdf`. For a saved
  LinkedIn job page (`.html`), only the job description is read.
- **Several postings:** ranked best fit first, which makes it easy to decide
  which applications to prioritise.
- **`--json`:** machine-readable output for scripts or spreadsheets.

From Python:

```python
from candidatefit import score

report = score(resume_text, posting_text)
report.score          # 0-100
report.missing        # requirements your resume doesn't show
report.keywords_missing
```

## How the score works

1. **Sections.** The posting is split by its headings. Skills under
   *Requirements* / *Qualifications* (or no heading) count fully. Skills
   under *Preferred* / *Nice to have*, or on a line saying "is a plus",
   count half. *About us* and *Benefits* sections are ignored.
2. **Alternatives.** "Java, Python, or C++" is one requirement that any of
   those skills satisfies.
3. **Skill coverage** is the weighted share of requirements your resume
   meets, using a vocabulary of about 90 skills
   ([`candidatefit/skills.py`](candidatefit/skills.py)). Ambiguous names
   like Go, C and R only count in context: "go the extra mile" isn't Go,
   and "Spring 2024" isn't Spring.
4. **Keyword coverage** is how many of the posting's most repeated
   non-skill words (e.g. "defects", "scalability") your resume also uses.
5. **Score** = 80% skill coverage + 20% keyword coverage. If a posting names
   no known skills, keyword coverage alone.

## Development

```
make develop   # install with dev dependencies
make test      # run tests
make lint      # black --check
make coverage
```

## Cover letter script (legacy)

`GPT_Cov_Let/scrapeToGPT.py` is the original project: it logs in to
LinkedIn with Selenium, scrapes a job posting and asks OpenAI for a cover
letter. Install with `pip install ".[coverletter]"`. It targets the retired
`text-davinci-003` completions API and needs updating before use.

[Documentation](https://parkjson.github.io/GPTCovLetDocs/)
