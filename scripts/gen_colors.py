"""CSS 名前付きカラー（148 個）から同色の別名を除いた 139 色の色見本を作り、
index.html の <!-- swatches:start --> と <!-- swatches:end --> の間を書き換える。

並べ方: 見た目の明るさ（OKLab の L）で色数がほぼ同じ 5 段階に分け、
各段の中は無彩色（白・灰・黒）を先頭に明るい順、そのあと色相順。

使い方（リポジトリーのルートで）:
    python3 scripts/gen_colors.py
"""
import colorsys
import re
import sys
from pathlib import Path

DEFAULT_INDEX = Path(__file__).resolve().parent.parent / "index.html"

COLORS = """
aliceblue F0F8FF
antiquewhite FAEBD7
aqua 00FFFF
aquamarine 7FFFD4
azure F0FFFF
beige F5F5DC
bisque FFE4C4
black 000000
blanchedalmond FFEBCD
blue 0000FF
blueviolet 8A2BE2
brown A52A2A
burlywood DEB887
cadetblue 5F9EA0
chartreuse 7FFF00
chocolate D2691E
coral FF7F50
cornflowerblue 6495ED
cornsilk FFF8DC
crimson DC143C
cyan 00FFFF
darkblue 00008B
darkcyan 008B8B
darkgoldenrod B8860B
darkgray A9A9A9
darkgreen 006400
darkgrey A9A9A9
darkkhaki BDB76B
darkmagenta 8B008B
darkolivegreen 556B2F
darkorange FF8C00
darkorchid 9932CC
darkred 8B0000
darksalmon E9967A
darkseagreen 8FBC8F
darkslateblue 483D8B
darkslategray 2F4F4F
darkslategrey 2F4F4F
darkturquoise 00CED1
darkviolet 9400D3
deeppink FF1493
deepskyblue 00BFFF
dimgray 696969
dimgrey 696969
dodgerblue 1E90FF
firebrick B22222
floralwhite FFFAF0
forestgreen 228B22
fuchsia FF00FF
gainsboro DCDCDC
ghostwhite F8F8FF
gold FFD700
goldenrod DAA520
gray 808080
green 008000
greenyellow ADFF2F
grey 808080
honeydew F0FFF0
hotpink FF69B4
indianred CD5C5C
indigo 4B0082
ivory FFFFF0
khaki F0E68C
lavender E6E6FA
lavenderblush FFF0F5
lawngreen 7CFC00
lemonchiffon FFFACD
lightblue ADD8E6
lightcoral F08080
lightcyan E0FFFF
lightgoldenrodyellow FAFAD2
lightgray D3D3D3
lightgreen 90EE90
lightgrey D3D3D3
lightpink FFB6C1
lightsalmon FFA07A
lightseagreen 20B2AA
lightskyblue 87CEFA
lightslategray 778899
lightslategrey 778899
lightsteelblue B0C4DE
lightyellow FFFFE0
lime 00FF00
limegreen 32CD32
linen FAF0E6
magenta FF00FF
maroon 800000
mediumaquamarine 66CDAA
mediumblue 0000CD
mediumorchid BA55D3
mediumpurple 9370DB
mediumseagreen 3CB371
mediumslateblue 7B68EE
mediumspringgreen 00FA9A
mediumturquoise 48D1CC
mediumvioletred C71585
midnightblue 191970
mintcream F5FFFA
mistyrose FFE4E1
moccasin FFE4B5
navajowhite FFDEAD
navy 000080
oldlace FDF5E6
olive 808000
olivedrab 6B8E23
orange FFA500
orangered FF4500
orchid DA70D6
palegoldenrod EEE8AA
palegreen 98FB98
paleturquoise AFEEEE
palevioletred DB7093
papayawhip FFEFD5
peachpuff FFDAB9
peru CD853F
pink FFC0CB
plum DDA0DD
powderblue B0E0E6
purple 800080
rebeccapurple 663399
red FF0000
rosybrown BC8F8F
royalblue 4169E1
saddlebrown 8B4513
salmon FA8072
sandybrown F4A460
seagreen 2E8B57
seashell FFF5EE
sienna A0522D
silver C0C0C0
skyblue 87CEEB
slateblue 6A5ACD
slategray 708090
slategrey 708090
snow FFFAFA
springgreen 00FF7F
steelblue 4682B4
tan D2B48C
teal 008080
thistle D8BFD8
tomato FF6347
turquoise 40E0D0
violet EE82EE
wheat F5DEB3
white FFFFFF
whitesmoke F5F5F5
yellow FFFF00
yellowgreen 9ACD32
"""

