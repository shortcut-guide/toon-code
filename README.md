リポジトリ `shortcut-guide/toon-code` のための、クールで実用的な **README.md** のドラフトを作成しました。

このプロジェクトの核心である「コードの量子化」と「トークン節約」を強調し、他の開発者がすぐに試せるような構成にしています。

TOON
[https://github.com/toon-format/toon](https://github.com/toon-format/toon)

---

# TOON Code

## 🚀 Code Quantization for AI Native Development

**TOON Code** は、ソースコードを AI（Gemini, Claude, GPT-4）が理解しやすい「量子化された構造データ」に変換し、トークン消費を劇的に抑えながら開発効率を最大化するためのツールキットです。

### 🌟 Why TOON Code?

- 現代の AI 開発において、コンテキストウィンドウの制限とトークンコストは大きな課題です。
- TOON Code は、冗長な構文を削ぎ落とし、**「データフローと構造」**のみを抽出することで以下のメリットを提供します。

* **トークン削減**: 生の TypeScript/Next.js コードと比較して 70〜90% のトークンを削減。
* **推論精度の向上**: ノイズ（複雑なロジックやスタイル定義）を排除し、AI がアーキテクチャの核心に集中できるようにします。
* **高速なフィードバック**: 軽量なデータ構造により、AI のレスポンス速度が向上します。

---

### 🛠 Installation

```bash
git clone https://github.com/shortcut-guide/toon-code.git
```

※ 現在、Python 3.8+ が必要です。

---

### 📖 Usage

#### 1. コードを TOON 形式に「量子化」する
既存のコンポーネントやロジックを解析し、AI 送信用の TOON データを生成します。

```bash
python toon-code/ts2toon.py path/to/YourComponent.tsx
```

**Output Example:**
```text
component:RankingList
  client:true
  imports:[usePathname,Product,useRankingPagination]
  props:
    products:Product[]
    pageSize:int
  logic:
    useRankingPagination(products,pageSize) -> [page,totalPages,gotoPage]
  render_tree:
    contains:[RankingItem,RankingPagination,LoadingOverlay]
```

#### 2. AI に依頼する
- 生成された TOON をコピーして、Cloud Code Gemini や Claude に貼り付けます。
> 「この TOON 構造に、お気に入り機能を追加して修正版を TOON で返して」

#### 3. 差分を適用する（開発中）
AI から返ってきた TOON を元のコードにマージします。

---

## toon2code.py: TOON to Source Merger
🛠 使い方とコミット手順
AIの回答を保存: Geminiから返ってきたTOONを update.toon として保存します。

マージ実行:
```
python toon-code/toon2code.py update.toon path/to/RankingList.tsx
```

リポジトリへ追加:
```
git add toon2code.py
git commit -m "feat: add toon2code merger script for applying AI suggestions"
git push origin main
```

- 既存のコードを正規表現でスキャンし、不足しているパーツだけを「差し込む」動きをします。
- 依存関係の解決: TOONに新しいHook名があれば、自動的に import 文を生成してファイルの先頭に追加します。
- 柔軟な Props 追加: コンポーネントの閉じタグ /> を検知して、その直前に新しい Props を改行付きで挿入します。

#### 3. プロジェクト全体を一括で「量子化」する
- ディレクトリ内のすべての TypeScript/TSX ファイルをスキャンし、プロジェクトの構造を1つの TOON ブロックにまとめます。
- AIにプロジェクト全体のコンテキスト（依存関係やアーキテクチャ）を伝えたい場合に有効です。

AIへのプロンプト例:

「これがプロジェクト全体の構造です。この構成を維持したまま、新しい共通コンポーネント UserAvatar を components/common に作成し、全ページで適用する設計をTOONで出して。」

```bash
python toon-code/2toon.py . > full_project.toon
```
---
# minify+TOON
約65%の削減
1. minify
2. TOON
3. 復元

[https://github.com/shortcut-guide/minifyForAI](https://github.com/shortcut-guide/minifyForAI)

## 問題点
- ⭕️ 状態管理(useState)やイベントハンドラのロジックは完璧に復元されています。
- ❌ コメントは復元されていません。
- ❌ className="counter-wrapper" などのUIの詳細情報はTOONに含まれていなかったため、AIが推測して省略（または別の名前で補完）しています。

---
# CoD + TOON + GSD フレームワークの定義
- 要素,役割,フェーズ,アウトプット
- CoD,思考の凝縮,Plan (戦略),A -> B -> C (ロジックの矢印)
- TOON,構造の量子化,Design (設計),component:X { logic:Y } (構造データ)
- GSD,実行の自動化,Execute (実行),toon2code.py による自動マージとビルド

# 「GSD」ワークフロー
- Plan (CoD): AIに Draft: A -> B -> C と伝え、TOONパッチを出力させる。
- Save: AIの回答を patch.toon に保存。
- Execute (GSD): python gsd.py patch.toon src/App.tsx を実行。
- Done: エラーがなければ実装完了。エラーがあれば、表示された type:error_log をAIに投げて修正TOONを貰い、再度 gsd.py を回す。
---
# GSD 自己修復ワークフロー
- Execute: python gsd.py patch.toon target.tsx でパッチ適用。
- Diagnose: python gsd_repair.py が自動で型チェックし、エラーをTOON化。
- Draft & Repair: AIに「診断TOON」を投げ、新しい「修正TOON」を受け取る。
- Repeat: 1に戻る。
---
# 自律型自動修復
gsd_autonomous.py
Gemini API（または Vertex AI API）と直接通信し、人間を介さずに「エラー検知 → 診断 → CoD思考 → TOONパッチ生成 → 適用 → 再検証」を成功するまで（またはリミットまで）自動で回し続けます。

- Context-Aware: generate_toon を使って、現在のファイルの構造（量子化データ）を Gemini に送ります。これにより、AI はファイル全体を読まずとも、Props や Hooks の構成を把握した上で修正案を出せます。
- CoD-Driven: プロンプトで「CoD を使って根本原因を特定せよ」と強制しています。これにより、場当たり的な修正ではなく、論理的な裏付けのあるパッチが生成されます。
- Hands-Free: 人間は python gsd_autonomous.py ... を実行してコーヒーを飲みに行くだけです。AI がビルドを通すまで試行錯誤します。

## 自動PR機能
修正が成功（ビルドが通過）した際に、自動で新しいブランチを作成し、コミット、そして GitHub CLI (gh) を利用してプルリクエストを飛ばす機能
- 非同期的な開発: あなたが別の作業をしている間に、AIが裏側でバグを直し、テストを通し、ブランチを切ってPRまで作っておいてくれます。あなたは通知が来たら、GitHubで「Approve」ボタンを押すだけです。
- トレーサビリティ: PRの本文に「AIがどう診断したか（TOON）」が自動で記載されるため、人間がレビューする際も「なぜこの修正が必要だったか」が即座にわかります。
- 安全性の担保: npx tsc --noEmit（またはあなたのプロジェクトのビルドコマンド）を通ったものしかPRにならないため、壊れたコードがメインブランチに混入することはありません。

---
### 🗺 Roadmap

- [x] **ts2toon.py**: TypeScript/TSX の基本解析と TOON 生成
- [x] **toon2code.py**: TOON 構造からソースコードへの自動マージ機能
- [x] **2toon.py**: プロジェクト全体の構造を1つに集約
- [ ] **Project Quantizer**: 複数ファイル間の依存関係を 1 つの TOON に集約

---

### 🤝 Contributing

「コードをより効率的に AI に伝える」ためのアイデアを募集中です！プルリクエストや Issue はいつでも歓迎します。

---

### 📄 License

MIT License

---
