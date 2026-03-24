import re
import sys
import os

def generate_toon(file_path):
    """
    指定されたファイルを解析し、拡張子に応じたTOON形式（量子化データ）を生成する
    """
    if not os.path.exists(file_path):
        return f"Error: File {file_path} not found."

    ext = os.path.splitext(file_path)[1].lower()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
    except Exception as e:
        return f"Error reading file: {str(e)}"

    # --- 1. TypeScript / TSX ---
    if ext in ['.ts', '.tsx']:
        return parse_typescript(code)

    # --- 2. Prisma Schema ---
    elif ext == '.prisma':
        return parse_prisma(code)

    # --- 3. CSS / SASS / SCSS ---
    elif ext in ['.css', '.sass', '.scss']:
        return parse_styles(code, ext)

    # --- 4. SQL (SQLite / PostgreSQL etc.) ---
    elif ext in ['.sql']:
        return parse_sql(code)

    # --- 5. Redis / Key-Value Config ---
    elif 'redis' in file_path.lower() or ext in ['.conf']:
        return parse_redis(code)

    # --- 6. JSON (Config/Data) ---
    elif ext == '.json':
        return f"type:json\n  keys:[{','.join(re.findall(r'\"(\w+)\":', code)[:15])}]"

    return f"type:raw\n  file:{os.path.basename(file_path)}"

def parse_typescript(code):
    comp_match = re.search(r'export default function (\w+)', code)
    comp_name = comp_match.group(1) if comp_match else "Module"
    
    imports = re.findall(r'from ["\'](.+?)["\']', code)
    clean_imports = [imp.split('/')[-1] for imp in imports]

    props_block = re.search(r'type Props = \{(.*?)\};', code, re.DOTALL)
    props = re.findall(r'(\w+)\??:\s*([\w\[\]<>| ]+)', props_block.group(1)) if props_block else []

    hooks = re.findall(r'const\s+[\{\[]?\s*([\w\s,:]+)\s*[\}\]]?\s*=\s*(\w+)\((.*?)\)', code)
    components = sorted(list(set(re.findall(r'<([A-Z][\w\.]*)', code))))

    toon = [f"component:{comp_name}"]
    if '"use client"' in code or "'use client'" in code: toon.append("  client:true")
    if clean_imports: toon.append(f"  imports:[{','.join(dict.fromkeys(clean_imports))}]")
    if props:
        toon.append("  props:")
        for p_name, p_type in props: toon.append(f"    {p_name}:{p_type.strip().replace(' ', '')}")
    if hooks:
        toon.append("  logic:")
        for vars, name, args in hooks: toon.append(f"    {name}({args.strip()}) -> [{re.sub(r'\s+', '', vars)}]")
    if components:
        toon.append(f"  render_tree:[{','.join(components)}]")
    
    return "\n".join(toon)

def parse_prisma(code):
    models = re.findall(r'model\s+(\w+)\s+{(.*?)}', code, re.DOTALL)
    toon = ["type:prisma_schema"]
    for name, body in models:
        fields = re.findall(r'^\s+(\w+)\s+([\w\[\]\?]+)', body, re.MULTILINE)
        field_str = ",".join([f"{f[0]}:{f[1]}" for f in fields])
        toon.append(f"  model:{name}[{field_str}]")
    return "\n".join(toon)

def parse_styles(code, ext):
    selectors = re.findall(r'([\.#][\w-]+)\s*{', code)
    vars = re.findall(r'(\$[\w-]+|--[\w-]+):\s*(.*?);', code)
    toon = [f"type:style({ext[1:]})"]
    if vars: toon.append(f"  vars:[{','.join([v[0] for v in vars[:15]])}]")
    if selectors: toon.append(f"  selectors:[{','.join(set(selectors[:20]))}]")
    return "\n".join(toon)

def parse_sql(code):
    tables = re.findall(r'CREATE TABLE\s+(\w+)\s+\((.*?)\);', code, re.DOTALL | re.IGNORECASE)
    toon = ["type:sql_schema"]
    for name, body in tables:
        cols = re.findall(r'^\s*(\w+)\s+(\w+)', body, re.MULTILINE)
        col_str = ",".join([f"{c[0]}:{c[1]}" for c in cols])
        toon.append(f"  table:{name}[{col_str}]")
    return "\n".join(toon)

def parse_redis(code):
    prefixes = re.findall(r'["\']?([\w-]+:[\w-]+)["\']?', code)
    toon = ["type:redis_config"]
    if prefixes: toon.append(f"  key_patterns:[{','.join(set(prefixes[:10]))}]")
    return "\n".join(toon)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ts2toon.py <file>")
    else:
        print(generate_toon(sys.argv[1]))
