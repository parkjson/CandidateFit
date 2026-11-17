"""
score.py
====================================
Scores how well a resume fits a job posting.

How the score works
-------------------
1. The posting is split into sections by its headings. Skills under
   "requirements" or "qualifications" headings, or under no heading, count
   fully (weight 1.0). Skills under "preferred" or "nice to have" headings
   count half (0.5). Sections about the company or benefits are ignored.
2. A sentence that lists skills joined by "or" ("Java, Python, or C++")
   becomes one requirement that any of those skills satisfies.
3. Skill coverage = matched requirement weight / total requirement weight.
4. Keyword coverage = how many of the posting's most repeated non-skill
   words (e.g. "testing", "defects") also appear in the resume.
5. Score = 80% skill coverage + 20% keyword coverage, from 0 to 100. If the
   posting names no known skills, the score is keyword coverage alone.

Everything runs locally and deterministically: no API key, same input gives
the same score.
"""

import re
from collections import Counter
from dataclasses import dataclass, field

from .skills import CASE_SENSITIVE, SKILLS

SKILL_WEIGHT = 0.8
KEYWORD_WEIGHT = 0.2
TOP_KEYWORDS = 12

REQUIRED = 1.0
PREFERRED = 0.5
IGNORED = 0.0

_HEADING_MODES = [
    (
        IGNORED,
        r"about us|who we are|company description|what we offer|benefits|perks"
        r"|compensation|additional information|equal opportunity|why join",
    ),
    (PREFERRED, r"preferred|nice[\s-]to[\s-]have|bonus|desired|good to have"),
    (
        REQUIRED,
        r"requirements?|qualifications|what you need|must[\s-]have|you have"
        r"|you bring|minimum|basic|responsibilities|what you.ll be doing"
        r"|about the (?:job|role|position)|job description",
    ),
]

_ALTERNATIVE_RE = re.compile(r"\b(?:or|either|any of|one of)\b", re.I)

# A line like "Docker is a plus" marks only its own skills as preferred.
_INLINE_PREFERRED_RE = re.compile(
    r"\b(?:a plus|a bonus|preferred|nice[\s-]to[\s-]have|desirable|bonus points)\b",
    re.I,
)

_STOPWORDS = set("""
    a about above across after again all also an and any are as at be because
    been before being both but by can could did do does doing during each
    either etc few for from further had has have having here how if in into is
    it its itself just more most must no nor not of off on once only or other
    our out over own per same should so some such than that the their them
    then there these they this those through to too under until up upon very
    was we were what when where which while who whom why will with within
    would you your yours us new well like one two three
    ability able across additional applicant applicants apply area areas based
    benefits candidate candidates company client clients day degree environment
    equal etc excellent experience experienced field good great help including
    job join knowledge level looking make many needs offer opportunity position
    preferred provide providing qualifications related required requirements
    responsibilities role skills strong team teams time using various work
    working years year least plus related etc. information description career
    companies office location include live within miles must authorized employment
    remote hybrid salary depending expect ensure across alongside other""".split())


@dataclass
class Requirement:
    """One thing the posting asks for: a skill, or a set of alternatives."""

    skills: tuple
    weight: float
    matched_by: tuple = ()

    @property
    def matched(self):
        return bool(self.matched_by)

    @property
    def label(self):
        return " / ".join(self.skills)


@dataclass
class FitReport:
    """The result of :func:`score`."""

    score: int
    skill_coverage: float
    keyword_coverage: float
    requirements: list = field(default_factory=list)
    keywords_matched: list = field(default_factory=list)
    keywords_missing: list = field(default_factory=list)

    @property
    def matched(self):
        return [r for r in self.requirements if r.matched]

    @property
    def missing(self):
        return [r for r in self.requirements if not r.matched]

    def to_dict(self):
        return {
            "score": self.score,
            "skill_coverage": round(self.skill_coverage, 3),
            "keyword_coverage": round(self.keyword_coverage, 3),
            "requirements": [
                {
                    "skills": list(r.skills),
                    "weight": r.weight,
                    "matched_by": list(r.matched_by),
                }
                for r in self.requirements
            ],
            "keywords_matched": self.keywords_matched,
            "keywords_missing": self.keywords_missing,
        }


def _compile():
    compiled = {}
    for name, patterns in SKILLS.items():
        flags = 0 if name in CASE_SENSITIVE else re.I
        compiled[name] = [
            re.compile(r"(?<![\w])" + p + r"(?![\w])", flags) for p in patterns
        ]
    return compiled


_COMPILED = _compile()


def _normalize(text):
    return (
        text.replace("’", "'")
        .replace("‘", "'")
        .replace("“", '"')
        .replace("”", '"')
        .replace(" ", " ")
    )


