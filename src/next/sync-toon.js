// sync-toon.js
const fs = require('fs');
const { exec } = require('child_process');

const toonPath = './project.toon';

if (fs.existsSync(toonPath)) {
  const content = fs.readFileSync(toonPath, 'utf8');
  
  // OSごとのクリップボードコピーコマンド
  const proc = exec(process.platform === 'win32' ? 'clip' : 'pbcopy');
  proc.stdin.write(content);
  proc.stdin.end();

  console.log('✅ project.toon has been generated and copied to clipboard!');
  console.log('👉 Paste it into Cloud Code Gemini with: "Update your context with this TOON data"');
} else {
  console.error('❌ project.toon not found. Run npm run build:toon first.');
}
