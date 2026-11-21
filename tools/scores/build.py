#!/usr/bin/env python3
"""tools/scores/*.ly を LilyPond で組み、music-theory/assets/ の楽譜画像（透過 WebP）を作り直す。

符頭の高さは五線の線間ちょうど（LilyPond の標準）。大きさを変えるときは
common.ily の set-global-staff-size か、下の RESOLUTION を変え、画像だけを伸縮させない。

使い方: python3 tools/scores/build.py   （lilypond 2.24 と Pillow が必要）
"""
import re
import subprocess
import tempfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parents[1] / "music-theory" / "assets"
RESOLUTION = 220
# サイトでは画素数の半分の幅で表示する。どの楽譜も同じ倍率になり、線間の大きさがそろう。
DISPLAY_SCALE = 0.5
PAGES = ["chapters/first.html", "chapters/melody.html", "chapters/contrapuntal.html", "resources.html"]
TARGETS = {"staff": "staff.webp", "melody": "melody_score.webp", "counterpoint": "counterpoint_score.webp"}

with tempfile.TemporaryDirectory() as tmp:
    for name, out in TARGETS.items():
        subprocess.run(["lilypond", "-s", "-dcrop", "-fpng", "-dpixmap-format=pngalpha",
                        f"-dresolution={RESOLUTION}", "-o", str(Path(tmp) / name), str(HERE / f"{name}.ly")],
                       check=True, cwd=HERE)
        with Image.open(Path(tmp) / f"{name}.cropped.png") as im:
            im.convert("RGBA").save(ASSETS / out, lossless=True, quality=100, method=6)
            width = round(im.width * DISPLAY_SCALE)
        for page in PAGES:
            path = ASSETS.parent / page
            text = path.read_text(encoding="utf-8")
            new = re.sub(r'(<img)((?:(?!>)[^w]|w(?!idth=))*?src="[^"]*' + re.escape(out) + r'")(?: width="\d+")?',
                         lambda m: f'{m.group(1)}{m.group(2)} width="{width}"', text)
            if new != text:
                path.write_text(new, encoding="utf-8")
        print(out, width)
