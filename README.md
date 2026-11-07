# web-color

ウェブカラー見本のページです。

公開ページ: https://ojklab.github.io/web-color/

## 色見本の作り直し

`index.html` の色見本（`<!-- swatches:start -->` から `<!-- swatches:end -->` まで）は、スクリプトで作っています。色の一覧や並べ方を変えたいときは、[scripts/gen_colors.py](scripts/gen_colors.py) を直してから、リポジトリーのルートで次を実行してください。

```bash
python3 scripts/gen_colors.py
```

この部分を `index.html` で直接書き換えても、次にスクリプトを実行したときに上書きされます。
