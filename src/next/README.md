# 🏗 CI/CD & Build Integration

`package.json` に以下を追記することで、ビルド時に自動でプロジェクトの量子化データを生成できます。

```bash
"scripts": {
  "build:toon": "python project2toon.py . > project.toon"
}
```

## 実行
```
npm run build:toon
```

## 💡 応用：差分ビルド（Git連携）
プロジェクトが大きくなった場合、全ファイルを毎回ビルドすると時間がかかるかもしれません。
その場合は、**「Git で変更があったファイルだけを TOON 化する」** スクリプトを `scripts` に入れるのも手です。

```bash
# Git のステージ上のファイルだけを TOON 化して表示（Mac/Linux例）
git diff --name-only --cached | grep -E "\.tsx?$" | xargs -I {} python ts2toon.py {}
```
