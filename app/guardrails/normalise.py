"""Text normalisation applied before any detector runs.

Obfuscation (zero-width characters, look-alike Unicode, padding, base64) is the main way cheap detectors are evaded,
so every detector sees the normalised text, and base64 runs are decoded and appended.
"""

from __future__ import annotations

import base64
import binascii
import re
import unicodedata

ZERO_WIDTH = dict.fromkeys(map(ord, "​‌‍⁠﻿­"), None)
LEET = str.maketrans({"0": "o", "1": "i", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a", "$": "s"})
B64_RUN = re.compile(r"[A-Za-z0-9+/]{16,}={0,2}")


def _decode_b64(text: str) -> list[str]:
    out = []
    for run in B64_RUN.findall(text):
        try:
            decoded = base64.b64decode(run + "=" * (-len(run) % 4), validate=True).decode("utf-8")
        except (binascii.Error, UnicodeDecodeError, ValueError):
            continue
        if decoded.isprintable() and sum(c.isalpha() for c in decoded) > len(decoded) * 0.6:
            out.append(decoded)
    return out


def normalise(text: str) -> str:
    t = unicodedata.normalize("NFKC", text).translate(ZERO_WIDTH)
    extra = _decode_b64(t)
    t = " ".join([t, *extra]).lower()
    t = re.sub(r"\s+", " ", t)
    return t


def deleet(text: str) -> str:
    return text.translate(LEET)
