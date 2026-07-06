"""
EcoWatcher — Security & Privacy Watcher Shield Module
===============================================
# Day 4 Concept: Pre-processing Privacy Guardrail
# Day 4 Concept: Defensive Input Sanitization Before External API Calls

This module implements a mandatory security pre-processing layer that
intercepts ALL user input BEFORE it is transmitted to Google GenAI API
endpoints. It scans for high-risk data leaks including API credentials,
passwords, tokens, private numbers (SSN, credit cards, phone numbers),
and email addresses. Flagged content is masked with [REDACTED_DATA]
tokens to prevent accidental PII exfiltration.

Architecture Position: Upstream of Agent A (Material Classifier).
                       User Input -> Security Scan -> Sanitized Payload -> Agent Pipeline
"""

import re
import time
from dataclasses import dataclass, field
from typing import List, Tuple


# ---------------------------------------------------------------------------
# Day 4 Concept: Security Scan Result Data Model
# ---------------------------------------------------------------------------
@dataclass
class SecurityScanResult:
    """Immutable result object from the security pre-processing pipeline.

    Attributes:
        original_input: The raw, unmodified user input string.
        sanitized_input: The cleaned payload safe for API transmission.
        security_breach: True if ANY sensitive pattern was detected.
        threat_categories: List of human-readable threat type labels found.
        redaction_count: Total number of individual redactions applied.
        scan_latency_ms: Wall-clock time consumed by the scan in milliseconds.
        detailed_log: Ordered list of (threat_type, matched_snippet) tuples
                      for the operational Watcher Shield dashboard.
    """
    original_input: str = ""
    sanitized_input: str = ""
    security_breach: bool = False
    threat_categories: List[str] = field(default_factory=list)
    redaction_count: int = 0
    scan_latency_ms: float = 0.0
    detailed_log: List[Tuple[str, str]] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Day 4 Concept: Threat Detection Pattern Registry
# Each pattern is a tuple of (threat_label, compiled_regex).
# Patterns are ordered from most specific to most general to avoid
# over-matching on partial overlaps.
# ---------------------------------------------------------------------------
_THREAT_PATTERNS: List[Tuple[str, re.Pattern]] = [
    # API Keys & Tokens — common cloud provider formats
    (
        "API Key / Secret Token",
        re.compile(
            r"""(?x)
            (?:                             # Match key-value style declarations
                (?:api[_\-]?key|api[_\-]?secret|access[_\-]?token|auth[_\-]?token
                |secret[_\-]?key|private[_\-]?key|bearer)
                \s*[:=]\s*                  # Assignment operator
                ['\"]?                      # Optional quotes
                ([\w\-\.]{16,})             # The actual token value (16+ chars)
                ['\"]?
            )
            """,
            re.IGNORECASE,
        ),
    ),
    # AWS-style access key IDs (AKIA...)
    (
        "AWS Access Key",
        re.compile(r"\b(AKIA[0-9A-Z]{16})\b"),
    ),
    # Generic long hex/base64 tokens that look like secrets
    (
        "Generic Secret Token",
        re.compile(
            r"""(?x)
            (?:                                 # Preceded by a label
                (?:token|key|secret|password|passwd|pwd)
                \s*[:=]\s*['\"]?
            )
            ([A-Za-z0-9+/=_\-]{32,})           # 32+ char base64/hex blob
            """,
            re.IGNORECASE,
        ),
    ),
    # Passwords — explicit password declarations
    (
        "Password / Credential",
        re.compile(
            r"""(?x)
            (?:password|passwd|pwd)
            \s*[:=]\s*
            ['\"]?
            (\S{4,})                            # 4+ non-space chars
            ['\"]?
            """,
            re.IGNORECASE,
        ),
    ),
    # US Social Security Numbers  (XXX-XX-XXXX)
    (
        "Social Security Number (SSN)",
        re.compile(r"\b(\d{3}-\d{2}-\d{4})\b"),
    ),
    # Credit Card Numbers — Visa, MasterCard, Amex patterns
    (
        "Credit Card Number",
        re.compile(
            r"\b("
            r"4[0-9]{3}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}"  # Visa
            r"|5[1-5][0-9]{2}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}[\s\-]?[0-9]{4}"  # MC
            r"|3[47][0-9]{1}[\s\-]?[0-9]{4}[\s\-]?[0-9]{6}[\s\-]?[0-9]{1}[0-9]{4}"  # Amex
            r")\b"
        ),
    ),
    # Phone Numbers — US/international formats
    (
        "Phone Number",
        re.compile(
            r"(?<!\d)(\+?1?[\s\-\.]?\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4})(?!\d)"
        ),
    ),
    # Email Addresses
    (
        "Email Address",
        re.compile(r"\b([A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,})\b"),
    ),
]


