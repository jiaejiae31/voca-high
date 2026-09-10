const fs = require('fs');
const html = fs.readFileSync('index.html', 'utf-8');
const scriptMatch = html.match(/<script type="text\/babel">([\s\S]*?)<\/script>/);

if (!scriptMatch) {
  console.log('No script match found');
  process.exit(1);
}

const code = scriptMatch[1];
console.log('Code length:', code.length);

// 괄호 짝 검사
let braces = 0;
let parens = 0;
let brackets = 0;
for (let i = 0; i < code.length; i++) {
  const c = code[i];
  if (c === '{') braces++;
  if (c === '}') braces--;
  if (c === '(') parens++;
  if (c === ')') parens--;
  if (c === '[') brackets++;
  if (c === ']') brackets--;
}
console.log(`Braces: ${braces}, Parens: ${parens}, Brackets: ${brackets}`);
