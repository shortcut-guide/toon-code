import re
import sys
import os

def merge_toon_to_code_v3(toon_path, target_code_path):
    if not os.path.exists(toon_path): return f"Error: TOON file not found"
    with open(toon_path, 'r', encoding='utf-8') as f: toon_content = f.read()
    if os.path.exists(target_code_path):
        with open(target_code_path, 'r', encoding='utf-8') as f: code = f.read()
    else: code = ""

    # TOONファイルを複数のコンポーネントブロックに分割
    blocks = toon_content.split('\n---\n')
    
    for block in blocks:
        # --- 1. Client & Imports ---
        if "client:true" in block and '"use client"' not in code: code = '"use client";\n\n' + code
        import_match = re.search(r'imports:\n((?:\s+-\s+.*\n?)*)', block)
        if import_match:
            for line in import_match.group(1).strip().split('\n'):
                m = re.match(r'-\s+(.+?):\s+\[(.*?)\]', line.strip())
                if m and f'from "{m.group(1)}"' not in code and f"from '{m.group(1)}'" not in code:
                    code = f'import {{ {m.group(2)} }} from "{m.group(1)}";\n' + code

        comp_match = re.search(r'(?:component|hook):(\w+)', block)
        comp_name = comp_match.group(1) if comp_match else "UnknownComponent"
        
        # --- 2. Types ---
        types_match = re.search(r'types:\n((?:\s+-\s+.*\n?)*)', block)
        types_code = ""
        if types_match:
            for line in types_match.group(1).strip().split('\n'):
                t_def = line.strip()[2:]
                n_match = re.match(r'(?:interface|type)\s+(\w+)', t_def)
                if n_match and f"interface {n_match.group(1)}" not in code and f"type {n_match.group(1)}" not in code:
                    types_code += f"export {t_def}\n\n"
                    
        # --- 3. Render Tree (JSXの正確なマージ) ---
        render_tree_match = re.search(r'render_tree:\n((?:\s+-\s+.*\n?)*)', block)
        if render_tree_match and "return null;" not in code:
            render_lines = render_tree_match.group(1).strip().split('\n')
            
            # このコンポーネントの記述開始位置を特定（他のコンポーネントを誤置換しないため）
            comp_start_idx = code.find(f"function {comp_name}")
            if comp_start_idx == -1: comp_start_idx = code.find(f"const {comp_name}")
            if comp_start_idx == -1: comp_start_idx = 0
            
            tag_counts = {}
            for line in render_lines:
                element_def = line.strip()[2:]
                tag_match = re.match(r'([a-zA-Z0-9_]+)(?:\((.*)\))?', element_def)
                if tag_match:
                    tag_name = tag_match.group(1)
                    attrs_str = tag_match.group(2) or ""
                    
                    tag_counts[tag_name] = tag_counts.get(tag_name, 0) + 1
                    n_th = tag_counts[tag_name]
                    
                    # classNameの値を抽出（"...", '...', {...} のどれか）
                    class_match = re.search(r'className:(".*?"|\'.*?\'|\{.*?\})', attrs_str)
                    if class_match:
                        new_class_full = class_match.group(1)
                        
                        # comp_start_idx 以降の該当タグを検索
                        tag_pattern = re.compile(rf'(<\s*{tag_name}\b)([^>]*?)(/?>)', re.DOTALL)
                        matches = list(tag_pattern.finditer(code, comp_start_idx))
                        
                        if len(matches) >= n_th:
                            m = matches[n_th - 1]
                            tag_start = m.group(1)
                            old_attrs = m.group(2) or ""
                            tag_end = m.group(3)
                            
                            if 'className=' in old_attrs:
                                # 古いclassName全体を安全に置換する
                                new_attrs = re.sub(r'className\s*=\s*(?:".*?"|\'.*?\'|\{[^>]*\})', f'className={new_class_full}', old_attrs, count=1)
                                if new_attrs == old_attrs: # 正規表現が失敗した場合のフォールバック
                                    new_attrs = re.sub(r'className\s*=\s*\S+', f'className={new_class_full}', old_attrs, count=1)
                            else:
                                new_attrs = f' className={new_class_full}' + old_attrs
                                
                            code = code[:m.start()] + tag_start + new_attrs + tag_end + code[m.end():]

    with open(target_code_path, 'w', encoding='utf-8') as f: f.write(code)
    return f"Successfully restored/merged TOON into {target_code_path}"

if __name__ == "__main__":
    if len(sys.argv) < 3: print("Usage: python toon2code.py <input.toon> <target.ts>")
    else: print(merge_toon_to_code_v3(sys.argv[1], sys.argv[2]))
