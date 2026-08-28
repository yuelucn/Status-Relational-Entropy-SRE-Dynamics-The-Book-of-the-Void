#!/usr/bin/env python3
import os
import re

def fix_dashes_in_md(root="."):
    # 要清除的特殊横杠：U+2011 非断开连字符，U+2013 en‑dash，U+2014 em‑dash
    bad_dash_pattern = re.compile(r"[\u2011\u2013\u2014]")
    for dirpath, _, filenames in os.walk(root):
        for fname in filenames:
            if not fname.lower().endswith(".md"):
                continue
            fpath = os.path.join(dirpath, fname)
            with open(fpath, "r", encoding="utf‑8") as f:
                raw = f.read()
            new_text = bad_dash_pattern.sub("-", raw)
            if new_text != raw:
                print(f"Fixed bad dashes: {fpath}")
                with open(fpath, "w", encoding="utf‑8") as f:
                    f.write(new_text)

if __name__ == "__main__":
    fix_dashes_in_md()
