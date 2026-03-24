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

---
# AIへの依頼からコード反映までの流れをシミュレーション
## 1. AIへのプロンプト
npm run sync:ai でクリップボードにコピーされた project.toon を貼り付けた後、以下のように指示します。

指示:
以下のTOONコンテキストに基づき、お気に入り機能に「登録日時（favoritedAt）」を記録する機能を追加してください。

Prismaの Product モデルに favoritedAt (DateTime, optional) を追加。

RankingList コンポーネントでその日時を表示するよう修正。
回答は imports, logic, render_update を含むTOON差分形式で出してください。

## 2. AIからの回答（TOON差分）
```
# DB Schema Update
type:prisma_patch
  model:Product[favoritedAt:DateTime?]

# Component Update
imports:[format]
logic:
  useFavorite(pageItems) -> [isFavorite, toggleFavorite, getFavoriteDate]
render_update:
  @RankingItem[
    isFavorite:isFavorite(product.id),
    favoritedAt:getFavoriteDate(product.id)
  ]
```
## 3. コードへの反映ワークフロー
### ステップ A: データベースの反映
PrismaのTOON差分を見て、schema.prisma を修正し、マイグレーションを実行します。
```
# schema.prisma に favoritedAt DateTime? を手動追加後
npx prisma migrate dev --name add_favorited_at
```

### ステップ B: フロントエンドの反映（自動）
AIが返したコンポーネント用のTOONを update.toon に保存し、作成したスクリプトで一気に適用します。
```
python toon2code.py update.toon path/to/RankingList.tsx
```
---
# syncのメリット
　- 型の不整合がなくなる: AIが schema.prisma の型（DateTime?）を知っているため、フロントエンドで undefined チェックが必要であることを自動的に考慮したコードを生成します。
- ビジネスロジックの集中: 「DBには日付があるが、画面には出ていない」といった漏れをAIが指摘できるようになります。
- トークンの圧倒的節約: DB構造を教えるために schema.prisma を丸ごと送る必要はなく、量子化された数行の model:Product[...] だけで、AIは背後のリレーションまで推測できます。
