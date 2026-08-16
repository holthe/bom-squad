#!/usr/bin/env python3
"""Sweep the repo for literal invisible characters.

The site footer claims this document contains no byte order mark, and the
README claims the repo contains invisible characters only as escape
sequences. This script is what makes both claims checkable. It fails (exit 1)
if any text file contains:

  * a literal invisible/format character (BOM, zero-widths, joiners, bidi
    controls, no-break space, soft hyphen), anywhere, ever; or
  * an em dash or curly quote outside index.html, where they appear only as
    visible exhibits in the field guide (house style: straight quotes, no
    em dashes).

Escape sequences like \\uFEFF in index.html's script are plain ASCII and
pass untouched. Binary assets (png, ico) are skipped by extension.
"""
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

INVISIBLE = {
    0xFEFF: "byte order mark / zero width no-break space",
    0x200B: "zero width space",
    0x200C: "zero width non-joiner",
    0x200D: "zero width joiner",
    0x2060: "word joiner",
    0x00A0: "no-break space",
    0x00AD: "soft hyphen",
    0x202A: "left-to-right embedding",
    0x202B: "right-to-left embedding",
    0x202C: "pop directional formatting",
    0x202D: "left-to-right override",
    0x202E: "right-to-left override",
    0x2066: "left-to-right isolate",
    0x2067: "right-to-left isolate",
    0x2068: "first strong isolate",
    0x2069: "pop directional isolate",
}

STYLE = {
    0x2014: "em dash",
    0x2018: "left smart quote",
    0x2019: "right smart quote",
    0x201C: "left smart double quote",
    0x201D: "right smart double quote",
}

# index.html displays these characters on purpose, as the exhibits in the
# field guide and the surrounding final copy. Invisibles are never allowed,
# there or anywhere.
STYLE_EXEMPT = {"index.html"}

BINARY_SUFFIXES = {".png", ".ico", ".woff2", ".jpg", ".gif"}


def files():
    for p in sorted(ROOT.rglob("*")):
        rel = p.relative_to(ROOT)
        if not p.is_file() or rel.parts[0] in {".git", ".wrangler", "node_modules"}:
            continue
        if p.suffix.lower() in BINARY_SUFFIXES:
            continue
        yield p, str(rel)


def main():
    problems = 0
    for path, rel in files():
        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), 1):
            for col, ch in enumerate(line, 1):
                cp = ord(ch)
                if cp in INVISIBLE:
                    label = INVISIBLE[cp]
                elif cp in STYLE and rel not in STYLE_EXEMPT:
                    label = STYLE[cp]
                elif unicodedata.category(ch) == "Cf":
                    label = unicodedata.name(ch, "format character").lower()
                else:
                    continue
                print(f"{rel}:{lineno}:{col}: U+{cp:04X} {label}")
                problems += 1
    if problems:
        print(f"\n{problems} device(s) located. The footer is lying. Fix that.")
        return 1
    print("All clear. Repo swept, 0 literal devices found. Remain vigilant.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
