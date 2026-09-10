/**
 * ==============================================================================
 * 보카하이 (vocahigh) - 단어 데이터셋, 커리큘럼 & 보카트리 매니저 (data.js)
 * ==============================================================================
 * 
 * [역할 및 주요 기능]
 * 1. 3대 추천 단어장(중학 필수, 고교 수능 빈출, 토익/토플 실전) 메타 및 데이터셋 제공
 * 2. 에빙하우스 망각곡선 3대 주기(1일, 7일, 30일) 기반 복습 스케줄링
 * 3. 2일(48시간) 이상 미복습 시 누적(Overdue) 감지
 * 4. 복습 비율(100%, 70%, 50%, 30%) 무작위 샘플링
 * 5. 보카 트리(Voca Tree) 7단계 성장 테이블 및 햇살(☀️) 계산 로직
 * 6. 브라우저 로컬스토리지 영속성 및 Web Speech API TTS 지원
 */

// 로컬스토리지 키 설정
export const STORAGE_KEYS = {
  WORDS: 'VOCAHIGH_WORDS_V3',
  CURRICULUM: 'VOCAHIGH_CURRICULUM_V3',
  USER_STATS: 'VOCAHIGH_USER_STATS_V3',
  TREE: 'VOCAHIGH_TREE_V3',
  THEME: 'VOCAHIGH_THEME_V3'
};

// 에빙하우스 망각곡선 3대 주기 (일 단위: 1차=1일, 2차=7일, 3차=30일)
export const REVIEW_INTERVALS = [1, 7, 30];

// 2일(48시간) 미복습 시 누적 경고 기준 밀리초
export const OVERDUE_THRESHOLD_MS = 2 * 24 * 60 * 60 * 1000;

/**
 * 📚 3대 추천 단어장 메타 정보
 */
export const BOOKS_DATA = [
  {
    id: "middle_800",
    title: "중학 필수 영단어 800",
    subtitle: "기초를 탄탄하게 세우는 중등 교과 필수 어휘",
    totalWords: 800,
    difficulty: "기초 / 초급",
    badgeColor: "#5F8D4E",
    icon: "🌱",
    recommendedDaily: 20
  },
  {
    id: "high_1200",
    title: "고교 수능 빈출 마스터 1200",
    subtitle: "역대 모의고사 및 수능 1등급 핵심 빈출 어휘",
    totalWords: 1200,
    difficulty: "중급 / 상급",
    badgeColor: "#2D5A27",
    icon: "🌿",
    recommendedDaily: 30
  },
  {
    id: "toeic_1000",
    title: "토익/토플 실전 보카 1000",
    subtitle: "실전 비즈니스 및 아카데믹 고득점 전략 어휘",
    totalWords: 1000,
    difficulty: "실전 / 고급",
    badgeColor: "#A1C954",
    icon: "🌟",
    recommendedDaily: 30
  }
];

/**
 * 🌳 보카 트리(Voca Tree) 7단계 성장 테이블
 * - 단어 하나당 무조건 햇살 1개 (☀️ +1)
 */
export const TREE_STAGES = [
  { level: 1, name: "씨앗", emoji: "🌱", minSunlight: 0, maxSunlight: 99, desc: "땅속에 콕 박힌 단단하고 귀여운 황금 씨앗" },
  { level: 2, name: "새싹", emoji: "🌿", minSunlight: 100, maxSunlight: 299, desc: "파릇파릇 두 잎이 돋아난 아기 새싹" },
  { level: 3, name: "어린 줄기", emoji: "🎋", minSunlight: 300, maxSunlight: 499, desc: "곧게 뻗어가는 싱그러운 줄기" },
  { level: 4, name: "푸른 묘목", emoji: "🪴", minSunlight: 500, maxSunlight: 999, desc: "잔가지와 풍성한 잎을 갖춘 묘목" },
  { level: 5, name: "보카 나무", emoji: "🌳", minSunlight: 1000, maxSunlight: 1999, desc: "넓은 그늘을 드리우는 듬직한 초록 나무" },
  { level: 6, name: "황금 지혜나무", emoji: "🌟", minSunlight: 2000, maxSunlight: 4999, desc: "반짝이는 황금 열매와 꽃이 만개한 지혜나무" },
  { level: 7, name: "불멸의 세계수", emoji: "👑", minSunlight: 5000, maxSunlight: 999999, desc: "온 우주의 단어를 지키는 영원한 빛의 세계수" }
];

