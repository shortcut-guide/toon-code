import re
import sys
import os
try:
    from tree_sitter import Parser, Language
    import tree_sitter_typescript as ts_typescript
except ImportError:
    print("Error: 必要なライブラリがインストールされていません。")
    print("実行してください: pip install tree-sitter tree-sitter-typescript")
    sys.exit(1)

# TSX用のASTパーサーを初期化
TSX_LANGUAGE = Language(ts_typescript.language_tsx())
parser = Parser(TSX_LANGUAGE)

def parse_toon_render_tree(block):
    """TOONの render_tree セクションを解析し、辞書のリストに変換する"""
    render_tree_match = re.search(r'render_tree:\n((?:\s+-\s+.*\n?)*)', block)
    if not render_tree_match: return []
    
    elements = []
    for line in render_tree_match.group(1).strip().split('\n'):
        element_def = line.strip()[2:] # "- " を削除
        tag_match = re.match(r'([a-zA-Z0-9_]+)(?:\((.*)\))?', element_def)
        if tag_match:
            tag_name = tag_match.group(1)
            attrs_str = tag_match.group(2) or ""
            
            # classNameの抽出
            class_val = ""
            class_match = re.search(r'className:(".*?"|\'.*?\'|\{.*?\})', attrs_str)
            if class_match: class_val = class_match.group(1)
            
            # textの抽出
            text_val = ""
            text_match = re.search(r'text:"(.*?)"', attrs_str)
            if text_match: text_val = text_match.group(1)
                
            elements.append({'tag': tag_name, 'className': class_val, 'text': text_val})
    return elements

def get_ast_jsx_elements(node, elements_list):
    """ASTを深さ優先探索し、すべてのJSX要素を順番に取得する"""
    if node.type in ['jsx_element', 'jsx_self_closing_element']:
        # タグ名を取得
        open_tag = node.child_by_field_name('open_tag') if node.type == 'jsx_element' else node
        name_node = open_tag.child_by_field_name('name') if open_tag else None
        if name_node:
            tag_name = name_node.text.decode('utf8')
            elements_list.append({
                'tag': tag_name,
                'node': node,
                'open_tag': open_tag
            })
    
    for child in node.children:
        get_ast_jsx_elements(child, elements_list)

def merge_toon_to_code_ast(toon_path, target_code_path):
    if not os.path.exists(toon_path): return f"Error: TOON file not found"
    with open(toon_path, 'r', encoding='utf-8') as f: toon_content = f.read()
    if os.path.exists(target_code_path):
        with open(target_code_path, 'r', encoding='utf-8') as f: code = f.read()
    else: code = ""

    blocks = toon_content.split('\n---\n')
    
    # Imports と Types の処理（正規表現で十分なためそのまま維持）
    for block in blocks:
        if "client:true" in block and '"use client"' not in code: code = '"use client";\n\n' + code
        import_match = re.search(r'imports:\n((?:\s+-\s+.*\n?)*)', block)
        if import_match:
            for line in import_match.group(1).strip().split('\n'):
                m = re.match(r'-\s+(.+?):\s+\[(.*?)\]', line.strip())
                if m and f'from "{m.group(1)}"' not in code and f"from '{m.group(1)}'" not in code:
                    code = f'import {{ {m.group(2)} }} from "{m.group(1)}";\n' + code

    # --- 【神髄】ASTによる JSX の差分パッチング ---
    # バイト位置がずれないように、変更操作（Edits）をリスト化して後で後ろから適用する
    edits = [] 
    
    # 現在のソースコードをASTとしてパース
    source_bytes = bytes(code, "utf8")
    tree = parser.parse(source_bytes)
    
    # ASTから全JSX要素をフラットなリストとして抽出
    ast_elements = []
    get_ast_jsx_elements(tree.root_node, ast_elements)
    
    # TOON側の render_tree をすべてフラットなリストとして抽出（全コンポーネント結合）
    toon_elements = []
    for block in blocks:
        toon_elements.extend(parse_toon_render_tree(block))
        
    if not toon_elements or not ast_elements:
        # 新規作成時はスキップ（今回は既存コードのアップデートに特化）
        pass
    else:
        # 貪欲マッチング（Greedy Matching）による差分適用アルゴリズム
        ast_idx = 0
        for toon_node in toon_elements:
            # AST側の要素とTOON側の要素のタグ名が一致するか？
            if ast_idx < len(ast_elements) and ast_elements[ast_idx]['tag'] == toon_node['tag']:
                # 【既存要素の更新】
                ast_item = ast_elements[ast_idx]
                open_tag_node = ast_item['open_tag']
                
                # className 属性を探す
                class_attr_node = None
                for child in open_tag_node.children:
                    if child.type == 'jsx_attribute':
                        attr_name = child.child_by_field_name('name')
                        if attr_name and attr_name.text.decode('utf8') == 'className':
                            class_attr_node = child
                            break
                
                new_class = toon_node.get('className')
                if new_class:
                    if class_attr_node:
                        # 既存の className を上書き
                        edits.append((class_attr_node.start_byte, class_attr_node.end_byte, f'className={new_class}'))
                    else:
                        # className が無い場合は、タグ名 (e.g. <div) の直後に挿入
                        name_node = open_tag_node.child_by_field_name('name')
                        insert_pos = name_node.end_byte
                        edits.append((insert_pos, insert_pos, f' className={new_class}'))
                
                ast_idx += 1 # ASTのポインターを進める
            else:
                # 【新規要素の挿入 (Injection)】
                # TOONにはあるが、ASTには無い -> AIが新しく追加したタグ！
                if ast_idx > 0:
                    # 1つ前のAST要素の後ろに挿入する
                    prev_ast_item = ast_elements[ast_idx - 1]
                    insert_pos = prev_ast_item['node'].end_byte
                    
                    # 挿入するJSX文字列の生成
                    new_class_str = f' className={toon_node["className"]}' if toon_node.get("className") else ""
                    new_text_str = toon_node.get("text", "")
                    
                    if new_text_str:
                        new_jsx = f'\n<{toon_node["tag"]}{new_class_str}>{new_text_str}</{toon_node["tag"]}>'
                    else:
                        new_jsx = f'\n<{toon_node["tag"]}{new_class_str} />'
                        
                    edits.append((insert_pos, insert_pos, new_jsx))

    # --- 編集の適用 (後ろから適用することでバイト位置のズレを防ぐ) ---
    edits.sort(key=lambda x: x[0], reverse=True)
    
    for start_byte, end_byte, new_text in edits:
        source_bytes = source_bytes[:start_byte] + bytes(new_text, "utf8") + source_bytes[end_byte:]
        
    # 最終結果を保存
    final_code = source_bytes.decode("utf8")
    with open(target_code_path, 'w', encoding='utf-8') as f:
        f.write(final_code)
        
    return f"Successfully AST-merged TOON into {target_code_path}"

if __name__ == "__main__":
    if len(sys.argv) < 3: print("Usage: python toon2code.py <input.toon> <target.ts>")
    else: print(merge_toon_to_code_ast(sys.argv[1], sys.argv[2]))
