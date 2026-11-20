#!/usr/bin/env python3
"""Web版の各ページを一冊にまとめ、music-theory/assets/music-theory.pdf を作り直す。

章の並び・部の区切りは music-theory/index.html の目次から読むので、
サイトを更新したらこのスクリプトを実行するだけで PDF が同じ構成になる。

必要なもの: Python 3 (beautifulsoup4, pypdf, Pillow), Node.js と playwright (Chromium),
フォント IPAex明朝 / IPAexゴシック / STIX Math（いずれも TrueType か OpenType）。

使い方: python3 tools/pdf/build_pdf.py
"""
import html
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from bs4 import BeautifulSoup, Tag
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[2]
SITE = ROOT / "music-theory"
CHAPTERS = SITE / "chapters"
OUT_PDF = SITE / "assets" / "music-theory.pdf"
PRINT_JS = Path(__file__).with_name("print.js")
PUBLIC = "https://tarouzirou.github.io/music-theory/"
TITLE = "音楽理論を耳と手で学ぶ"


def soup_of(path):
    return BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")


# ---------- 構成を目次ページから読む ----------
index = soup_of(SITE / "index.html")
PARTS = []  # (kicker, title, desc, [slug])
for card in index.select(".part-card"):
    slugs = [Path(a["href"]).stem for a in card.select("li > a")]
    desc = card.select_one(".part-desc")
    PARTS.append((card.select_one(".kicker").get_text(strip=True), card.h3.get_text(strip=True),
                  desc.get_text(strip=True) if desc else "", slugs))
ORDER = ["start"] + [s for p in PARTS for s in p[3]]
FIRST_OF_PART = {p[3][0]: p for p in PARTS}
edition = index.select_one(".hero .kicker").get_text(strip=True)
footer_text = index.select_one(".footer-inner").get_text(strip=True)

# ---------- 各ページの本文 ----------
IDS = {}  # (slug, 元のid) -> PDF内の短いid


def short_id(slug, frag):
    key = (slug, frag)
    if key not in IDS:
        IDS[key] = f"{slug}-{len([k for k in IDS if k[0] == slug]) + 1}"
    return IDS[key]


def anchor(slug, frag=""):
    return f"#{short_id(slug, frag)}" if frag else f"#ch-{slug}"


def rewrite_href(href, slug):
    """章ページ内のリンクを、PDF内のリンクか公開サイトのURLに直す。"""
    if href.startswith(("http:", "https:", "mailto:")):
        return href
    if href.startswith("#"):
        return anchor(slug, href[1:]) if len(href) > 1 else href
    path, _, frag = href.partition("#")
    target = (CHAPTERS / path).resolve()
    if target.parent == CHAPTERS and target.suffix == ".html" and target.stem in ORDER:
        return anchor(target.stem, frag)
    rel = target.relative_to(SITE).as_posix()
    return PUBLIC + ("" if rel == "index.html" else rel) + (("#" + frag) if frag else "")


def chapter_html(slug):
    soup = soup_of(CHAPTERS / f"{slug}.html")
    art = soup.find("article")
    title = art.find("h1").get_text()
    for sel in ["div.crumb", "h1", "nav.chapter-end", ".next-up", ".proof-toggle", "a.chip.maplink", "button", "script"]:
        for t in art.select(sel):
            t.decompose()
    # 見出しを一段下げる（部＝h1、章＝h2、節＝h3）
    for level in (4, 3, 2):
        for h in art.find_all(f"h{level}"):
            h.name = f"h{level + 1}"
    for t in art.find_all(id=True):
        t["id"] = short_id(slug, t["id"])
    for a in art.find_all("a", href=True):
        a["href"] = rewrite_href(a["href"], slug)
    for d in art.find_all("details"):
        d["open"] = ""
        summary = d.find("summary")
        if summary is not None:  # 画面向けの「〜を読む（…）」を、紙面では見出し語だけにする
            summary.string = re.split(r"を(読む|見る)", summary.get_text())[0]
    for au in art.find_all("audio"):
        src = au.get("src") or (au.find("source") or {}).get("src", "")
        note = soup.new_tag("p", attrs={"class": "audio-note"})
        note.string = "試聴音源："
        link = soup.new_tag("a", href=PUBLIC + src.replace("../", ""))
        link.string = PUBLIC + src.replace("../", "")
        note.append(link)
        au.replace_with(note)
    body = "".join(str(c) for c in art.children)
    return title, body


