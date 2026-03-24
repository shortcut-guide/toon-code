リポジトリ `shortcut-guide/toon-code` のための、クールで実用的な **README.md** のドラフトを作成しました。

このプロジェクトの核心である「コードの量子化」と「トークン節約」を強調し、他の開発者がすぐに試せるような構成にしています。

TOON
(https://github.com/toon-format/toon)[https://github.com/toon-format/toon]


---

# TOON Code

## 🚀 Code Quantization for AI Native Development

**TOON Code** は、ソースコードを AI（Gemini, Claude, GPT-4）が理解しやすい「量子化された構造データ」に変換し、トークン消費を劇的に抑えながら開発効率を最大化するためのツールキットです。

### 🌟 Why TOON Code?

現代の AI 開発において、コンテキストウィンドウの制限とトークンコストは大きな課題です。TOON Code は、冗長な構文を削ぎ落とし、**「データフローと構造」**のみを抽出することで以下のメリットを提供します。

* **トークン削減**: 生の TypeScript/Next.js コードと比較して 70〜90% のトークンを削減。
* **推論精度の向上**: ノイズ（複雑なロジックやスタイル定義）を排除し、AI がアーキテクチャの核心に集中できるようにします。
* **高速なフィードバック**: 軽量なデータ構造により、AI のレスポンス速度が向上します。

---

### 🛠 Installation

```bash
git clone https://github.com/shortcut-guide/toon-code.git
cd toon-code
```

※ 現在、Python 3.8+ が必要です。

---

### 📖 Usage

#### 1. コードを TOON 形式に「量子化」する
既存のコンポーネントやロジックを解析し、AI 送信用の TOON データを生成します。

```bash
python ts2toon.py path/to/YourComponent.tsx
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
生成された TOON をコピーして、Cloud Code Gemini や Claude に貼り付けます。
> 「この TOON 構造に、お気に入り機能を追加して修正版を TOON で返して」

#### 3. 差分を適用する（開発中）
AI から返ってきた TOON を元のコードにマージします。

---

## toon2code.py: TOON to Source Merger
🛠 使い方とコミット手順
AIの回答を保存: Geminiから返ってきたTOONを update.toon として保存します。

マージ実行:
```
python toon2code.py update.toon path/to/RankingList.tsx
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

---

### 🗺 Roadmap

- [x] **ts2toon.py**: TypeScript/TSX の基本解析と TOON 生成
- [x] **toon2code.py**: TOON 構造からソースコードへの自動マージ機能
- [ ] **VS Code Extension**: 右クリックメニューから「Copy as TOON」を実行
- [ ] **Project Quantizer**: 複数ファイル間の依存関係を 1 つの TOON に集約

---

### 🤝 Contributing

「コードをより効率的に AI に伝える」ためのアイデアを募集中です！プルリクエストや Issue はいつでも歓迎します。

---

### 📄 License

MIT License

---
