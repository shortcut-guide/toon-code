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
        # もしくは、もっとシンプルに一度変数に出してから f-string に入れる（これが一番安全）
        keys_str = ','.join(re.findall(r'"(\w+)":', code)[:15])
        return f"type:json\n  keys:[{keys_str}]"

    return f"type:raw\n  file:{os.path.basename(file_path)}"

def parse_typescript(code):
    # コンポーネント名の抽出を強化（export function も対象に）
    comp_match = re.search(r'export (?:default )?(?:function|const) (\w+)', code)
    comp_name = comp_match.group(1) if comp_match else "Module"
    
    # --- 【改修1】Imports: パスと変数の関係を正確に保持 ---
    import_dict = {}
    
    # 名前付きインポート (import { A, B } from "path")
    named_imports = re.findall(r'import\s+\{([^}]+)\}\s+from\s+["\']([^"\']+)["\']', code)
    for items, path in named_imports:
        clean_items = [i.strip() for i in items.split(',')]
        if path not in import_dict:
            import_dict[path] = []
        import_dict[path].extend(clean_items)
        
    # デフォルトインポート (import A from "path")
    default_imports = re.findall(r'import\s+(\w+)\s+from\s+["\']([^"\']+)["\']', code)
    for item, path in default_imports:
        if path not in import_dict:
            import_dict[path] = []
        import_dict[path].append(item)

    # Hooks: 戻り値が {} や [] のケース、および複数行に対応
    hooks = re.findall(r'const\s+[\{\[\s]*([\w\s,:]+)[\}\]\s]*\s*=\s*(\w+)\((.*?)\)', code, re.DOTALL)

    toon = [f"component:{comp_name}"]
    if '"use client"' in code or "'use client'" in code: toon.append("  client:true")
    
    # 抽出したインポート情報をTOONにリスト形式で追加
    if import_dict:
        toon.append("  imports:")
        for path, items in import_dict.items():
            # 重複を排除し、空文字を消す
            unique_items = sorted(list(set([i for i in items if i])))
            toon.append(f"    - {path}: [{','.join(unique_items)}]")
    
    # logic セクションの構造化
    if hooks:
        toon.append("  logic:")
        for vars, name, args in hooks:
            # 改行や余計な空白を削除して圧縮
            clean_vars = re.sub(r'\s+', '', vars)
            clean_args = re.sub(r'\s+', ' ', args).strip()
            toon.append(f"    {name}({clean_args}) -> [{clean_vars}]")
            
    # --- Render Tree: classNameの保持 ---
    tags = re.findall(r'<([a-zA-Z0-9_]+)([^>]*)>', code)
    render_elements = []
    
    for tag_name, attrs in tags:
        # className の抽出（"", '', {} のパターンに対応）
        class_match = re.search(r'className\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|\{([^}]*)\})', attrs)
        
        if class_match:
            # マッチしたグループのうち、Noneでないものを取得
            class_value = class_match.group(1) or class_match.group(2) or class_match.group(3)
            if class_value:
                # テンプレートリテラル内の改行などを潰して1行にする
                clean_class = re.sub(r'\s+', ' ', class_value).strip()
                render_elements.append(f'{tag_name}(className:"{clean_class}")')
        else:
            # classNameがない場合は「大文字始まりのコンポーネント」だけを残す
            if tag_name[0].isupper():
                render_elements.append(tag_name)

    # 重複を排除（元の順序を維持）
    unique_elements = []
    for el in render_elements:
        if el not in unique_elements:
            unique_elements.append(el)

    # 出力フォーマットを見やすい箇条書きリストに変更
    if unique_elements:
        toon.append("  render_tree:")
        for el in unique_elements:
            toon.append(f"    - {el}")
    
    return "\n".join(toon)

def parse_prisma(code):
    # モデルのブロックを抽出
    models = re.findall(r'model\s+(\w+)\s+{(.*?)}', code, re.DOTALL)
    toon = ["type:prisma_schema"]
    
    for name, body in models:
        # 各フィールドを解析 (フィールド名, 型, 属性)
        # 属性(Attributes)も抽出することでリレーションを把握可能にする
        fields = re.findall(r'^\s+(\w+)\s+([\w\[\]\?]+)(.*)', body, re.MULTILINE)
        
        field_details = []
        for f_name, f_type, f_attr in fields:
            f_attr = f_attr.strip()
            # リレーション (@relation) や ID, Unique などの重要なメタデータのみ抽出
            meta = ""
            if "@id" in f_attr: meta = "(pk)"
            elif "@unique" in f_attr: meta = "(uq)"
            elif "@relation" in f_attr:
                # 参照先フィールドなどを抽出
                rel_match = re.search(r'fields:\s*\[(.*?)\],\s*references:\s*\[(.*?)\]', f_attr)
                if rel_match:
                    meta = f"->{rel_match.group(2)}" # 参照先のみ簡潔に表示
                else:
                    meta = "(rel)" # 逆参照など
            
            field_details.append(f"{f_name}:{f_type}{meta}")
            
        toon.append(f"  model:{name}[{','.join(field_details)}]")
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

def parse_error(error_text):
    """
    複雑なエラーログを、ファイル名、行数、エラー内容に量子化する
    """
    # TypeScriptのエラー形式 (file.ts(line,col): error TSXXXX: message) を抽出
    error_pattern = r'([\w\/\.-]+)\((\d+),\d+\):\s+error\s+(TS\d+):\s+(.*)'
    matches = re.findall(error_pattern, error_text)
    
    if not matches:
        return f"type:error_raw\n  msg:{error_text[:200]}"

    toon = ["type:diagnosis"]
    for file, line, code, msg in matches[:5]: # 上位5つに制限
        toon.append(f"  at:{file}:{line}")
        toon.append(f"  code:{code}")
        toon.append(f"  cause:{msg.strip()}")
    return "\n".join(toon)
