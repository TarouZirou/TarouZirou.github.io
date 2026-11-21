# 音楽理論を耳と手で学ぶ

GitHub Pages で公開している音楽理論の教材です。公開先: https://tarouzirou.github.io/music-theory/

- `music-theory/index.html` 目次・目的別のコース・検索
- `music-theory/chapters/` 全60章と付録（本書の使い方、6つの順路、証明、解答、索引）
- `music-theory/map.html` 章どうしのつながりをたどる地図
- `music-theory/music-lab.html` ブラウザで音を鳴らして試す実験室
- `music-theory/resources.html` 譜例・試聴音源・ダウンロード

## 構成

| 部 | 章 | 内容 |
| --- | --- | --- |
| I | 1–5 | 耳・身体・楽譜 |
| II | 6–11 | 音階・旋律・和声 |
| III | 12–15 | 対位法・編成・形式 |
| IV | 16–19 | ジャズ・ポピュラー・20世紀以降 |
| V | 20–23 | 音楽史と文化 |
| VI | 24–29 | 音の物理と聴覚 |
| VII | 30–37 | デジタル音響と制作 |
| VIII | 38–42 | 電子楽器と総合制作 |
| IX–XI | 43–60 | 発展編（音の形と空間、リズムと対称性、時間を書く技術） |

Web版では、元の第16〜29章（和声・旋律・形式など）を第6〜19章へ、元の第6〜15章（歴史・物理・聴覚）を第20〜29章へ移しました。第1〜5章と第30〜60章の番号は元のままです。

## PDF

`music-theory/assets/music-theory.pdf`（A4）は Web版のページから生成しており、章番号・本文・図がサイトと一致します。サイトの本文を直したら、次のコマンドで作り直してください。章の並びと部の区切りは `music-theory/index.html` の目次から読み取ります。

```sh
python3 tools/pdf/build_pdf.py
```

必要なもの: Python 3（beautifulsoup4, pypdf, Pillow）、Node.js と playwright（Chromium）、フォント IPAex明朝・IPAexゴシック・STIX Math。Debian/Ubuntu なら `apt-get install fonts-ipaexfont-mincho fonts-ipaexfont-gothic fonts-stix`。

`music-theory/assets/music-theory-typeset-original.pdf` は並べ替える前の LaTeX 組版版で、章番号が Web版と異なります。

## 楽譜

本文の楽譜（`staff.webp`、`melody_score.webp`、`counterpoint_score.webp`）は `tools/scores/*.ly` を LilyPond で組んだものです。符頭の高さは五線の線間ちょうどで、どの楽譜も同じ譜表サイズ・同じ解像度（220dpi）で作り、サイトでも PDF でも同じ倍率で表示します。楽譜を足すときも `tools/scores/common.ily` を読み込んで同じ大きさにしてください。

```sh
python3 tools/scores/build.py   # 画像を作り直し、各ページの表示幅も更新する
python3 tools/pdf/build_pdf.py  # PDF に反映する
```

必要なもの: LilyPond 2.24、Pillow。

