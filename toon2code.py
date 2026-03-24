import re
import sys
import os

def merge_toon_to_code(toon_path, target_code_path):
    '''
    このスクリプトは、元の .tsx ファイルを読み込み、TOONで指定された「追加要素」を適切なセクション（Import, Logic, Render）に自動でマージします。
    '''
    if not os.path.exists(toon_path) or not os.path.exists(target_code_path):
        return "Error: File not found."

    with open(toon_path, 'r', encoding='utf-8') as f:
        toon_content = f.read()
    
    with open(target_code_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # --- 1. Imports のマージ ---
    import_match = re.search(r'imports:\[(.*?)\]', toon_content)
    if import_match:
        new_imports = import_match.group(1).split(',')
        for imp in new_imports:
            imp = imp.strip()
            # 既存のインポートになければ追加 (簡易的に先頭付近へ)
            if imp not in code and imp != "navigation": # navigation等ライブラリ名は除外
                import_line = f"import {{ {imp} }} from '../hooks/{imp}';\n"
                code = import_line + code

    # --- 2. Logic (Hooks) のマージ ---
    # TOON内の logic: セクションを抽出
    logic_section = re.search(r'logic:(.*?)(?=\n\s*\w+:|$)', toon_content, re.DOTALL)
    if logic_section:
        hooks = re.findall(r'(\w+)\((.*?)\) -> \[(.*?)\]', logic_section.group(1))
        for h_name, h_args, h_vars in hooks:
            h_vars = h_vars.strip()
            if h_vars not in code:
                # 最後のHook呼び出しの後ろに挿入を試みる
                insertion_point = re.findall(r'const\s+[\{\[].*?\}\]\s*=\s*\w+\(.*?\);', code)
                if insertion_point:
                    last_hook = insertion_point[-1]
                    new_hook_line = f"\n  const {{ {h_vars} }} = {h_name}({h_args});"
                    code = code.replace(last_hook, last_hook + new_hook_line)

    # --- 3. Render (Props) のマージ ---
    # 例: isFavorite:isFavorite(product.id) のようなパターンを探す
    render_props = re.findall(r'(\w+):(\w+\([\w\.]+\))', toon_content)
    for p_name, p_val in render_props:
        if p_name not in code:
            # 適切なコンポーネント（ここではRankingItemを想定）のPropsに挿入
            # <RankingItem ... /> の中に新しいPropを追加
            code = re.sub(
                r'(<RankingItem[^>]*?)(\s*/>)',
                fr'\1\n            {p_name}={{{p_val}}}\2',
                code
            )

    # 変更を保存
    with open(target_code_path, 'w', encoding='utf-8') as f:
        f.write(code)
    
    return f"Successfully merged TOON into {target_code_path}"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python toon2code.py <input.toon> <target.tsx>")
    else:
        result = merge_toon_to_code(sys.argv[1], sys.argv[2])
        print(result)