/**
 * 현재 햇살 수량에 따른 보카 트리 정보 계산
 * @param {number} sunlight - 누적 햇살 수
 * @returns {Object} 현재 레벨 정보 및 다음 레벨까지의 진행률(0~100)
 */
export function getTreeInfo(sunlight = 0) {
  let currentStage = TREE_STAGES[0];
  let nextStage = TREE_STAGES[1];

  for (let i = 0; i < TREE_STAGES.length; i++) {
    if (sunlight >= TREE_STAGES[i].minSunlight) {
      currentStage = TREE_STAGES[i];
      nextStage = TREE_STAGES[i + 1] || null;
    }
  }

  let progressPercent = 100;
  let remainingSunlight = 0;

  if (nextStage) {
    const range = nextStage.minSunlight - currentStage.minSunlight;
    const currentInStage = sunlight - currentStage.minSunlight;
    progressPercent = Math.min(100, Math.max(0, Math.round((currentInStage / range) * 100)));
    remainingSunlight = nextStage.minSunlight - sunlight;
  }

  return {
    currentStage,
    nextStage,
    progressPercent,
    remainingSunlight,
    sunlight
  };
}

/**
 * 기본 영단어 고품질 데이터베이스
 */
export const INITIAL_WORDS = [
  // 1. 중학 필수 영단어
  {
    id: "w-mid-1",
    bookId: "middle_800",
    word: "cherish",
    meaning: "소중히 여기다, 아끼다",
    phonetic: "/ˈtʃer.ɪʃ/",
    partOfSpeech: "동사",
    imageUrl: "https://images.unsplash.com/photo-1516589178581-6cd7833ae3b2?w=600&auto=format&fit=crop&q=80",
    exampleSentence: "I cherish the wonderful moments we spent together.",
    exampleTranslation: "나는 우리가 함께 보낸 소중한 순간들을 아낀다.",
    synonyms: ["treasure", "value"],
    antonyms: ["neglect", "ignore"],
    level: "중학",
    repetitionStage: 0,
    lastReviewedAt: null,
    nextReviewAt: new Date().toISOString(),
    isOverdue: false,
    correctCount: 0,
    incorrectCount: 0
  },
  {
    id: "w-mid-2",
    bookId: "middle_800",
    word: "courage",
    meaning: "용기, 담력",
    phonetic: "/ˈkɝː.ɪdʒ/",
    partOfSpeech: "명사",
    imageUrl: "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=600&auto=format&fit=crop&q=80",
    exampleSentence: "It takes courage to stand up and speak the truth.",
    exampleTranslation: "일어서서 진실을 말하는 데는 용기가 필요하다.",
    synonyms: ["bravery", "valor"],
    antonyms: ["cowardice", "fear"],
    level: "중학",
    repetitionStage: 0,
    lastReviewedAt: null,
    nextReviewAt: new Date().toISOString(),
    isOverdue: false,
    correctCount: 0,
    incorrectCount: 0
  },
  {
    id: "w-mid-3",
    bookId: "middle_800",
    word: "curious",
    meaning: "호기심이 많은, 신기한",
    phonetic: "/ˈkjʊr.i.əs/",
    partOfSpeech: "형용사",
    imageUrl: "https://images.unsplash.com/photo-1544717305-2782549b5136?w=600&auto=format&fit=crop&q=80",
    exampleSentence: "The curious puppy explored every corner of the backyard.",
    exampleTranslation: "호기심 많은 강아지가 뒷마당 구석구석을 탐험했다.",
    synonyms: ["inquisitive", "eager"],
    antonyms: ["indifferent", "apathetic"],
    level: "중학",
    repetitionStage: 0,
    lastReviewedAt: null,
    nextReviewAt: new Date().toISOString(),
    isOverdue: false,
    correctCount: 0,
    incorrectCount: 0
  },
  {
    id: "w-mid-4",
    bookId: "middle_800",
    word: "genuine",
    meaning: "진짜의, 순수한, 진실한",
    phonetic: "/ˈdʒen.ju.ɪn/",
    partOfSpeech: "형용사",
    imageUrl: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=600&auto=format&fit=crop&q=80",
    exampleSentence: "She showed genuine kindness to the new transfer student.",
    exampleTranslation: "그녀는 새로 전학 온 학생에게 진심 어린 친절을 베풀었다.",
    synonyms: ["authentic", "sincere"],
    antonyms: ["fake", "deceptive"],
    level: "중학",
    repetitionStage: 0,
    lastReviewedAt: null,
    nextReviewAt: new Date().toISOString(),
    isOverdue: false,
    correctCount: 0,
    incorrectCount: 0
  },
  {
    id: "w-mid-5",
    bookId: "middle_800",
    word: "gratitude",
    meaning: "감사, 고마움",
    phonetic: "/ˈɡræt̬.ə.tuːd/",
    partOfSpeech: "명사",
    imageUrl: "https://images.unsplash.com/photo-1506784983877-45594efa4cbe?w=600&auto=format&fit=crop&q=80",
    exampleSentence: "We expressed our deep gratitude to our teachers on Graduation Day.",
    exampleTranslation: "우리는 졸업식 날 선생님들께 깊은 감사를 전했다.",
    synonyms: ["thankfulness", "appreciation"],
    antonyms: ["ingratitude", "resentment"],
    level: "중학",
    repetitionStage: 0,
    lastReviewedAt: null,
    nextReviewAt: new Date().toISOString(),
    isOverdue: false,
    correctCount: 0,
    incorrectCount: 0
  },
  {
    id: "w-mid-6",
    bookId: "middle_800",
    word: "inspire",
    meaning: "영감을 주다, 고무시키다",
    phonetic: "/ɪnˈspaɪr/",
    partOfSpeech: "동사",
    imageUrl: "https://images.unsplash.com/photo-1499209974431-9dddcece7f88?w=600&auto=format&fit=crop&q=80",
    exampleSentence: "Her passion for science inspires everyone around her.",
    exampleTranslation: "과학에 대한 그녀의 열정은 주변의 모든 이들에게 영감을 준다.",
    synonyms: ["motivate", "encourage"],
    antonyms: ["discourage", "depress"],
    level: "중학",
    repetitionStage: 0,
    lastReviewedAt: null,
    nextReviewAt: new Date().toISOString(),
    isOverdue: false,
    correctCount: 0,
    incorrectCount: 0
  },

  // 2. 고교 수능 빈출 마스터
  {
    id: "w-high-1",
    bookId: "high_1200",
    word: "persistent",
    meaning: "끈기 있는, 끈질긴, 지속적인",
    phonetic: "/pərˈsɪs.tənt/",
    partOfSpeech: "형용사",
    imageUrl: "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=600&auto=format&fit=crop&q=80",
    exampleSentence: "His persistent efforts eventually led to a major academic breakthrough.",
    exampleTranslation: "그의 끈기 있는 노력은 결국 학문적 대혁신으로 이어졌다.",
    synonyms: ["tenacious", "determined"],
    antonyms: ["fleeting", "surrendering"],
    level: "고교수능",
    repetitionStage: 0,
    lastReviewedAt: null,
    nextReviewAt: new Date().toISOString(),
    isOverdue: false,
    correctCount: 0,
    incorrectCount: 0
  },
  {
    id: "w-high-2",
    bookId: "high_1200",
    word: "resilient",
    meaning: "회복력 있는, 곧 기운을 차리는",
    phonetic: "/rɪˈzɪl.jənt/",
    partOfSpeech: "형용사",
    imageUrl: "https://images.unsplash.com/photo-1466692476868-aef1dfb1e735?w=600&auto=format&fit=crop&q=80",
    exampleSentence: "Forests are surprisingly resilient after natural fires.",
    exampleTranslation: "산림은 자연 화재 이후 놀라울 정도로 빠른 회복력을 보인다.",
    synonyms: ["adaptable", "tough"],
    antonyms: ["fragile", "vulnerable"],
    level: "고교수능",
    repetitionStage: 0,
    lastReviewedAt: null,
    nextReviewAt: new Date().toISOString(),
    isOverdue: false,
    correctCount: 0,
    incorrectCount: 0
  },
  {
    id: "w-high-3",
    bookId: "high_1200",
    word: "profound",
    meaning: "심오한, 깊은, 엄청난",
    phonetic: "/prəˈfaʊnd/",
    partOfSpeech: "형용사",
    imageUrl: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&auto=format&fit=crop&q=80",
    exampleSentence: "The philosopher had a profound influence on modern thinking.",
    exampleTranslation: "그 철학자는 현대인의 사고방식에 깊은 영향을 끼쳤다.",
    synonyms: ["deep", "insightful"],
    antonyms: ["superficial", "shallow"],
    level: "고교수능",
    repetitionStage: 0,
    lastReviewedAt: null,
    nextReviewAt: new Date().toISOString(),
    isOverdue: false,
    correctCount: 0,
    incorrectCount: 0
  },
  {
    id: "w-high-4",
    bookId: "high_1200",
    word: "contemplate",
    meaning: "심사숙고하다, 깊이 생각하다",
    phonetic: "/ˈkɑːn.təm.pleɪt/",
    partOfSpeech: "동사",
    imageUrl: "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=600&auto=format&fit=crop&q=80",
    exampleSentence: "He sat by the window to contemplate his future career path.",
    exampleTranslation: "그는 미래 진로를 깊이 생각하기 위해 창가에 앉았다.",
    synonyms: ["ponder", "meditate"],
    antonyms: ["overlook", "ignore"],
    level: "고교수능",
    repetitionStage: 0,
    lastReviewedAt: null,
    nextReviewAt: new Date().toISOString(),
    isOverdue: false,
    correctCount: 0,
    incorrectCount: 0
  },
  {
    id: "w-high-5",
    bookId: "high_1200",
    word: "ambiguous",
    meaning: "모호한, 여러 의미로 해석되는",
    phonetic: "/æmˈbɪɡ.ju.əs/",
    partOfSpeech: "형용사",
    imageUrl: "https://images.unsplash.com/photo-1518495973542-4542c06a5843?w=600&auto=format&fit=crop&q=80",
    exampleSentence: "The ending of the novel was intentionally ambiguous.",
    exampleTranslation: "그 소설의 결말은 의도적으로 모호하게 처리되었다.",
    synonyms: ["vague", "unclear"],
    antonyms: ["precise", "clear"],
    level: "고교수능",
    repetitionStage: 0,
    lastReviewedAt: null,
    nextReviewAt: new Date().toISOString(),
    isOverdue: false,
    correctCount: 0,
    incorrectCount: 0
  },
  {
    id: "w-high-6",
    bookId: "high_1200",
    word: "empathy",
    meaning: "공감, 감정이입",
    phonetic: "/ˈem.pə.θi/",
    partOfSpeech: "명사",
    imageUrl: "https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=600&auto=format&fit=crop&q=80",
    exampleSentence: "Empathy allows us to build stronger and more compassionate communities.",
    exampleTranslation: "공감 능력은 더 단단하고 따뜻한 공동체를 만드는 원동력이다.",
    synonyms: ["compassion", "understanding"],
    antonyms: ["apathy", "indifference"],
    level: "고교수능",
    repetitionStage: 0,
    lastReviewedAt: null,
    nextReviewAt: new Date().toISOString(),
    isOverdue: false,
    correctCount: 0,
    incorrectCount: 0
  },

  // 3. 토익/토플 실전 보카
  {
    id: "w-toeic-1",
    bookId: "toeic_1000",
    word: "feasible",
    meaning: "실현 가능한, 그럴싸한",
    phonetic: "/ˈfiː.zə.bəl/",
    partOfSpeech: "형용사",
    imageUrl: "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=600&auto=format&fit=crop&q=80",
    exampleSentence: "The committee concluded that the project proposal is economically feasible.",
    exampleTranslation: "위원회는 그 사업 제안서가 경제적으로 실현 가능하다고 결론지었다.",
    synonyms: ["viable", "practicable"],
    antonyms: ["impossible", "impractical"],
    level: "실전",
    repetitionStage: 0,
    lastReviewedAt: null,
    nextReviewAt: new Date().toISOString(),
    isOverdue: false,
    correctCount: 0,
    incorrectCount: 0
  },
  {
    id: "w-toeic-2",
    bookId: "toeic_1000",
    word: "reimburse",
    meaning: "환급하다, 변제하다, 배상하다",
    phonetic: "/ˌriː.ɪmˈbɝːs/",
    partOfSpeech: "동사",
    imageUrl: "https://images.unsplash.com/photo-1554224155-8d04cb21cd6c?w=600&auto=format&fit=crop&q=80",
    exampleSentence: "The company will reimburse all travel expenses upon submission of receipts.",
    exampleTranslation: "회사는 영수증 제출 시 모든 출장 경비를 환급해 줄 것이다.",
    synonyms: ["refund", "repay"],
    antonyms: ["deprive", "charge"],
    level: "실전",
    repetitionStage: 0,
    lastReviewedAt: null,
    nextReviewAt: new Date().toISOString(),
    isOverdue: false,
    correctCount: 0,
    incorrectCount: 0
  },
  {
    id: "w-toeic-3",
    bookId: "toeic_1000",
    word: "unprecedented",
    meaning: "전례 없는, 유례없는",
    phonetic: "/ʌnˈpres.ə.den.t̬ɪd/",
    partOfSpeech: "형용사",
    imageUrl: "https://images.unsplash.com/photo-1518770660439-4636190af475?w=600&auto=format&fit=crop&q=80",
    exampleSentence: "The technology firm reported unprecedented growth in the third quarter.",
    exampleTranslation: "그 IT 기업은 3분기에 전례 없는 높은 성장을 기록했다.",
    synonyms: ["groundbreaking", "unmatched"],
    antonyms: ["customary", "typical"],
    level: "실전",
    repetitionStage: 0,
    lastReviewedAt: null,
    nextReviewAt: new Date().toISOString(),
    isOverdue: false,
    correctCount: 0,
    incorrectCount: 0
  },
  {
    id: "w-toeic-4",
    bookId: "toeic_1000",
    word: "substantiate",
    meaning: "입증하다, 실증하다",
    phonetic: "/səbˈstæn.ʃi.eɪt/",
    partOfSpeech: "동사",
    imageUrl: "https://images.unsplash.com/photo-1450133064473-71024230f91b?w=600&auto=format&fit=crop&q=80",
    exampleSentence: "The auditor asked for additional records to substantiate the tax deductions.",
    exampleTranslation: "회계감사인은 세금 공제를 입증하기 위한 추가 서류를 요청했다.",
    synonyms: ["verify", "validate"],
    antonyms: ["disprove", "refute"],
    level: "실전",
    repetitionStage: 0,
    lastReviewedAt: null,
    nextReviewAt: new Date().toISOString(),
    isOverdue: false,
    correctCount: 0,
    incorrectCount: 0
  },
  {
    id: "w-toeic-5",
    bookId: "toeic_1000",
    word: "tentative",
    meaning: "잠정적인, 시험적인, 임시의",
    phonetic: "/ˈten.t̬ə.t̬ɪv/",
    partOfSpeech: "형용사",
    imageUrl: "https://images.unsplash.com/photo-1506784365847-bbad939e9335?w=600&auto=format&fit=crop&q=80",
    exampleSentence: "We reached a tentative agreement pending board approval.",
    exampleTranslation: "우리는 이사회 승인을 전제로 한 잠정 합의에 도달했다.",
    synonyms: ["provisional", "interim"],
    antonyms: ["definite", "final"],
    level: "실전",
    repetitionStage: 0,
    lastReviewedAt: null,
    nextReviewAt: new Date().toISOString(),
    isOverdue: false,
    correctCount: 0,
    incorrectCount: 0
  },
  {
    id: "w-toeic-6",
    bookId: "toeic_1000",
    word: "streamline",
    meaning: "간소화하다, 능률화하다",
    phonetic: "/ˈstriːm.laɪn/",
    partOfSpeech: "동사",
    imageUrl: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=600&auto=format&fit=crop&q=80",
    exampleSentence: "The new ERP software will streamline the entire inventory process.",
    exampleTranslation: "새로운 ERP 소프트웨어는 전체 재고 관리 과정을 획기적으로 간소화할 것이다.",
    synonyms: ["simplify", "optimize"],
    antonyms: ["complicate", "hinder"],
    level: "실전",
    repetitionStage: 0,
    lastReviewedAt: null,
    nextReviewAt: new Date().toISOString(),
    isOverdue: false,
    correctCount: 0,
    incorrectCount: 0
  }
];