# 同じ色を指す別名のうち、使わないほう
DROP = {"aqua", "fuchsia", "darkgrey", "darkslategrey", "dimgrey", "grey",
        "lightgrey", "lightslategrey", "slategrey"}


BAND_TITLES = ["とても明るい", "明るい", "中くらい", "暗い", "とても暗い"]
# この文字数以上の色名は、カードに収まるよう少し小さく表示する
LONG_NAME = 16
BAND_IDS = ["very-light", "light", "medium", "dark", "very-dark"]
START = "  <!-- swatches:start -->"
END = "  <!-- swatches:end -->"


def main(index_path):
    pairs = [line.split() for line in COLORS.strip().splitlines()]
    assert len(pairs) == 148, len(pairs)
    colors = [(n, "#" + h) for n, h in pairs if n not in DROP]
    assert len(colors) == 139, len(colors)
    assert len({h for _, h in colors}) == 139, "duplicate hex remains"

    def parse(h):
        return [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]

    def oklab_lightness(h):
        """見た目の明るさに近い OKLab の L（0〜1）"""
        def lin(c):
            return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        r, g, b = (lin(c) for c in parse(h))
        l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
        m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
        s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
        return 0.2104542553 * l ** (1 / 3) + 0.7936177850 * m ** (1 / 3) - 0.0040720468 * s ** (1 / 3)

    def hue_key(item):
        hue, light, sat = colorsys.rgb_to_hls(*parse(item[1]))
        # 段の中では無彩色（白・灰・黒）を先に明るい順、そのあと色相順
        if sat == 0:
            return (0, -light)
        return (1, hue)

    # 明るい順に並べ、色数がほぼ同じになるよう 5 段階に分ける
    colors.sort(key=lambda c: -oklab_lightness(c[1]))
    bands = [colors[len(colors) * i // 5: len(colors) * (i + 1) // 5] for i in range(5)]

    btn = '<button type="button" class="copy {cls}" title="クリックでコピー">{text}</button>'
    # 各段の見出しへのページ内リンク
    parts = ['  <nav class="bands" aria-label="明るさの段">']
    parts += [f'    <a href="#{bid}">{title}</a>' for bid, title in zip(BAND_IDS, BAND_TITLES)]
    parts.append('  </nav>')
    for bid, title, band in zip(BAND_IDS, BAND_TITLES, bands):
        band.sort(key=hue_key)
        parts.append(f'  <h2 id="{bid}">{title}（{len(band)} 色）</h2>')
        parts.append('  <div class="grid">')
        parts += [
            f'    <div class="swatch"><div class="chip" style="background:{n}"></div>'
            f'<div class="label">{btn.format(cls="name long" if len(n) >= LONG_NAME else "name", text=n)}{btn.format(cls="hex", text=h)}</div></div>'
            for n, h in band
        ]
        parts.append('  </div>')

    html = open(index_path, encoding="utf-8").read()
    block = START + "\n" + "\n".join(parts) + "\n" + END
    pattern = re.escape(START) + ".*?" + re.escape(END)
    if START not in html:
        # 初回: 既存の色見本グリッドを置き換える
        pattern = r'  <div class="grid">\n.*?\n  </div>'
    html, count = re.subn(pattern, lambda _: block, html, flags=re.S)
    assert count == 1
    open(index_path, "w", encoding="utf-8").write(html)
    for title, band in zip(BAND_TITLES, bands):
        print(title, len(band), " ".join(n for n, _ in band))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INDEX)
