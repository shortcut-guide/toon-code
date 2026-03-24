import re
import sys
import os

def generate_toon(file_path):
    """
    TypeScript/TSXファイルを解析し、AI向けの量子化データ(TOON)を生成する
    """
    if not os.path.exists(file_path):
        return f"Error: File {file_path} not found."

    with open(file_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # 1. コンポーネント名の抽出 (Default Export)
    comp_match = re.search(r'export default function (\w+)', code)
    comp_name = comp_match.group(1) if comp_match else "UnknownComponent"

    # 2. インポートの抽出 (モジュール名に凝縮)
    imports = re.findall(r'from ["\'](.+?)["\']', code)
    clean_imports = [imp.split('/')[-1] for imp in imports]

    # 3. Propsの抽出 (型定義ブロックをスキャン)
    props_block = re.search(r'type Props = \{(.*?)\};', code, re.DOTALL)
    props = []
    if props_block:
        props = re.findall(r'(\w+)\??:\s*([\w\[\]<>| ]+)', props_block.group(1))

    # 4. Hooks (Logic) の抽出 
    # const { vars } = useHook(args) のパターン
    hooks = re.findall(r'const\s+[\{\[]?\s*([\w\s,:]+)\s*[\}\]]?\s*=\s*(\w+)\((.*?)\)', code)

    # 5. コンポーネントツリーの抽出 (JSXタグの抽出)
    components = re.findall(r'<([A-Z][\w\.]*)', code)
    unique_components = sorted(list(set(components)))

    # --- TOON 形式の構築 ---
    toon = [f"component:{comp_name}"]
    
    # Next.js Client Directive チェック
    if '"use client"' in code or "'use client'" in code:
        toon.append("  client:true")

    # インポート情報の圧縮表示
    if clean_imports:
        toon.append(f"  imports:[{','.join(dict.fromkeys(clean_imports))}]")

    # Props 定義の量子化
    if props:
        toon.append("  props:")
        for p_name, p_type in props:
            # 型名の空白を詰める
            p_type_clean = p_type.strip().replace(" ", "")
            toon.append(f"    {p_name}:{p_type_clean}")

    # ロジック(Hooks)の抽出
    if hooks:
        toon.append("  logic:")
        for vars, name, args in hooks:
            clean_vars = re.sub(r'\s+', '', vars)
            toon.append(f"    {name}({args.strip()}) -> [{clean_vars}]")

    # レンダリング構造のサマリー
    if unique_components:
        toon.append("  render_tree:")
        toon.append(f"    contains:[{','.join(unique_components)}]")

    return "\n".join(toon)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ts2toon.py <path_to_ts_file>")
    else:
        print(generate_toon(sys.argv[1]))
