const fs = require('fs');

const html = fs.readFileSync('index.html', 'utf8');
const match = html.match(/<script type="text\/babel">([\s\S]*?)<\/script>/);

if (!match) {
  console.error("❌ Babel script tag not found!");
  process.exit(1);
}

const code = match[1];
console.log("Found Babel script, length:", code.length);

// 1. Check for required components and features
const requiredStrings = [
  'CreateCurriculumScreen',
  'MyCurriculumsScreen',
  'StudySetupModal',
  'TrainingSetupModal',
  'RankingScreen',
  'CreateCustomBookScreen',
  'CustomBooksScreen',
  'TutorialScreen',
  'EbbinghausScreen',
  'TreeScreen',
  'WordListScreen',
  // Podium features
  'CHAMPION',
  '전체 랭킹 리스트 (4위~)',
  'fixed bottom-0',
  // Custom book features
  '+ 단어 행 추가',
  'custom_vocab_books',
  'custom_vocab_words',
  // Ebbinghaus features
  'Hermann Ebbinghaus',
  '2일 미복습 누적 경고 시스템'
];

let allFound = true;
for (const str of requiredStrings) {
  if (code.includes(str)) {
    console.log(`✅ [FOUND] ${str}`);
  } else {
    console.error(`❌ [MISSING] ${str}`);
    allFound = false;
  }
}

// 2. Check for syntax balance ignoring strings and comments
function checkBalanced(source) {
  let inStr = null;
  let inLineComment = false;
  let inBlockComment = false;
  let bOpen = 0, pOpen = 0, brOpen = 0;

  for (let i = 0; i < source.length; i++) {
    const c = source[i];
    const next = source[i + 1];

    if (inLineComment) {
      if (c === '\n') inLineComment = false;
      continue;
    }
    if (inBlockComment) {
      if (c === '*' && next === '/') {
        inBlockComment = false;
        i++;
      }
      continue;
    }
    if (inStr) {
      if (c === '\\') {
        i++; // skip escaped char
        continue;
      }
      if (c === inStr) {
        inStr = null;
      }
      continue;
    }

    if (c === '/' && next === '/') {
      inLineComment = true;
      i++;
      continue;
    }
    if (c === '/' && next === '*') {
      inBlockComment = true;
      i++;
      continue;
    }
    if (c === '"' || c === "'" || c === '`') {
      inStr = c;
      continue;
    }

    if (c === '{') bOpen++;
    else if (c === '}') bOpen--;
    else if (c === '(') pOpen++;
    else if (c === ')') pOpen--;
    else if (c === '[') brOpen++;
    else if (c === ']') brOpen--;

    if (bOpen < 0 || pOpen < 0 || brOpen < 0) {
      console.error(`⚠️ Negative balance at index ${i}: char='${c}', braces=${bOpen}, parens=${pOpen}, brackets=${brOpen}`);
    }
  }

  console.log(`Balance check: Braces=${bOpen}, Parens=${pOpen}, Brackets=${brOpen}`);
  return bOpen === 0 && pOpen === 0 && brOpen === 0;
}

const isClean = checkBalanced(code);
if (allFound && isClean) {
  console.log("\n🎉 ALL 4 CORE REQUIREMENTS & SYNTAX BALANCED 100%!");
} else {
  console.log("\n⚠️ Some checks failed. Inspect output above.");
}
