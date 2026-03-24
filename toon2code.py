import re
import sys
import os

def merge_toon_to_code_v2(toon_path, target_code_path):
    if not os.path.exists(toon_path) or not os.path.exists(target_code_path):
        return "Error: File not found."

    with open(toon_path, 'r', encoding='utf-8') as f:
        toon_content = f.read()
    
    with open(target_code_path, 'r', encoding='utf-8') as f:
        code = f.read()

    # --- 1. Imports のマージ (前回同様) ---
    import_match = re.search(r'imports:\[(.*?)\]', toon_content)
    if import_match:
        new_imports = import_match.group(1).split(',')
        for imp in new_imports:
            imp = imp.strip()
            if imp not in code and imp not in ["navigation", "React"]:
                import_line = f"import {{ {imp} }} from '../hooks/{imp}';\n"
                code = import_line + code

    # --- 2. Logic (Hooks) のマージ ---
    logic_section = re.search(r'logic:(.*?)(?=\n\s*\w+:|$)', toon_content, re.DOTALL)
    if logic_section:
        hooks = re.findall(r'(\w+)\((.*?)\) -> \[(.*?)\]', logic_section.group(1))
        for h_name, h_args, h_vars in hooks:
            h_vars = h_vars.strip()
            if h_vars not in code:
                # 最後のHookの直後に挿入
                last_hook_pos = [m.end() for m in re.finditer(r'const\s+[\{\[].*?\}\]\s*=\s*\w+\(.*\);', code)]
                if last_hook_pos:
                    pos = last_hook_pos[-1]
                    new_line = f"\n  const {{ {h_vars} }} = {h_name}({h_args});"
                    code = code[:pos] + new_line + code[pos:]

    # --- 3. 【拡張】明示的Props注入 (@Component[prop:val]) ---
    # @ComponentName[prop:value] を抽出
    prop_updates = re.findall(r'@(\w+)\[(\w+):(.*?)\]', toon_content)
    
    for comp_name, prop_name, prop_val in prop_updates:
        # すでにそのPropが存在するかチェック（重複防止）
        if f"{prop_name}=" in code:
            continue

        # 対象コンポーネントの開始タグ内を探して挿入
        # 例: <RankingItem ... /> または <RankingItem ... >...</RankingItem>
        pattern = fr'(<{comp_name}\b[^>]*?)(/?>)'
        
        def add_prop(match):
            base_tag = match.group(1)
            closing = match.group(2)
            # 属性の前に改行とインデントを入れつつ挿入
            return f'{base_tag}\n            {prop_name}={{{prop_val}}}{closing}'

        code = re.sub(pattern, add_prop, code, count=1)

    # 変更を保存
    with open(target_code_path, 'w', encoding='utf-8') as f:
        f.write(code)
    
    return f"Successfully merged extended TOON into {target_code_path}"

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python toon2code.py <input.toon> <target.tsx>")
    else:
        print(merge_toon_to_code_v2(sys.argv[1], sys.argv[2]))