parts_html = []
toc_rows = []
for slug in ORDER:
    if slug in FIRST_OF_PART:
        kicker, ptitle, desc, _ = FIRST_OF_PART[slug]
        pid = f"part-{len(parts_html)}"
        parts_html.append(f'<section class="part-page" id="{pid}">'
                          f'<h1>{html.escape(kicker)}<span class="sep">　</span>{html.escape(ptitle)}</h1><p class="part-desc">{html.escape(desc)}</p></section>')
        toc_rows.append(("part", f"{kicker}　{ptitle}", pid))
    title, body = chapter_html(slug)
    parts_html.append(f'<section class="book-chapter" id="ch-{slug}"><h2 class="chapter-title">{html.escape(title)}</h2>{body}</section>')
    toc_rows.append(("chapter", title, f"ch-{slug}"))


def toc_html(pages):
    rows = []
    for kind, text, target in toc_rows:
        num = pages.get(target, "")
        rows.append(f'<li class="toc-{kind}"><a href="#{target}"><span class="toc-text">{html.escape(text)}</span>'
                    f'<span class="toc-page">{num}</span></a></li>')
    return '<nav class="toc" id="toc"><h1>目次</h1><ol>' + "".join(rows) + "</ol></nav>"


PRINT_CSS = """
@page{size:176mm 250mm;margin:18mm 16mm 20mm 17mm;
  @bottom-center{content:counter(page);font:8.5pt "IPAexGothic",sans-serif;color:#476050}
  @top-right{content:"%(title)s";font:7.5pt "IPAexGothic",sans-serif;color:#7a8a80}}
@page :first{@bottom-center{content:none}@top-right{content:none}}
:root{--serif:"IPAexMincho",serif;--sans:"IPAexGothic",sans-serif}
html{font-size:9.6pt}
*{font-weight:400!important;font-synthesis:none}
strong,b,th,h1,h2,h3,h4,.box-title,.callout-kind,.kicker,summary{font-family:"IPAexGothic",sans-serif!important}
code,pre{font-family:"DejaVu Sans Mono",monospace}
body.book{background:#fff;color:#1f2b25;font-family:"IPAexMincho",serif;line-height:1.85;margin:0}
body.book a{color:#145b47;text-decoration:none}
math{font-family:"STIX Math",math}
.cover{height:210mm;display:flex;flex-direction:column;justify-content:center;break-after:page;font-family:"IPAexGothic",sans-serif}
.cover .ed{letter-spacing:.2em;color:#255d4a;font-weight:700;font-size:10pt}
.cover h1{font-family:"IPAexMincho",serif;font-size:34pt;line-height:1.35;margin:.4em 0}
.cover p{font-size:10.5pt;color:#476050;margin:.3em 0}
.cover img{width:70%%;margin:10mm 0}
.toc{break-after:page;font-family:"IPAexGothic",sans-serif}
.toc h1{font-size:18pt;margin:0 0 4mm}
.toc ol{list-style:none;margin:0;padding:0;columns:2;column-gap:8mm}
.toc li{break-inside:avoid;font-size:8.4pt;line-height:1.5}
.toc a{display:flex;gap:2mm;color:inherit!important}
.toc .toc-text{flex:1}
.toc .toc-page{min-width:7mm;text-align:right;font-variant-numeric:tabular-nums}
.toc .toc-part{font-weight:700;color:#255d4a;margin-top:2.6mm;break-after:avoid}
.toc .toc-chapter{padding:.35mm 0 .35mm 2mm}
.part-page{break-before:page;break-after:page;padding-top:60mm;font-family:"IPAexGothic",sans-serif}
.part-page h1 .sep{display:block;height:0;overflow:hidden}
.part-page h1{font-family:"IPAexMincho",serif;font-size:24pt;margin:.2em 0 .5em}
.part-page .part-desc{color:#476050;max-width:110mm}
.book-chapter{break-before:page}
.book-chapter .chapter-title{font-size:17pt;line-height:1.4;margin:0 0 4mm;border:0;padding:0;color:#173a30}
.book-chapter h3{font-family:"IPAexGothic",sans-serif;font-size:11.5pt;margin:6mm 0 2mm;padding-top:2mm;border-top:.4pt solid #c9d3c3;color:#224f40;break-after:avoid}
.book-chapter h4{font-family:"IPAexGothic",sans-serif;font-size:10.5pt;break-after:avoid}
.book-chapter p,.book-chapter li{line-height:1.85;orphans:2;widows:2}
.book-chapter p{margin:.4em 0 .75em}
.chapter-intro,.takeaways,.callout,.theorem,details,figure,table,pre{break-inside:avoid}
.chapter-intro{margin:0 0 5mm;padding:3mm 4mm;border-radius:2mm;background:#f6f8f2}
.chapter-intro .lead{font-size:10.5pt}
.chip{font-size:7pt!important}
.box-title,.callout-kind{font-family:"IPAexGothic",sans-serif}
details>summary{list-style:none;font-family:"IPAexGothic",sans-serif;font-size:8pt;font-weight:700;color:#255d4a;border:0!important;padding:1.5mm 0 0!important;margin:0!important}
details>summary::-webkit-details-marker{display:none}
details.proof,details.solution{background:#fafbf7;padding:0 3mm .5mm}
figure img{max-height:80mm}
figcaption{font-size:7.8pt}
table{font-size:8pt}
pre{white-space:pre-wrap;font-size:7.6pt}
.audio-note{font-size:8pt;font-family:"IPAexGothic",sans-serif}
.primer{background:none;border-left:2pt solid #7caa8b;padding:1mm 3mm}
.colophon{break-before:page;font-family:"IPAexGothic",sans-serif;font-size:8.5pt;color:#476050;padding-top:150mm}
""" % {"title": TITLE}


