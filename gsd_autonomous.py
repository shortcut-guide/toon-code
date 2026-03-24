import os
import sys
import subprocess
import google.generativeai as genai
from datetime import datetime
from ts2toon import parse_error, generate_toon
from toon2code import merge_toon_to_code_v2

# --- Configuration ---
# 環境変数 GOOGLE_API_KEY を設定してください
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro')

MAX_AUTONOMOUS_RETRIES = 5
VERIFY_COMMAND = "npx tsc --noEmit" # プロジェクトに応じて変更 (npm test 等)
TEMP_BACKUP = ".gsd_backup.tmp"

# --- Utility Functions ---

def run_command(command):
    """実行結果を (code, stdout, stderr) で返す"""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def backup_file(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(TEMP_BACKUP, 'w', encoding='utf-8') as f:
            f.write(content)

def rollback_file(file_path):
    if os.path.exists(TEMP_BACKUP):
        with open(TEMP_BACKUP, 'r', encoding='utf-8') as src, open(file_path, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
        print(f"⏪ Rollback: {file_path} restored.")

def ask_gemini_for_patch(diagnosis, current_code_toon):
    """Gemini APIを使用して修正TOONパッチを生成する"""
    prompt = f"""
# Role: Senior AI Engineer
# Task: Fix the code error using CoD (Chain of Draft) and TOON patch.

# Context (Current TOON Structure):
{current_code_toon}

# Diagnosis (Current Error):
{diagnosis}

# Instructions:
1. Use CoD (Chain of Draft) to analyze the root cause in 1-2 lines.
2. Provide a TOON patch (imports, logic, render_update) to fix the issue.
3. Output ONLY the CoD and the TOON patch. Do not include markdown code blocks.
"""
    response = model.generate_content(prompt)
    return response.text

def create_github_pr(file_path, initial_diagnosis):
    """GitHub CLI (gh) を使用してPRを作成する"""
    print("📦 GSD: Starting Pull Request process...")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    branch_name = f"gsd-fix-{timestamp}"
    
    # Git操作
    run_command(f"git checkout -b {branch_name}")
    run_command(f"git add {file_path}")
    commit_msg = f"fix: AI auto-repair for {os.path.basename(file_path)}"
    run_command(f'git commit -m "{commit_msg}"')
    run_command(f"git push origin {branch_name}")
    
    # PR作成
    title = f"AI Auto-Fix: {os.path.basename(file_path)}"
    body = f"GSD Autonomous mode fixed the error.\n\n### Initial Diagnosis\n{initial_diagnosis}"
    run_command(f'gh pr create --title "{title}" --body "{body}"')
    print(f"✅ GSD: PR created on branch {branch_name}")

# --- Main GSD Autonomous Loop ---

def start_gsd_autonomous(target_file):
    print(f"🤖 GSD Autonomous Mode: Processing {target_file}...")
    backup_file(target_file)
    
    initial_diagnosis = ""
    retry_count = 0
    
    while retry_count < MAX_AUTONOMOUS_RETRIES:
        retry_count += 1
        print(f"\n[Cycle {retry_count}/{MAX_AUTONOMOUS_RETRIES}] Verifying...")
        
        # 1. 構文/型チェック
        code, out, err = run_command(VERIFY_COMMAND)
        if code == 0:
            print("✨ GSD MISSION ACCOMPLISHED: Code is verified.")
            if initial_diagnosis: # 修正が行われた場合のみPR作成
                create_github_pr(target_file, initial_diagnosis)
            return

        # 2. エラーの量子化
        error_log = err if err else out
        diagnosis = parse_error(error_log)
        if not initial_diagnosis: initial_diagnosis = diagnosis
        
        # 3. 現状のコード構造を量子化
        current_toon = generate_toon(target_file)
        
        # 4. AIに修正を依頼
        print("🧠 AI is drafting a fix...")
        ai_patch = ask_gemini_for_patch(diagnosis, current_toon)
        
        # 5. パッチの適用
        with open("patch.toon", "w", encoding="utf-8") as f:
            f.write(ai_patch)
        
        print("🔧 Applying patch...")
        merge_toon_to_code_v2("patch.toon", target_file)

    print("🛑 Limit reached. GSD could not resolve the error autonomously.")
    rollback_file(target_file)
    sys.exit(1)

if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Error: Set GOOGLE_API_KEY environment variable.")
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print("Usage: python gsd_autonomous.py <file_path>")
    else:
        start_gsd_autonomous(sys.argv[1])