/**
 * 2일 이상 경과 여부 확인
 */
export function calculateIsOverdue(word) {
  if (!word.nextReviewAt) return false;
  const nextTime = new Date(word.nextReviewAt).getTime();
  const now = Date.now();
  return (now - nextTime) >= OVERDUE_THRESHOLD_MS;
}

/**
 * 단어 목록 전체에 대해 현재 시점 기준 누적(isOverdue) 상태 갱신
 */
export function refreshWordsOverdueStatus(words) {
  return words.map(word => ({
    ...word,
    isOverdue: calculateIsOverdue(word)
  }));
}

/**
 * 로컬스토리지에서 단어 로드
 */
export function loadWords() {
  try {
    const raw = localStorage.getItem(STORAGE_KEYS.WORDS);
    if (!raw) {
      saveWords(INITIAL_WORDS);
      return refreshWordsOverdueStatus(INITIAL_WORDS);
    }
    return refreshWordsOverdueStatus(JSON.parse(raw));
  } catch (err) {
    console.error("단어 로드 실패:", err);
    return refreshWordsOverdueStatus(INITIAL_WORDS);
  }
}

/**
 * 로컬스토리지에 단어 저장
 */
export function saveWords(words) {
  try {
    localStorage.setItem(STORAGE_KEYS.WORDS, JSON.stringify(words));
  } catch (err) {
    console.error("단어 저장 실패:", err);
  }
}

