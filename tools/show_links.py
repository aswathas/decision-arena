"""Print the internal links of a built page. A scratch tool for the site build.

    python tools/show_links.py site/dist/index.html
"""
from __future__ import annotations

import re
import sys

HREF = re.compile(r'href="([^"]+)"')

for path in sys.argv[1:]:
    with open(path, "r", encoding="utf-8") as f:
        html = f.read()
    internal = sorted({h for h in HREF.findall(html) if h.startswith("/")})
    print(path)
    for href in internal:
        print("   ", href)