def find_skills(text):
    """Returns the skills mentioned in ``text``, in vocabulary order."""
    text = _normalize(text)
    return [
        name
        for name, patterns in _COMPILED.items()
        if any(p.search(text) for p in patterns)
    ]


def _heading_mode(line):
    """The section weight a heading line starts, or None if it isn't one."""
    stripped = line.strip().strip("#*-").strip()
    if not stripped or stripped.endswith(".") or len(stripped.split()) > 6:
        return None
    stripped = stripped.rstrip(":")
    for mode, pattern in _HEADING_MODES:
        if re.search(pattern, stripped, re.I):
            return mode
    return None


def _segments(line):
    """Splits a line into sentences without breaking "Node.js" or "C#."."""
    return [s for s in re.split(r";|(?<=[a-z0-9)])\.\s+", line) if s.strip()]


def _weighted_lines(posting):
    """
    Yields (line, weight) for the parts of the posting that describe the job,
    skipping heading lines and company/benefits sections.
    """
    mode = REQUIRED
    for line in _normalize(posting).splitlines():
        heading = _heading_mode(line)
        if heading is not None:
            mode = heading
            # A heading can carry skills too ("Must have: Python"); keep it
            # for skills but tell callers it's a heading via weight sign.
            if mode != IGNORED:
                yield line, -mode
            continue
        if mode == IGNORED or not line.strip():
            continue
        weight = mode
        if _INLINE_PREFERRED_RE.search(line):
            weight = min(mode, PREFERRED)
        yield line, weight


def extract_requirements(posting):
    """Turns a posting into a list of :class:`Requirement` (unmatched)."""
    singles = {}
    groups = {}
    for line, weight in _weighted_lines(posting):
        weight = abs(weight)
        for seg in _segments(line):
            found = find_skills(seg)
            if len(found) >= 2 and _ALTERNATIVE_RE.search(seg):
                key = tuple(found)
                groups[key] = max(groups.get(key, 0), weight)
            else:
                for s in found:
                    singles[s] = max(singles.get(s, 0), weight)

    reqs = [Requirement((s,), w) for s, w in singles.items()]
    for key, w in groups.items():
        # A group fully covered by stand-alone requirements adds nothing.
        if not all(s in singles for s in key):
            reqs.append(Requirement(key, w))
    return reqs


def _stem(word):
    for suffix in ("ing", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 4:
            return word[: -len(suffix)]
    return word


def _words(text):
    return re.findall(r"[a-z][a-z-]{2,}(?![a-z'])", _normalize(text).lower())


def top_keywords(posting, n=TOP_KEYWORDS):
    """The posting's most repeated meaningful words (2+ uses), skills excluded."""
    skill_stems = {
        _stem(w.lower()) for name in SKILLS for w in re.findall(r"\w+", name)
    }
    body = "\n".join(line for line, w in _weighted_lines(posting) if w > 0)
    counts = Counter()
    first = {}
    for w in _words(body):
        st = _stem(w)
        if w in _STOPWORDS or st in skill_stems:
            continue
        counts[st] += 1
        first.setdefault(st, w)
    ranked = [st for st, c in counts.most_common() if c >= 2][:n]
    return [(st, first[st]) for st in ranked]


def score(resume, posting):
    """
    Scores how well ``resume`` fits ``posting``. Both are plain text.

    Returns
    -------
    FitReport
        ``score`` (0-100), the posting's requirements with which resume skill
        satisfied each, and the posting keywords the resume does or doesn't use.
    """
    resume_skills = set(find_skills(resume))
    reqs = extract_requirements(posting)
    for r in reqs:
        r.matched_by = tuple(s for s in r.skills if s in resume_skills)

    total = sum(r.weight for r in reqs)
    skill_cov = sum(r.weight for r in reqs if r.matched) / total if total else 0.0

    resume_stems = {_stem(w) for w in _words(resume)}
    kws = top_keywords(posting)
    kw_hit = [word for st, word in kws if st in resume_stems]
    kw_miss = [word for st, word in kws if st not in resume_stems]
    kw_cov = len(kw_hit) / len(kws) if kws else 0.0

    if total:
        value = SKILL_WEIGHT * skill_cov + KEYWORD_WEIGHT * kw_cov
    else:
        value = kw_cov
    return FitReport(
        score=round(100 * value),
        skill_coverage=skill_cov,
        keyword_coverage=kw_cov,
        requirements=sorted(reqs, key=lambda r: (-r.weight, r.label)),
        keywords_matched=kw_hit,
        keywords_missing=kw_miss,
    )
