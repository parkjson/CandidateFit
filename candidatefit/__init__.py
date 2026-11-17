"""CandidateFit: score how well your resume fits a job posting."""

from ._version import __version__
from .score import FitReport, Requirement, extract_requirements, find_skills, score

__all__ = [
    "__version__",
    "FitReport",
    "Requirement",
    "extract_requirements",
    "find_skills",
    "score",
]
