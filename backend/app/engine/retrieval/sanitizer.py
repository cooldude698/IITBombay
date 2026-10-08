"""Anti-Prompt-Injection Text Sanitizer & Untrusted Boundary Fencer.

Neutralizes prompt injection patterns in external documents (invoices, emails,
vendor notes), strips obfuscated Unicode, and wraps evidence inside secure
<untrusted_evidence_data> isolation tags.
"""

import hashlib
import re
import unicodedata
from typing import List, Optional
from pydantic import BaseModel, Field


class SanitizationResult(BaseModel):
    clean_text: str
    is_safe: bool
    flagged_patterns: List[str] = Field(default_factory=list)
    quarantined_xml: str
    safety_flag: str  # "CLEAN" or "POTENTIAL_ADVERSARIAL_INJECTION"
    payload_hash: str


class EvidenceSanitizer:
    """Detects and quarantines prompt injection patterns in external text."""

    INJECTION_PATTERNS = [
        re.compile(r"(?i)\bignore\s+(all\s+)?previous\s+instructions\b"),
        re.compile(r"(?i)\bsystem\s*prompt\s*override\b"),
        re.compile(r"(?i)\byou\s+are\s+now\s+in\s+developer\s+mode\b"),
        re.compile(r"(?i)\bdo\s+not\s+verify\s+this\s+transaction\b"),
        re.compile(r"(?i)\bdisregard\s+(all\s+)?(po|policy|rules|constraints|limits)\b"),
        re.compile(r"(?i)\bemergency\s+protocol\s*[:\-]\s*transfer\b"),
        re.compile(r"(?i)\bsystem\s*override\b"),
        re.compile(r"(?i)\bact\s+as\s+(an?\s+)?unrestricted\b"),
        re.compile(r"(?i)\bbypass\s+verification\b"),
        re.compile(r"(?i)\btransfer\s+funds\s+immediately\s+without\s+approval\b"),
    ]

    # Zero-width, formatting, and invisible unicode characters
    ZERO_WIDTH_REGEX = re.compile(r"[\u200B-\u200D\uFEFF\u202A-\u202E]")

    def sanitize(
        self,
        raw_text: str,
        source_id: str = "document",
    ) -> SanitizationResult:
        """Sanitizes text, checks for injection patterns, and produces XML container."""
        if not raw_text:
            return SanitizationResult(
                clean_text="",
                is_safe=True,
                flagged_patterns=[],
                quarantined_xml=f'<untrusted_evidence_data source="{source_id}" hash="empty">\n</untrusted_evidence_data>',
                safety_flag="CLEAN",
                payload_hash="empty",
            )

        # 1. Normalize Unicode (NFKC) and strip zero-width characters
        normalized = unicodedata.normalize("NFKC", raw_text)
        cleaned = self.ZERO_WIDTH_REGEX.sub("", normalized)

        # 2. Compute SHA-256 hash of cleaned text
        payload_hash = hashlib.sha256(cleaned.encode("utf-8")).hexdigest()[:16]

        # 3. Detect Injection Patterns
        flagged: List[str] = []
        for pattern in self.INJECTION_PATTERNS:
            matches = pattern.findall(cleaned)
            if matches:
                flagged.append(pattern.pattern)

        is_safe = len(flagged) == 0
        safety_flag = "CLEAN" if is_safe else "POTENTIAL_ADVERSARIAL_INJECTION"

        # 4. Wrap inside strictly isolated XML boundary tag
        quarantined_xml = (
            f'<untrusted_evidence_data source="{source_id}" hash="{payload_hash}" safety_flag="{safety_flag}">\n'
            f"{cleaned.strip()}\n"
            f"</untrusted_evidence_data>"
        )

        return SanitizationResult(
            clean_text=cleaned,
            is_safe=is_safe,
            flagged_patterns=flagged,
            quarantined_xml=quarantined_xml,
            safety_flag=safety_flag,
            payload_hash=payload_hash,
        )


default_sanitizer = EvidenceSanitizer()
