import subprocess
import sys
import os
from toon2code import merge_toon_to_code_v2

def run_command(command):
    """コマンドを実行し、結果を返す"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)

def gsd_cycle(toon_patch_path, target_file_path):
    print(f"--- 🚀 GSD Mode: Starting Execution ---")

    # 1. Apply TOON Patch (Quantized Design -> Code)
    print(f"Step 1: Applying TOON patch to {target_file_path}...")
    merge_result = merge_toon_to_code_v2(toon_patch_path, target_file_path)
    print(f"  {merge_result}")

    # 2. Verify (Type Check / Lint)
    print(f"Step 2: Verifying code integrity (tsc)...")
    # プロジェクト全体の型チェックを行う例
    code, out, err = run_command("npx tsc --noEmit")

    if code == 0:
        print("✅ GSD Success: Code is clean and functional.")
    else:
        print("❌ GSD Warning: Type errors detected.")
        # 3. Self-Healing (Error -> TOON for AI)
        error_summary = err if err else out
        print(f"--- 🩹 Self-Healing Context (Copy this to AI) ---")
        print(f"type:error_log\n  file:{target_file_path}\n  message:{error_summary[:200]}...")
        print(f"-----------------------------------------------")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python gsd.py <patch.toon> <target.tsx>")
    else:
        gsd_cycle(sys.argv[1], sys.argv[2])
