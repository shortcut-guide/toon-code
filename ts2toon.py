import re
import sys
import os

def generate_toon(file_path):
    if not os.path.exists(file_path):
        return f"Error: File {file_path} not found."
    ext = os.path.splitext(file_path)[1].lower()
    try:
        with open(file_path, 'r', encoding='utf-8') as f: code = f.read()
    except Exception as e: return f"Error reading file: {str(e)}"
    if ext in ['.ts', '.tsx']: return parse_typescript(code)
    return f"type:raw\n  file:{os.path.basename(file_path)}"

def parse_typescript(code):
    # 1. Imports / Types の抽出 (ファイル全体)
    import_dict = {}
    named_imports = re.findall(r'import\s+\{([^}]+)\}\s+from\s+["\']([^"\']+)["\']', code)
    for items, path in named_imports:
        clean_items = [i.strip() for i in items.split(',')]
        if path not in import_dict: import_dict[path] = []
        import_dict[path].extend(clean_items)
        
    default_imports = re.findall(r'import\s+(\w+)\s+from\s+["\']([^"\']+)["\']', code)
    for item, path in default_imports:
        if path not in import_dict: import_dict[path] = []
        import_dict[path].append(item)

    interfaces = re.findall(r'(?:export\s+)?interface\s+(\w+)\s*\{([^}]+)\}', code)
    types = re.findall(r'(?:export\s+)?type\s+(\w+)\s*=\s*([^;]+);', code)

    # 2. コンポーネントごとの分割処理
    # (function App() や const App: React.FC = () => {} の両方に対応)
    comp_pattern = re.compile(r'(?:export\s+)?(?:default\s+)?(?:function\s+|const\s+)([A-Z]\w+)(?:\s*:\s*React\.[a-zA-Z<>]+)?\s*(?:=\s*(?:\([^)]*\))?\s*=>|\()')
    comp_matches = list(comp_pattern.finditer(code))
    
    toon_blocks = []
    
    for i, match in enumerate(comp_matches):
        comp_name = match.group(1)
        start_idx = match.start()
        end_idx = comp_matches[i+1].start() if i + 1 < len(comp_matches) else len(code)
        comp_code = code[start_idx:end_idx] # このコンポーネントの中身だけをスライス
        
        toon = [f"component:{comp_name}"]
        
        # Imports と Types は最初のブロックのみに出力
        if i == 0:
            if '"use client"' in code or "'use client'" in code: toon.append("  client:true")
            if import_dict:
                toon.append("  imports:")
                for path, items in import_dict.items():
                    unique_items = sorted(list(set([it for it in items if it])))
                    toon.append(f"    - {path}: [{','.join(unique_items)}]")
            if interfaces or types:
                toon.append("  types:")
                for name, body in interfaces:
                    clean_body = re.sub(r'\s+', ' ', body).strip()
                    toon.append(f"    - interface {name} {{{clean_body}}}")
                for name, body in types:
                    clean_body = re.sub(r'\s+', ' ', body).strip()
                    toon.append(f"    - type {name} = {clean_body}")

        # Hooks
        hooks = re.findall(r'const\s+[\{\[\s]*([\w\s,:]+)[\}\]\s]*\s*=\s*(\w+)\((.*?)\)', comp_code, re.DOTALL)
        if hooks:
            toon.append("  logic:")
            for vars, name, args in hooks:
                clean_vars = re.sub(r'\s+', '', vars)
                clean_args = re.sub(r'\s+', ' ', args).strip()
                toon.append(f"    {name}({clean_args}) -> [{clean_vars}]")
                
        # Render Tree
        tag_pattern = re.compile(r'<([a-zA-Z0-9_]+)([^>]*)>\s*([^<]*)(?:<)?')
        render_elements = []
        for tag_match in tag_pattern.finditer(comp_code):
            tag_name = tag_match.group(1)
            attrs = tag_match.group(2)
            content = tag_match.group(3).strip()
            props = []
            
            # classNameを "", '', {} ごとに正確に抽出
            class_match = re.search(r'className\s*=\s*(".*?"|\'.*?\'|\{.*?\})', attrs, re.DOTALL)
            if class_match:
                class_val = class_match.group(1) # {cn(...)} や "flex" がそのまま入る
                clean_class = re.sub(r'\s+', ' ', class_val).strip()
                props.append(f'className:{clean_class}')
                
            if content and not content.startswith('/'):
                clean_content = re.sub(r'\s+', ' ', content).strip()
                if clean_content:
                    clean_content = clean_content.replace('"', '\\"') # エスケープ
                    props.append(f'text:"{clean_content}"')
                    
            element_str = tag_name
            if props: element_str += f'({", ".join(props)})'
            render_elements.append(element_str)
            
        if render_elements:
            toon.append("  render_tree:")
            for el in render_elements: toon.append(f"    - {el}")
                
        toon_blocks.append("\n".join(toon))
        
    return "\n---\n".join(toon_blocks)

if __name__ == "__main__":
    if len(sys.argv) < 2: print("Usage: python ts2toon.py <file>")
    else: print(generate_toon(sys.argv[1]))
