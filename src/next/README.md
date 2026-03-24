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
---

## 運用フロー
ターミナルで実行: npm run build (または npm run sync:ai)

IDEでの操作:
1. Cloud Code の Gemini チャットを開く。
2. Ctrl + V (貼り付け) をして送信。
3. AIの反応: Geminiが「プロジェクト全体の最新構造（TOON）」を把握した状態になり、その後のコード生成やリファクタリングの精度が最大化されます。