def book(pages):
    return f"""<!doctype html><html lang="ja"><head><meta charset="utf-8">
<base href="{CHAPTERS.as_uri()}/"><title>{TITLE}</title>
<link rel="stylesheet" href="../assets/reader.css"><style>{PRINT_CSS}</style></head>
<body class="book">
<section class="cover"><p class="ed">{html.escape(edition)}</p><h1>音楽理論を<br>耳と手で学ぶ</h1>
<p>読譜・和声・形式から、音楽史、音響と聴覚、デジタル制作、電子楽器、そして分野をまたぐ発展編まで</p>
<img src="../assets/cover.webp" alt=""><p>Web版　{PUBLIC}</p></section>
{toc_html(pages)}
{"".join(parts_html)}
<section class="colophon"><p>{html.escape(footer_text)}</p><p>このPDFはWeb版（{PUBLIC}）と同じ構成・同じ本文から生成しています。章番号・図・資料リンクはWeb版と一致します。</p></section>
</body></html>"""


def print_images(tmp):
    """図版を印刷向けの JPEG（白背景）に変換し、元のパスとの対応を返す。Chromium は JPEG をそのまま埋め込むので PDF が軽くなる。"""
    from PIL import Image
    out = {}
    folder = Path(tmp) / "img"
    folder.mkdir(exist_ok=True)
    for img in sorted((SITE / "assets").glob("*.webp")):
        with Image.open(img) as im:
            im = im.convert("RGBA")
            flat = Image.new("RGB", im.size, "white")
            flat.paste(im, mask=im.split()[3])
            dest = folder / (img.stem + ".jpg")
            flat.save(dest, quality=90, optimize=True, progressive=False)
        out["../assets/" + img.name] = dest.as_uri()
    return out


def render(pages, tmp):
    src = Path(tmp) / "book.html"
    text = book(pages)
    for old, new in IMAGES.items():
        text = text.replace(f'src="{old}"', f'src="{new}"')
    src.write_text(text, encoding="utf-8")
    out = Path(tmp) / "book.pdf"
    subprocess.run(["node", str(PRINT_JS), str(src), str(out)], check=True)
    return out


def start_pages(pdf):
    """Chromium がカタログの /Dests に書いたリンク先から、各項目の開始ページを読む。"""
    reader = PdfReader(pdf)
    dests = reader.trailer["/Root"].get("/Dests")
    found = {}
    if dests is not None:
        for name, dest in dests.get_object().items():
            found[name.lstrip("/")] = reader.get_page_number(dest[0].get_object()) + 1
    return found


with tempfile.TemporaryDirectory() as tmp:
    IMAGES = print_images(tmp)
    first = render({}, tmp)
    pages = start_pages(first)
    targets = [t for _, _, t in toc_rows]
    missing = [t for t in targets if t not in pages]
    if missing:
        sys.exit(f"開始ページを特定できない項目があります: {missing[:5]}")
    second = render(pages, tmp)
    check = start_pages(second)
    if any(check[t] != pages[t] for t in targets):
        sys.exit("目次のページ番号が二回目の出力と一致しません")
    OUT_PDF.write_bytes(second.read_bytes())
print(f"{OUT_PDF.relative_to(ROOT)}: {len(PdfReader(OUT_PDF).pages)} ページ, {len(targets)} 項目")