# ---------------------------------------------------------------------------
# Day 4 Concept: Core Security Scan Execution Engine
# ---------------------------------------------------------------------------
def execute_security_scan(user_input_string: str) -> SecurityScanResult:
    """Run the full security pre-processing pipeline on raw user input.

    This function MUST be called before any data is sent to the Google
    GenAI API. It performs sequential regex-based threat detection,
    masks all matches with [REDACTED_DATA] tokens, and returns a rich
    audit result for dashboard rendering.

    # Day 4 Concept: Pre-processing Privacy Guardrail
    # Day 4 Concept: Input Sanitization Before External API Transmission

    Args:
        user_input_string: The raw, unmodified text from the user input field.

    Returns:
        SecurityScanResult with sanitized payload and full audit trail.
    """
    start_time = time.perf_counter()

    # Initialize result container
    result = SecurityScanResult(original_input=user_input_string)
    sanitized = user_input_string
    total_redactions = 0
    seen_categories = set()
    detailed_log = []

    # --- Sequential pattern scan ---
    # Day 4 Concept: Layered Threat Detection
    for threat_label, pattern in _THREAT_PATTERNS:
        matches = pattern.findall(sanitized)
        if matches:
            seen_categories.add(threat_label)
            for match in matches:
                # Extract the actual matched string (may be a group or full match)
                matched_text = match if isinstance(match, str) else match[0]
                if matched_text and len(matched_text) >= 4:
                    # Log the detection before masking
                    # Show only first 4 and last 2 chars in the log for safety
                    safe_preview = (
                        matched_text[:4] + "***" + matched_text[-2:]
                        if len(matched_text) > 6
                        else "****"
                    )
                    detailed_log.append((threat_label, safe_preview))

                    # Day 4 Concept: Explicit [REDACTED_DATA] Token Masking
                    sanitized = sanitized.replace(matched_text, "[REDACTED_DATA]")
                    total_redactions += 1

    # --- Compute timing ---
    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    # --- Populate result ---
    result.sanitized_input = sanitized
    result.security_breach = total_redactions > 0
    result.threat_categories = sorted(seen_categories)
    result.redaction_count = total_redactions
    result.scan_latency_ms = round(elapsed_ms, 3)
    result.detailed_log = detailed_log

    return result


# ---------------------------------------------------------------------------
# Day 4 Concept: Standalone CLI Verification (for Video Demo)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Quick self-test with deliberately injected sensitive data
    test_input = (
        "I have 3 glass jars, some old cardboard, and a broken laptop. "
        "My email is jane.doe@example.com and my SSN is 123-45-6789. "
        "Also my api_key = 'sk-abc123def456ghi789jkl012mno345pq' "
        "and password=SuperSecret123!"
    )
    print("=" * 70)
    print("EcoWatcher Watcher Shield — Standalone Test")
    print("=" * 70)
    print(f"\n[RAW INPUT]\n{test_input}\n")

    scan = execute_security_scan(test_input)

    print(f"[SECURITY BREACH DETECTED]: {scan.security_breach}")
    print(f"[REDACTION COUNT]: {scan.redaction_count}")
    print(f"[SCAN LATENCY]: {scan.scan_latency_ms} ms")
    print(f"[THREAT CATEGORIES]: {scan.threat_categories}")
    print(f"\n[SANITIZED OUTPUT]\n{scan.sanitized_input}\n")
    print("[DETAILED AUDIT LOG]")
    for category, snippet in scan.detailed_log:
        print(f"  • {category}: {snippet}")
    print("=" * 70)
