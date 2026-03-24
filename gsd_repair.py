import subprocess
import sys
import os
import hashlib
from ts2toon import parse_error

# 設定
MAX_RETRIES = 3
temp_backup_file = ".gsd_backup.tmp"

def run_command(command):
    """シェルコマンドを実行し、(終了コード, 標準出力, 標準エラー)を返す"""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr

def backup_file(file_path):
    """ファイルを一時バックアップする"""
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as src, open(temp_backup_file, 'w', encoding='utf-8') as dst:
            dst.write(src.read())

def rollback_file(file_path):
    """バックアップからファイルを復元する"""
    if os.path.exists(temp_backup_file):
        with open(temp_backup_file, 'r', encoding='utf-8') as src, open(file_path, 'w', encoding='utf-8') as dst:
            dst.write(src.read())
        print(f"⏪ Rollback: {file_path} has been restored to its original state.")

def get_file_hash(file_path):
    """ファイルのハッシュ値を計算して、内容の変化（ループ）を検知する"""
    with open(file_path, 'rb') as f:
        return hashlib.md5(f.read()).hexdsize()

def gsd_repair_cycle(target_file):
    print(f"--- 🛠 GSD Self-Healing Loop: {target_file} ---")
    
    # 初期のバックアップ作成
    backup_file(target_file)
    
    history = []
    retry_count = 0
    
    while retry_count < MAX_RETRIES:
        retry_count += 1
        print(f"\n[Cycle {retry_count}/{MAX_RETRIES}] Verifying code...")

        # 1. 検証 (npx tsc 等)
        # プロジェクトに合わせてコマンドを変更してください（例: npm run build）
        code, stdout, stderr = run_command("npx tsc --noEmit")
        
        if code == 0:
            print("✅ GSD Success: No errors detected!")
            if os.path.exists(temp_backup_file): os.remove(temp_backup_file)
            return

        # 2. エラーの量子化 (TOON化)
        print("❌ Error detected. Quantizing logs...")
        error_log = stderr if stderr else stdout
        diagnosis = parse_error(error_log)
        
        # 3. ループ検知
        current_hash = hashlib.md5(diagnosis.encode()).hexdigest()
        if current_hash in history:
            print("🛑 Loop Detected: AI is producing the same error. Stopping.")
            break
        history.append(current_hash)

        # 4. AIへの指示（手動またはAPI連携の準備）
        print("\n--- 📋 COPY TO AI ---")
        print(diagnosis)
        print(f"at_file: {target_file}")
        print("instruction: Please provide a TOON patch to fix this based on CoD (Draft).")
        print("---------------------\n")

        # 5. 次のパッチ待機（手動運用の場合はここで一時停止）
        # ※全自動化する場合はここで Gemini API 等を叩く
        input(f"Apply the AI's new TOON patch to {target_file}, then press Enter to re-verify...")

    # 失敗した場合の処理
    print("\n❌ GSD Failed to resolve errors within retry limit.")
    rollback_file(target_file)
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gsd_repair.py <target_file.tsx>")
    else:
        gsd_repair_cycle(sys.argv[1])
