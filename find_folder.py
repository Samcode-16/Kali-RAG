import sys
from pathlib import Path

kw = sys.argv[1].lower()
for d in sorted(Path("data/raw/kali-docs").rglob("*")):
    if d.is_dir() and kw in d.name.lower():
        print(d.name)