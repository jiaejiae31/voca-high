const fs = require('fs');
const content = fs.readFileSync('index.html', 'utf8');
const scriptMatch = content.match(/<script type="text\/babel">([\s\S]*?)<\/script>/);

if (!scriptMatch) {
  console.log("No babel script found");
  process.exit(1);
}

const code = scriptMatch[1];
const lines = code.split('\n');

let balance = 0;
lines.forEach((line, idx) => {
  // 문자열 리터럴을 단순화해서 괄호 계산
  const sanitized = line.replace(/(["'`])(?:(?=(\\?))\2.)*?\1/g, '""');
  for (let c of sanitized) {
    if (c === '(') balance++;
    if (c === ')') balance--;
  }
  if (balance < 0) {
    console.log(`Line ${idx + 1}: ${line.trim()} (balance: ${balance})`);
    balance = 0;
  }
});
console.log("Final balance after sanitized scan:", balance);
