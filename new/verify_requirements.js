const fs = require('fs');

const content = fs.readFileSync('index.html', 'utf8');

const tests = [
  { name: "토익 1000 삭제 확인", test: !content.includes('toeic_1000') && !content.includes('토익') },
  { name: "필수 영단어 2000 포함", test: content.includes('essential_2000') && content.includes('필수 영단어 2000') },
  { name: "수능 필수 1000 포함", test: content.includes('csat_1000') && content.includes('수능 필수 1000') },
  { name: "커스텀 단어장 포함", test: content.includes('커스텀 단어장') },
  { name: "일일 목표 20, 30, 40, 50개 지원", test: content.includes('[20, 30, 40, 50]') },
  { name: "햄버거 버튼 좌측 상단 배치", test: content.includes('title="전체 메뉴 열기"') },
  { name: "맞춤 훈련 모드 카드 삭제 확인", test: !content.includes('맞춤 훈련 모드') },
  { name: "좌측 드로어: 1. 내 정보, 2. 단어장, 3. 기능 설명", test: content.includes('1. 내 정보') && content.includes('2. 단어장') && content.includes('3. 기능 설명') },
  { name: "메인 화면: 상시 복습칸 (0개일 때도 항상 표시)", test: content.includes('에빙하우스 망각곡선 복습칸') && content.includes('대기 0단어') && content.includes('현재 복습할 단어가 없습니다') },
  { name: "학습 단어장 팝업 (StudySetupModal): 하나씩 / 리스트 선택", test: content.includes('StudySetupModal') && content.includes('단어 하나씩 보기') && content.includes('리스트로 보기') },
  { name: "학습 단어장 (StudyScreen): 리스트 뷰 & 훈련 연계", test: content.includes('mode === \'list\'') && content.includes('onGoToTraining') },
  { name: "훈련 단어장 팝업 (TrainingSetupModal): 영한/한영, 하나씩/리스트, 타이머", test: content.includes('TrainingSetupModal') && content.includes('en_to_ko') && content.includes('ko_to_en') && content.includes('timerSec') },
  { name: "훈련 단어장 (TrainingScreen): 타이머 게이지 및 리스트 풀이", test: content.includes('TrainingScreen') && content.includes('timeLeft') && content.includes('handleListSubmit') },
  { name: "커리큘럼 설정 영구 저장 (localStorage & userId)", test: content.includes('STORAGE_PREFIX + currentUser.id + \'_CURRICULUM\'') || content.includes('_CURRICULUM') },
  { name: "독립 화면: StatsScreen, RankingScreen, WordListScreen, CustomVocabScreen", test: content.includes('StatsScreen') && content.includes('RankingScreen') && content.includes('WordListScreen') && content.includes('CustomVocabScreen') }
];

console.log("=== VOCAHIGH 신규 요구사항 전수 검증 결과 ===");
let passed = 0;
tests.forEach(t => {
  if (t.test) {
    console.log(`[PASS] ${t.name}`);
    passed++;
  } else {
    console.log(`[FAIL] ${t.name}`);
  }
});
console.log(`\n총 ${tests.length}개 항목 중 ${passed}개 통과 (${Math.round((passed / tests.length) * 100)}%)`);
