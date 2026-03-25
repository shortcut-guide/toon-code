import os
import sys
# スクリプトがあるディレクトリを検索パスの先頭に追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ts2toon import generate_toon # 既存のロジックを再利用

def project_to_toon(root_dir):
    # 除外するディレクトリ（フォルダのみ）
    exclude_dirs = {
        '.git', 'node_modules', '.next', 'dist', 'build',
        '.cache', '.history', '.vscode', '.codex', '.claude',
        '.gemini', '.openai', '.opencode', '.husky', '.specify'
    }
    
    # 除外するファイル（元々 exclude_dirs に混ざっていたもの）
    exclude_files = {
        'package-lock.json', 'tsconfig.json', 'n8nac-config.json',
        '.gitignore', '.lock', 'typedoc.json', '.gitmodules', '.envrc'
    }
    
    # 対象とする拡張子
    include_exts = {'.ts', '.tsx', '.prisma', '.sql', '.css', '.scss', '.sass', '.json'}

    full_project_toon = ["project_root: " + os.path.abspath(root_dir)]
    full_project_toon.append("---")

    for root, dirs, files in os.walk(root_dir):
        # 不要なディレクトリをスキップ
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            # 除外ファイルリストに完全一致するものはスキップ
            if file in exclude_files:
                continue
                
            # 対象の拡張子かどうか判定
            if any(file.endswith(ext) for ext in include_exts):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, root_dir)
                
                full_project_toon.append(f"file: {rel_path}")
                # ts2toon.py のロジックを呼び出し
                file_toon = generate_toon(file_path)
                indented_toon = "\n".join(["  " + line for line in file_toon.split("\n")])
                full_project_toon.append(indented_toon)
                full_project_toon.append("---")

    return "\n".join(full_project_toon)

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "."
    print(project_to_toon(target))
