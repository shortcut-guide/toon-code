import os
import sys
import google.generativeai as genai
from gsd_repair import run_command, backup_file, rollback_file, get_file_hash
from ts2toon import parse_error, generate_toon
from toon2code import merge_toon_to_code_v2

# API設定
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro')

MAX_AUTONOMOUS_RETRIES = 5

def ask_gemini_for_patch(diagnosis, current_code_toon):
    prompt = f"""
    # Role: Senior AI Engineer
    # Context (TOON Format):
    {current_code_toon}

    # Diagnosis (Error):
    {diagnosis}

    # Task:
    Based on the diagnosis above, use CoD (Chain of Draft) to identify the root cause.
    Then, provide a TOON patch to fix the error.
    Output ONLY the CoD (Draft) and the TOON patch (imports, logic, render_update).
    """
    response = model.generate_content(prompt)
    return response.text

def gsd_autonomous_loop(target_file):
    print(f"🤖 GSD Autonomous Mode: Active for {target_file}")
    backup_file(target_file)
    
    retry_count = 0
    while retry_count < MAX_AUTONOMOUS_RETRIES:
        retry_count += 1
        print(f"\n[Cycle {retry_count}] Verifying...")
        
        # 1. 検証
        code, stdout, stderr = run_command("npx tsc --noEmit")
        if code == 0:
            print("✨ GSD MISSION ACCOMPLISHED: Code is fixed and verified.")
            return

        # 2. 診断の量子化
        error_log = stderr if stderr else stdout
        diagnosis = parse_error(error_log)
        current_toon = generate_toon(target_file)
        
        print("🧠 AI is thinking and drafting a fix...")
        # 3. Gemini API に修復を依頼
        ai_response = ask_gemini_for_patch(diagnosis, current_toon)
        
        # 4. 回答からTOONパッチを抽出して保存
        with open("patch.toon", "w", encoding="utf-8") as f:
            f.write(ai_response)
        
        # 5. パッチを自動適用
        print("🔧 Applying AI-generated patch...")
        merge_toon_to_code_v2("patch.toon", target_file)
        
    print("🛑 Autonomous Repair Limit Reached.")
    rollback_file(target_file)

if __name__ == "__main__":
    if not os.environ.get("GOOGLE_API_KEY"):
        print("Error: GOOGLE_API_KEY environment variable is not set.")
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print("Usage: python gsd_autonomous.py <target_file.tsx>")
    else:
        gsd_autonomous_loop(sys.argv[1])
