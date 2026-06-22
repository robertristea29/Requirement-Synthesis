from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class SrsValidationResult:
    passed: bool
    missing_headings: list[str]
    fr_count: int
    nfr_count: int
    contradiction_count: int


def validate_srs_spec(srs_text: str) -> SrsValidationResult:
    required_headings = [
        "# Software Requirements Specification (SRS)",
        "## 1. Purpose",
        "## 2. Scope",
        "## 3. Stakeholders",
        "## 4. Functional Requirements",
        "## 5. Non-Functional Requirements",
        "## 6. Contradictions and Risks",
        "## 7. Open Questions",
    ]

    missing_headings = [h for h in required_headings if h not in srs_text]

    fr_count = len(re.findall(r"\bFR-\d+\b", srs_text))
    nfr_count = len(re.findall(r"\bNFR-\d+\b", srs_text))
    contradiction_count = len(re.findall(r"\bC-\d+\b", srs_text))

    passed = not missing_headings and fr_count > 0 and nfr_count > 0

    return SrsValidationResult(
        passed=passed,
        missing_headings=missing_headings,
        fr_count=fr_count,
        nfr_count=nfr_count,
        contradiction_count=contradiction_count,
    )