/**
 * 커리큘럼 데이터 로드
 */
export function loadCurriculum() {
  try {
    const raw = localStorage.getItem(STORAGE_KEYS.CURRICULUM);
    if (!raw) return null;
    return JSON.parse(raw);
  } catch (err) {
    return null;
  }
}

/**
 * 커리큘럼 데이터 저장
 */
export function saveCurriculum(curr) {
  try {
    localStorage.setItem(STORAGE_KEYS.CURRICULUM, JSON.stringify(curr));
  } catch (err) {
    console.error("커리큘럼 저장 실패:", err);
  }
}

/**
 * 보카 트리 햇살 데이터 로드
 */
export function loadTreeData() {
  try {
    const raw = localStorage.getItem(STORAGE_KEYS.TREE);
    if (!raw) return { sunlight: 0 };
    return JSON.parse(raw);
  } catch (err) {
    return { sunlight: 0 };
  }
}

/**
 * 보카 트리 햇살 데이터 저장 및 1 증가
 */
export function addSunlight(amount = 1) {
  try {
    const current = loadTreeData();
    const updated = {
      ...current,
      sunlight: (current.sunlight || 0) + amount,
      lastUpdatedAt: new Date().toISOString()
    };
    localStorage.setItem(STORAGE_KEYS.TREE, JSON.stringify(updated));
    return updated;
  } catch (err) {
    return { sunlight: amount };
  }
}

