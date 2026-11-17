import json
from pathlib import Path

import pytest

from candidatefit import extract_requirements, find_skills, score
from candidatefit.cli import main
from candidatefit.readers import read_text

LINKEDIN_PAGE = (
    Path(__file__).resolve().parents[2]
    / "GPT_Cov_Let"
    / "tests"
    / "staticPageUnitTest.html"
)

POSTING = """Backend Engineer

About Us
We are a fintech startup with a great benefits package and Kubernetes swag.

Requirements:
- 3+ years building services in Python or Go
- Strong SQL and PostgreSQL experience
- Experience writing unit tests and maintaining CI/CD pipelines

Nice to have:
- Docker
- AWS

Experience with GraphQL is a plus.
"""


def labels(reqs):
    return {r.label: r.weight for r in reqs}


def test_find_skills_handles_ambiguous_names():
    assert find_skills("C, C++ and C# experience") == ["C", "C++", "C#"]
    assert find_skills("Go and Rust") == ["Go", "Rust"]
    assert "Go" not in find_skills("Ready to go the extra mile")
    assert "Spring" not in find_skills("Software intern, Spring 2024")
    assert "Spring" in find_skills("Java with Spring Boot")
    assert "JavaScript" not in find_skills("Java developer")
    assert "R" not in find_skills("Our R&D team")


def test_sections_set_weights_and_company_text_is_ignored():
    reqs = labels(extract_requirements(POSTING))
    assert reqs["Python / Go"] == 1.0
    assert reqs["SQL"] == 1.0 and reqs["PostgreSQL"] == 1.0
    assert reqs["Unit Testing"] == 1.0 and reqs["CI/CD"] == 1.0
    assert reqs["Docker"] == 0.5 and reqs["AWS"] == 0.5
    assert reqs["GraphQL"] == 0.5  # inline "is a plus"
    assert "Kubernetes" not in reqs  # only mentioned under About Us


def test_alternatives_need_only_one():
    report = score("Python and SQL", "Requirements:\nJava, Python, or C++\nSQL")
    assert report.skill_coverage == 1.0
    (group,) = [r for r in report.requirements if len(r.skills) > 1]
    assert group.matched_by == ("Python",)


def test_score_reflects_missing_and_preferred_skills():
    strong = score("Python, Go, SQL, PostgreSQL, unit tests, CI/CD", POSTING)
    weak = score("Python, SQL", POSTING)
    assert strong.skill_coverage > weak.skill_coverage
    assert {r.label for r in weak.missing} >= {"PostgreSQL", "Docker"}
    # Missing a preferred skill costs less than missing a required one.
    everything = "Python SQL PostgreSQL unit tests CI/CD Docker AWS GraphQL"
    no_docker = score(everything.replace("Docker", ""), POSTING)
    no_postgres = score(everything.replace("PostgreSQL", ""), POSTING)
    assert score(everything, POSTING).skill_coverage == 1.0
    assert no_postgres.skill_coverage < no_docker.skill_coverage < 1.0


def test_score_is_deterministic_and_bounded():
    a = score("Python", POSTING)
    b = score("Python", POSTING)
    assert a.to_dict() == b.to_dict()
    assert 0 <= a.score <= 100


def test_posting_without_known_skills_uses_keywords():
    posting = "Gardener wanted. Pruning, pruning, mulching and mulching daily."
    report = score("Experienced in pruning hedges", posting)
    assert report.requirements == []
    assert "pruning" in report.keywords_matched
    assert "mulching" in report.keywords_missing
    assert report.score == 50


def test_saved_linkedin_page():
    posting = read_text(LINKEDIN_PAGE)
    assert "RTTS" in posting
    reqs = labels(extract_requirements(posting))
    assert reqs["Python / Java / C / C++ / C#"] == 1.0
    assert "Test Automation" in reqs
    # "database platforms" appears only under "What We Offer"
    assert "Databases" not in reqs
    assert score("Java developer, test automation", posting).skill_coverage == 1.0


def test_cli_text_and_json(tmp_path, capsys):
    resume = tmp_path / "resume.txt"
    posting = tmp_path / "posting.txt"
    resume.write_text("Python, SQL, Docker")
    posting.write_text(POSTING)

    assert main([str(resume), str(posting)]) == 0
    out = capsys.readouterr().out
    assert "Fit score:" in out and "Missing" in out and "PostgreSQL" in out

    assert main([str(resume), str(posting), "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert 0 <= data["score"] <= 100
    assert any(r["skills"] == ["Docker"] for r in data["requirements"])


def test_cli_ranks_several_postings(tmp_path, capsys):
    resume = tmp_path / "r.md"
    resume.write_text("Python")
    good = tmp_path / "good.txt"
    bad = tmp_path / "bad.txt"
    good.write_text("Requirements: Python")
    bad.write_text("Requirements: Rust, Haskell-free Scala")
    main([str(resume), str(bad), str(good)])
    out = capsys.readouterr().out
    assert out.index("good.txt") < out.index("bad.txt")


def test_pdf_without_pypdf_explains(tmp_path, monkeypatch):
    import builtins

    real_import = builtins.__import__

    def fake_import(name, *a, **k):
        if name == "pypdf":
            raise ImportError
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    pdf = tmp_path / "resume.pdf"
    pdf.write_bytes(b"%PDF-1.4")
    with pytest.raises(SystemExit, match="pypdf"):
        read_text(pdf)
