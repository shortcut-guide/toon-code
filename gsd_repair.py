import subprocess
import sys
from ts2toon import parse_error

def run_verify():
    """ビルド/型チェックを実行し、エラーがあれば量子化して返す"""
    # Next.js / TS プロジェクトを想定
    result = subprocess.run("npx tsc --noEmit", shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        return None # 成功
    
    # エラーをTOON化
    error_log = result.stderr if result.stderr else result.stdout
    return parse_error(error_log)

def main():
    print("🚀 GSD Self-Healing: Verifying current build...")
    diagnosis = run_verify()
    
    if not diagnosis:
        print("✅ No errors found. System is healthy.")
        return

    print("❌ Error detected. Generating TOON Diagnosis...")
    print("\n--- [COPY THIS TO AI FOR AUTO-REPAIR] ---")
    print(diagnosis)
    print("------------------------------------------")
    print("\nAI Prompt Suggestion:")
    print("「上記診断に基づき、CoD (Draft) を経て、修正用の TOON パッチを作成してください。」")

if __name__ == "__main__":
    main()