/**
 * 복습 후 단어 상태 갱신 (1일 -> 7일 -> 30일)
 */
export function updateWordAfterReview(word, isSuccess) {
  const now = new Date();
  let newStage = word.repetitionStage || 0;

  if (isSuccess) {
    newStage = Math.min(newStage + 1, REVIEW_INTERVALS.length);
  } else {
    newStage = 1; // 실패 시 내일 1차 복습으로 유도
  }

  const intervalDays = REVIEW_INTERVALS[Math.max(0, newStage - 1)];
  const nextDate = new Date(now.getTime() + intervalDays * 24 * 60 * 60 * 1000);

  return {
    ...word,
    repetitionStage: newStage,
    lastReviewedAt: now.toISOString(),
    nextReviewAt: nextDate.toISOString(),
    isOverdue: false,
    correctCount: (word.correctCount || 0) + (isSuccess ? 1 : 0),
    incorrectCount: (word.incorrectCount || 0) + (isSuccess ? 0 : 1)
  };
}

/**
 * 복습 비율별 무작위 추출
 */
export function sampleWordsByRatio(words, ratio = 1.0) {
  if (!words || words.length === 0) return [];
  const shuffled = [...words].sort(() => Math.random() - 0.5);
  if (ratio >= 1.0) return shuffled;
  const count = Math.max(1, Math.round(words.length * ratio));
  return shuffled.slice(0, count);
}

/**
 * Web Speech API 영어 원어민 발음 TTS 재생
 */
export function speakWord(text) {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const utter = new SpeechSynthesisUtterance(text);
  utter.lang = 'en-US';
  utter.rate = 0.9;
  utter.pitch = 1.0;
  window.speechSynthesis.speak(utter);
}
