/**
 * ==============================================================================
 * 보카하이 (vocahigh) - 메인 리액트 웹 애플리케이션 (app.jsx)
 * ==============================================================================
 * 
 * [완전 구현 기능 목록]
 * 1. 모바일 퍼스트 스마트폰 프레임 뷰포트 (Max Width 430px) & 둥글둥글한 UI
 * 2. 다크 모드 (딥 포레스트) / 화이트 모드 (웜 아이보리 크림) 테마 전환 엔진
 * 3. 좌측 사이드 드로어 메뉴 (이어 학습하기, 학습 현황, 학습 랭킹, 보카 트리, 커리큘럼, 기능설명/튜토리얼)
 * 4. 커리큘럼 필수 가드 & 출석 인정 기준 커스텀 체크박스 4종 (학습단어장, 플래시카드, 워드리콜, 스펠링)
 * 5. 메인 홈: 오늘의 학습목표 카드 + 장기기억 SAVE 카드
 * 6. 단어 학습 (카드/리스트 뷰) & 훈련 (플래시카드, 워드 리콜 4지선다, 스펠링)
 * 7. 보카 트리 7단계 성장 (단어 1개당 무조건 햇살 1 ☀️ +1 적립)
 * 8. 에빙하우스 망각곡선 3대 주기 (1일, 7일, 30일) 및 30~100% 분량 복습
 * 9. 인터랙티브 기능 튜토리얼 (샌드박스 모드 + 검정 반투명 스포트라이트 오버레이)
 */

import React, { useState, useEffect, useMemo, useRef } from 'react';
import {
  BOOKS_DATA,
  TREE_STAGES,
  INITIAL_WORDS,
  loadWords,
  saveWords,
  loadCurriculum,
  saveCurriculum,
  loadTreeData,
  addSunlight,
  getTreeInfo,
  updateWordAfterReview,
  sampleWordsByRatio,
  speakWord
} from './data.js';

export default function VocaHighApp() {
  // ----------------------------------------------------------------------------
  // [상태 1] 테마 (다크 / 화이트(웜 크림))
  // ----------------------------------------------------------------------------
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('VOCAHIGH_THEME_V3') || 'light';
  });

  const toggleTheme = () => {
    const nextTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(nextTheme);
    localStorage.setItem('VOCAHIGH_THEME_V3', nextTheme);
  };

  // ----------------------------------------------------------------------------
  // [상태 2] 사용자 인증 및 세션 (간편 인증)
  // ----------------------------------------------------------------------------
  const [user, setUser] = useState(() => {
    const saved = localStorage.getItem('VOCAHIGH_USER_V3');
    return saved ? JSON.parse(saved) : { name: "학생 사용자", email: "student@vocahigh.com", isLoggedIn: true };
  });

  // ----------------------------------------------------------------------------
  // [상태 3] 단어 데이터 및 커리큘럼
  // ----------------------------------------------------------------------------
  const [words, setWords] = useState(() => loadWords());
  const [curriculum, setCurriculum] = useState(() => loadCurriculum());

  // ----------------------------------------------------------------------------
  // [상태 4] 보카 트리 햇살 데이터
  // ----------------------------------------------------------------------------
  const [treeData, setTreeData] = useState(() => loadTreeData());
  const treeInfo = useMemo(() => getTreeInfo(treeData.sunlight || 0), [treeData.sunlight]);

  // 햇살 획득 시 팝업 애니메이션 효과
  const [floatingSun, setFloatingSun] = useState(false);
  const triggerSunlightAnimation = (amount = 1) => {
    const updated = addSunlight(amount);
    setTreeData(updated);
    setFloatingSun(true);
    setTimeout(() => setFloatingSun(false), 1200);
  };

  // ----------------------------------------------------------------------------
  // [상태 5] 오늘 당일 학습 달성 현황 (출석 기준 체크용)
  // ----------------------------------------------------------------------------
  const todayKey = new Date().toISOString().split('T')[0];
  const [dailyProgress, setDailyProgress] = useState(() => {
    const saved = localStorage.getItem(`VOCAHIGH_DAILY_${todayKey}`);
    return saved ? JSON.parse(saved) : {
      studyCompleted: false,     // 학습 단어장 완료 여부
      flashcardCompleted: false, // 플래시카드 완료 여부
      recallCompleted: false,    // 워드 리콜 완료 여부
      spellingCompleted: false,  // 스펠링 완료 여부
      isAttendanceStamped: false // 출석 도장 날인 여부
    };
  });

  const saveDailyProgress = (newProgress) => {
    setDailyProgress(newProgress);
    localStorage.setItem(`VOCAHIGH_DAILY_${todayKey}`, JSON.stringify(newProgress));
  };

  // 출석 인정 여부 자동 판별 (커리큘럼에 설정된 체크박스 항목을 모두 완수했는지 검사)
  useEffect(() => {
    if (!curriculum || !curriculum.attendanceCriteria || dailyProgress.isAttendanceStamped) return;
    
    const criteria = curriculum.attendanceCriteria; // 예: ['vocab_study', 'recall']
    let allDone = true;

    if (criteria.includes('vocab_study') && !dailyProgress.studyCompleted) allDone = false;
    if (criteria.includes('flashcard') && !dailyProgress.flashcardCompleted) allDone = false;
    if (criteria.includes('recall') && !dailyProgress.recallCompleted) allDone = false;
    if (criteria.includes('spelling') && !dailyProgress.spellingCompleted) allDone = false;

    if (allDone && criteria.length > 0) {
      const updated = { ...dailyProgress, isAttendanceStamped: true };
      saveDailyProgress(updated);
      alert("🎉 축하합니다! 오늘의 커리큘럼 기준을 모두 완수하여 '오늘의 출석 도장'이 쾅! 찍혔습니다!");
    }
  }, [dailyProgress, curriculum]);

  // ----------------------------------------------------------------------------
  // [상태 6] 화면 네비게이션
  // ----------------------------------------------------------------------------
  // 'home' | 'curriculum_setup' | 'study' | 'train_select' | 'flashcard' | 'word_recall' | 'spelling' | 'review' | 'tree' | 'my'
  const [currentTab, setCurrentTab] = useState('home');

  // 좌측 사이드 드로어 열림/닫힘
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  // 모달 팝업 상태 (학습현황, 랭킹, 기능설명)
  const [modalType, setModalType] = useState(null); // 'stats' | 'ranking' | 'guide' | null

  // ----------------------------------------------------------------------------
  // [상태 7] 인터랙티브 기능 튜토리얼 (Sandbox + 스포트라이트 오버레이)
  // ----------------------------------------------------------------------------
  const [isTutorialActive, setIsTutorialActive] = useState(false);
  const [tutorialStep, setTutorialStep] = useState(1); // 1: 커리큘럼 생성 유도, 2: 단어 학습 유도, 3: 출석 도장 체험

  const startTutorial = () => {
    setIsDrawerOpen(false);
    setModalType(null);
    setIsTutorialActive(true);
    setTutorialStep(1);
  };

  const nextTutorialStep = () => {
    if (tutorialStep >= 3) {
      setIsTutorialActive(false);
      setTutorialStep(1);
      alert("🎓 기능 튜토리얼을 완주하셨습니다! 이제 마음껏 보카하이를 즐겨보세요!");
    } else {
      setTutorialStep(tutorialStep + 1);
    }
  };

  const exitTutorial = () => {
    setIsTutorialActive(false);
    setTutorialStep(1);
  };

  // ----------------------------------------------------------------------------
  // [헬퍼] 현재 커리큘럼에 배정된 오늘의 단어 목록 추출
  // ----------------------------------------------------------------------------
  const activeBookWords = useMemo(() => {
    if (!curriculum) return [];
    return words.filter(w => w.bookId === curriculum.bookId);
  }, [words, curriculum]);

  const todayStudyWords = useMemo(() => {
    if (!curriculum || activeBookWords.length === 0) return [];
    const count = curriculum.dailyGoal || 10;
    return activeBookWords.slice(0, count);
  }, [curriculum, activeBookWords]);

  // 망각곡선 복습 대상 단어들 (기한 도래 또는 오버듀)
  const dueReviewWords = useMemo(() => {
    const now = Date.now();
    return words.filter(w => {
      if (!w.nextReviewAt) return false;
      return new Date(w.nextReviewAt).getTime() <= now || w.isOverdue;
    });
  }, [words]);

  const overdueWordsCount = useMemo(() => {
    return words.filter(w => w.isOverdue).length;
  }, [words]);

  // ----------------------------------------------------------------------------
  // [커리큘럼 미설정 시 강제 유도 가드]
  // ----------------------------------------------------------------------------
  useEffect(() => {
    if (!curriculum && !isTutorialActive) {
      setCurrentTab('curriculum_setup');
    }
  }, [curriculum, isTutorialActive]);

  // ============================================================================
  // [화면 1: 커리큘럼 생성/설정 화면]
  // ============================================================================
  const CurriculumSetupScreen = () => {
    const [selectedBookId, setSelectedBookId] = useState(curriculum?.bookId || 'middle_800');
    const [dailyGoal, setDailyGoal] = useState(curriculum?.dailyGoal || 20);
    const [days, setDays] = useState(curriculum?.days || ['월', '화', '수', '목', '금']);
    
    // 출석 인정 기준 체크박스 4종
    const [criteria, setCriteria] = useState(curriculum?.attendanceCriteria || ['vocab_study', 'recall']);

    const toggleDay = (day) => {
      setDays(prev => prev.includes(day) ? prev.filter(d => d !== day) : [...prev, day]);
    };

    const toggleCriteria = (key) => {
      setCriteria(prev => prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]);
    };

    const handleSave = () => {
      if (days.length === 0) {
        alert("학습 요일을 최소 하루 이상 선택해 주세요!");
        return;
      }
      if (criteria.length === 0) {
        alert("출석 인정 기준을 최소 한 가지 이상 선택해 주세요!");
        return;
      }

      const newCurr = {
        bookId: selectedBookId,
        dailyGoal: Number(dailyGoal),
        days,
        attendanceCriteria: criteria,
        createdAt: new Date().toISOString()
      };

      saveCurriculum(newCurr);
      setCurriculum(newCurr);
      setCurrentTab('home');
      alert("✅ 단어 커리큘럼이 성공적으로 저장되었습니다!");
    };

    return (
      <div className="p-5 pb-24 space-y-6 animate-fadeIn">
        <div className="text-center space-y-2">
          <span className="inline-block px-3 py-1 text-xs font-bold rounded-full bg-[#A1C954]/20 text-[#5F8D4E] dark:text-[#A1C954]">
            맞춤 커리큘럼 설정
          </span>
          <h1 className="text-2xl font-black text-[#2D5A27] dark:text-[#A1C954]">
            어떤 단어장을 정복해 볼까요?
          </h1>
          <p className="text-xs text-stone-500 dark:text-stone-400">
            목표를 설정해야 매일 즐거운 학습 습관이 완성됩니다.
          </p>
        </div>

        {/* 1. 단어장 선택 */}
        <div className="space-y-3">
          <label className="block text-sm font-bold text-[#2C3E2D] dark:text-[#EDECE4]">
            1. 단어장 선택 (Book)
          </label>
          <div className="space-y-3">
            {BOOKS_DATA.map(book => {
              const isSelected = selectedBookId === book.id;
              return (
                <div
                  key={book.id}
                  onClick={() => setSelectedBookId(book.id)}
                  className={`p-4 rounded-3xl border-2 transition-all cursor-pointer flex items-center justify-between ${
                    isSelected
                      ? 'border-[#2D5A27] bg-[#FAF6EC] dark:bg-[#203624] dark:border-[#A1C954] shadow-md scale-[1.01]'
                      : 'border-stone-200 dark:border-stone-800 bg-white dark:bg-[#1D2A1F] hover:border-[#5F8D4E]'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">{book.icon}</span>
                    <div>
                      <div className="font-bold text-sm text-[#2C3E2D] dark:text-[#EDECE4]">
                        {book.title}
                      </div>
                      <div className="text-xs text-stone-500 dark:text-stone-400">
                        {book.subtitle} • {book.totalWords}단어
                      </div>
                    </div>
                  </div>
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center border-2 ${
                    isSelected ? 'bg-[#2D5A27] border-[#2D5A27] text-white' : 'border-stone-300'
                  }`}>
                    {isSelected && <span className="text-xs">✓</span>}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* 2. 일일 목표 단어 수 */}
        <div className="space-y-3">
          <label className="block text-sm font-bold text-[#2C3E2D] dark:text-[#EDECE4]">
            2. 하루 학습 목표량 (일일 단어 수)
          </label>
          <div className="grid grid-cols-4 gap-2">
            {[10, 20, 30, 50].map(cnt => (
              <button
                key={cnt}
                type="button"
                onClick={() => setDailyGoal(cnt)}
                className={`py-3 rounded-2xl font-bold text-sm transition-all ${
                  dailyGoal === cnt
                    ? 'bg-[#2D5A27] text-white shadow-md scale-105'
                    : 'bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 text-stone-700 dark:text-stone-300'
                }`}
              >
                {cnt}개
              </button>
            ))}
          </div>
        </div>

        {/* 3. 학습 요일 선택 */}
        <div className="space-y-3">
          <label className="block text-sm font-bold text-[#2C3E2D] dark:text-[#EDECE4]">
            3. 학습 요일 선택
          </label>
          <div className="flex justify-between gap-1">
            {['월', '화', '수', '목', '금', '토', '일'].map(d => {
              const active = days.includes(d);
              return (
                <button
                  key={d}
                  type="button"
                  onClick={() => toggleDay(d)}
                  className={`w-11 h-11 rounded-2xl font-bold text-sm flex items-center justify-center transition-all ${
                    active
                      ? 'bg-[#5F8D4E] text-white shadow-sm'
                      : 'bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 text-stone-400'
                  }`}
                >
                  {d}
                </button>
              );
            })}
          </div>
        </div>

        {/* 4. 출석 체크 인정 기준 체크박스 4종 (핵심 요구사항) */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <label className="block text-sm font-bold text-[#2C3E2D] dark:text-[#EDECE4]">
              4. 출석 인정 기준 선택 (중복 가능)
            </label>
            <span className="text-[11px] text-[#5F8D4E] dark:text-[#A1C954]">
              선택한 항목을 완료해야 출석!
            </span>
          </div>
          <div className="space-y-2">
            {[
              { id: 'vocab_study', label: '📖 학습 단어장', desc: '기본 단어 카드로 뜻과 예문 확인' },
              { id: 'flashcard', label: '🃏 플래시카드', desc: '카드를 앞뒤로 뒤집으며 기억 인출' },
              { id: 'recall', label: '🧠 워드리콜 (Word Recall)', desc: '4개 보기 중 올바른 뜻 즉시 회상' },
              { id: 'spelling', label: '✍️ 스펠링 훈련', desc: '가상 키보드로 철자 직접 타이핑' }
            ].map(item => {
              const checked = criteria.includes(item.id);
              return (
                <div
                  key={item.id}
                  onClick={() => toggleCriteria(item.id)}
                  className={`p-3.5 rounded-2xl border-2 transition-all cursor-pointer flex items-center gap-3.5 ${
                    checked
                      ? 'bg-[#F1F8E9] dark:bg-[#203624] border-[#5F8D4E] dark:border-[#A1C954]'
                      : 'bg-white dark:bg-[#1D2A1F] border-stone-200 dark:border-stone-800'
                  }`}
                >
                  <div className={`w-5 h-5 rounded-lg flex items-center justify-center border-2 ${
                    checked ? 'bg-[#5F8D4E] border-[#5F8D4E] text-white' : 'border-stone-300'
                  }`}>
                    {checked && <span className="text-xs">✓</span>}
                  </div>
                  <div className="flex-1">
                    <div className="font-bold text-sm text-[#2C3E2D] dark:text-[#EDECE4]">
                      {item.label}
                    </div>
                    <div className="text-xs text-stone-500 dark:text-stone-400">
                      {item.desc}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* 저장 버튼 */}
        <button
          onClick={handleSave}
          className="w-full py-4 bg-[#2D5A27] hover:bg-[#244b1f] text-white font-extrabold text-base rounded-2xl shadow-lg active:scale-98 transition-all flex items-center justify-center gap-2"
        >
          <span>🌱</span>
          <span>커리큘럼 설정 완료하고 시작하기</span>
        </button>
      </div>
    );
  };

  // ============================================================================
  // [화면 2: 메인 홈 대시보드 - design_guide/메인 화면.png 기준]
  // ============================================================================
  const HomeScreen = () => {
    const activeBook = BOOKS_DATA.find(b => b.id === curriculum?.bookId) || BOOKS_DATA[0];
    const goalCount = curriculum?.dailyGoal || 10;
    const progressPercent = Math.min(100, Math.round((todayStudyWords.length / goalCount) * 100));

    return (
      <div className="p-5 pb-24 space-y-6 animate-fadeIn">
        {/* 상단 웰컴 인사 및 보카 트리 요약 바 */}
        <div 
          onClick={() => setCurrentTab('tree')}
          className="p-4 rounded-3xl bg-gradient-to-r from-[#2D5A27] to-[#5F8D4E] text-white shadow-md cursor-pointer hover:shadow-lg transition-all flex items-center justify-between"
        >
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-2xl bg-white/20 flex items-center justify-center text-2xl">
              {treeInfo.currentStage.emoji}
            </div>
            <div>
              <div className="text-xs text-white/80 font-medium">나의 보카 트리</div>
              <div className="font-black text-base">
                Lv.{treeInfo.currentStage.level} {treeInfo.currentStage.name}
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-xs text-[#A1C954] font-bold">☀️ {treeInfo.sunlight} 햇살</div>
            <div className="text-[10px] text-white/70">나무 보러가기 →</div>
          </div>
        </div>

        {/* 🎯 카드 1: [오늘의 학습목표] (design_guide/메인 화면.png) */}
        <div className="bg-white dark:bg-[#1D2A1F] border border-[#F0E9D7] dark:border-[#2E4232] rounded-3xl p-6 shadow-sm space-y-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xl">🎯</span>
              <h2 className="text-lg font-black text-[#2D5A27] dark:text-[#A1C954]">
                오늘의 학습목표
              </h2>
            </div>
            {dailyProgress.isAttendanceStamped ? (
              <span className="px-3 py-1 bg-[#A1C954]/20 text-[#2D5A27] dark:text-[#A1C954] text-xs font-black rounded-full flex items-center gap-1 border border-[#A1C954]">
                <span>쾅!</span> 출석 완료
              </span>
            ) : (
              <span className="px-3 py-1 bg-stone-100 dark:bg-stone-800 text-stone-600 dark:text-stone-300 text-xs font-bold rounded-full">
                학습 진행 중
              </span>
            )}
          </div>

          <div>
            <div className="text-xs text-stone-500 dark:text-stone-400">선택된 단어장</div>
            <div className="text-base font-bold text-[#2C3E2D] dark:text-[#EDECE4]">
              {activeBook.title}
            </div>
          </div>

          {/* 프로그레스 바 */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs font-bold text-stone-600 dark:text-stone-300">
              <span>오늘의 단어 진도</span>
              <span>{todayStudyWords.length}개 / 목표 {goalCount}개 ({progressPercent}%)</span>
            </div>
            <div className="w-full h-3 bg-stone-100 dark:bg-stone-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-[#5F8D4E] to-[#A1C954] transition-all duration-500"
                style={{ width: `${progressPercent}%` }}
              />
            </div>
          </div>

          {/* 내가 설정한 출석 기준 항목 완료 배지 현황 */}
          <div className="p-3.5 rounded-2xl bg-[#FAF6EC] dark:bg-[#162418] border border-[#EADBCA] dark:border-[#28382a] space-y-2">
            <div className="text-[11px] font-bold text-[#5F8D4E] dark:text-[#A1C954] flex items-center justify-between">
              <span>내 출석 체크 기준 완수 현황</span>
              <span>완료 시 자동 도장</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-xs">
              {curriculum?.attendanceCriteria?.map(critId => {
                const map = {
                  vocab_study: { label: '학습 단어장', done: dailyProgress.studyCompleted },
                  flashcard: { label: '플래시카드', done: dailyProgress.flashcardCompleted },
                  recall: { label: '워드리콜', done: dailyProgress.recallCompleted },
                  spelling: { label: '스펠링 훈련', done: dailyProgress.spellingCompleted }
                };
                const item = map[critId] || { label: critId, done: false };
                return (
                  <div
                    key={critId}
                    className={`px-2.5 py-1.5 rounded-xl font-bold flex items-center justify-between ${
                      item.done
                        ? 'bg-[#A1C954]/30 text-[#2D5A27] dark:text-[#A1C954]'
                        : 'bg-white dark:bg-[#1D2A1F] text-stone-400 border border-stone-200 dark:border-stone-800'
                    }`}
                  >
                    <span>{item.label}</span>
                    <span>{item.done ? '✓' : '미완료'}</span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* 주요 학습 버튼 2종 */}
          <div className="grid grid-cols-2 gap-3 pt-1">
            <button
              onClick={() => setCurrentTab('study')}
              className="py-3.5 px-4 bg-[#2D5A27] hover:bg-[#23471f] text-white font-bold text-sm rounded-2xl shadow-md active:scale-95 transition-all flex items-center justify-center gap-1.5"
            >
              <span>📖</span>
              <span>학습 단어장</span>
            </button>
            <button
              onClick={() => setCurrentTab('train_select')}
              className="py-3.5 px-4 bg-[#5F8D4E] hover:bg-[#4d733f] text-white font-bold text-sm rounded-2xl shadow-md active:scale-95 transition-all flex items-center justify-center gap-1.5"
            >
              <span>⚡</span>
              <span>훈련 단어장</span>
            </button>
          </div>
        </div>

        {/* 🧠 카드 2: [장기기억 SAVE] (design_guide/메인 화면.png) */}
        <div className="bg-white dark:bg-[#1D2A1F] border border-[#F0E9D7] dark:border-[#2E4232] rounded-3xl p-6 shadow-sm space-y-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xl">🧠</span>
              <h2 className="text-lg font-black text-[#2D5A27] dark:text-[#A1C954]">
                장기기억 SAVE
              </h2>
            </div>
            {overdueWordsCount > 0 && (
              <span className="px-3 py-1 bg-[#C24A4A]/20 text-[#C24A4A] text-xs font-bold rounded-full animate-pulse flex items-center gap-1">
                <span>⚠️</span> 밀린 복습 {overdueWordsCount}개
              </span>
            )}
          </div>

          <p className="text-xs text-stone-500 dark:text-stone-400">
            에빙하우스 망각곡선 3대 주기(1일, 7일, 30일)에 맞춰 기억이 사라지기 직전에 자동으로 찾아옵니다.
          </p>

          {/* 복습 주기별 요약 수치 */}
          <div className="grid grid-cols-3 gap-2 text-center">
            <div className="p-3 rounded-2xl bg-[#FAF6EC] dark:bg-[#162418] border border-[#EADBCA] dark:border-[#28382a]">
              <div className="text-[10px] text-stone-500 dark:text-stone-400 font-bold">1차 (1일 후)</div>
              <div className="text-lg font-black text-[#2D5A27] dark:text-[#A1C954]">
                {words.filter(w => w.repetitionStage === 1).length}개
              </div>
            </div>
            <div className="p-3 rounded-2xl bg-[#FAF6EC] dark:bg-[#162418] border border-[#EADBCA] dark:border-[#28382a]">
              <div className="text-[10px] text-stone-500 dark:text-stone-400 font-bold">2차 (7일 후)</div>
              <div className="text-lg font-black text-[#5F8D4E] dark:text-[#A1C954]">
                {words.filter(w => w.repetitionStage === 2).length}개
              </div>
            </div>
            <div className="p-3 rounded-2xl bg-[#FAF6EC] dark:bg-[#162418] border border-[#EADBCA] dark:border-[#28382a]">
              <div className="text-[10px] text-stone-500 dark:text-stone-400 font-bold">3차 (30일 후)</div>
              <div className="text-lg font-black text-[#A1C954]">
                {words.filter(w => w.repetitionStage >= 3).length}개
              </div>
            </div>
          </div>

          {/* 복습 시작 CTA */}
          <button
            onClick={() => setCurrentTab('review')}
            className="w-full py-4 bg-[#5F8D4E] hover:bg-[#4d733f] text-white font-extrabold text-sm rounded-2xl shadow-md active:scale-98 transition-all flex items-center justify-center gap-2"
          >
            <span>🔄</span>
            <span>망각곡선 복습 시작하기 ({dueReviewWords.length}단어 대기 중)</span>
          </button>
        </div>
      </div>
    );
  };

  // ============================================================================
  // [화면 3: 학습 단어장 (카드 뷰 / 리스트 뷰)]
  // ============================================================================
  const StudyVocabScreen = () => {
    const [viewMode, setViewMode] = useState('card'); // 'card' | 'list'
    const [currentIndex, setCurrentIndex] = useState(0);
    const [hideMeaning, setHideMeaning] = useState(false);

    const wordList = todayStudyWords;
    const currentWord = wordList[currentIndex] || wordList[0];

    const handleNext = () => {
      triggerSunlightAnimation(1); // 단어 1개 완료 시 햇살 1 획득!
      if (currentIndex < wordList.length - 1) {
        setCurrentIndex(currentIndex + 1);
      } else {
        // 학습 단어장 완수 플래그 처리
        saveDailyProgress({ ...dailyProgress, studyCompleted: true });
        alert("🎉 오늘의 학습 단어장을 모두 확인했습니다! (햇살 획득 완료)");
        setCurrentTab('home');
      }
    };

    if (!currentWord) {
      return (
        <div className="p-8 text-center space-y-4">
          <p>오늘의 단어가 없습니다.</p>
          <button onClick={() => setCurrentTab('home')} className="px-4 py-2 bg-[#2D5A27] text-white rounded-xl">
            홈으로 돌아가기
          </button>
        </div>
      );
    }

    return (
      <div className="p-5 pb-24 space-y-5 animate-fadeIn">
        {/* 상단 네비 */}
        <div className="flex items-center justify-between">
          <button
            onClick={() => setCurrentTab('home')}
            className="w-10 h-10 rounded-2xl bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 flex items-center justify-center font-bold"
          >
            ←
          </button>
          <div className="text-sm font-black text-[#2D5A27] dark:text-[#A1C954]">
            📖 학습 단어장 ({currentIndex + 1} / {wordList.length})
          </div>
          <div className="flex gap-1">
            <button
              onClick={() => setViewMode(viewMode === 'card' ? 'list' : 'card')}
              className="px-3 py-1.5 rounded-xl text-xs font-bold bg-[#FAF6EC] dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 text-[#5F8D4E]"
            >
              {viewMode === 'card' ? '리스트 보기' : '카드 보기'}
            </button>
          </div>
        </div>

        {viewMode === 'card' ? (
          /* 카드 뷰 */
          <div className="space-y-4">
            <div className="bg-white dark:bg-[#1D2A1F] border border-[#F0E9D7] dark:border-[#2E4232] rounded-3xl overflow-hidden shadow-md">
              {/* 이미지 */}
              <div className="relative h-48 w-full bg-stone-100 overflow-hidden">
                <img
                  src={currentWord.imageUrl}
                  alt={currentWord.word}
                  className="w-full h-full object-cover"
                />
                <button
                  onClick={() => speakWord(currentWord.word)}
                  className="absolute bottom-3 right-3 px-3 py-1.5 rounded-full bg-black/60 text-white text-xs font-bold flex items-center gap-1 backdrop-blur-sm"
                >
                  <span>🔊</span> 발음 듣기
                </button>
              </div>

              {/* 단어 상세 */}
              <div className="p-6 space-y-4">
                <div className="text-center space-y-1">
                  <h1 className="text-3xl font-black text-[#2D5A27] dark:text-[#A1C954]">
                    {currentWord.word}
                  </h1>
                  <p className="text-xs text-stone-400 font-mono">
                    {currentWord.phonetic} • {currentWord.partOfSpeech}
                  </p>
                </div>

                {/* 뜻 (가리기 기능 지원) */}
                <div 
                  onClick={() => setHideMeaning(!hideMeaning)}
                  className="p-4 rounded-2xl bg-[#FAF6EC] dark:bg-[#162418] border border-[#EADBCA] dark:border-[#28382a] text-center cursor-pointer transition-all"
                >
                  <div className="text-[10px] text-[#5F8D4E] font-bold mb-1">
                    {hideMeaning ? "💡 탭하여 뜻 확인하기" : "한국어 의미"}
                  </div>
                  <div className={`text-lg font-bold text-[#2C3E2D] dark:text-[#EDECE4] ${hideMeaning ? 'blur-sm select-none' : ''}`}>
                    {currentWord.meaning}
                  </div>
                </div>

                {/* 예문 및 해석 */}
                <div className="space-y-1 text-xs p-3 rounded-2xl bg-stone-50 dark:bg-stone-800/40">
                  <p className="font-semibold text-stone-800 dark:text-stone-200">
                    "{currentWord.exampleSentence}"
                  </p>
                  <p className="text-stone-500 dark:text-stone-400">
                    {currentWord.exampleTranslation}
                  </p>
                </div>

                {/* 유의어 / 반의어 */}
                <div className="flex justify-between text-xs text-stone-500 pt-2 border-t border-stone-100 dark:border-stone-800">
                  <div>
                    <span className="font-bold text-[#5F8D4E]">유의어: </span>
                    {currentWord.synonyms?.join(', ')}
                  </div>
                  <div>
                    <span className="font-bold text-[#C24A4A]">반의어: </span>
                    {currentWord.antonyms?.join(', ')}
                  </div>
                </div>
              </div>
            </div>

            <button
              onClick={handleNext}
              className="w-full py-4 bg-[#2D5A27] hover:bg-[#23471f] text-white font-extrabold text-base rounded-2xl shadow-lg active:scale-98 transition-all flex items-center justify-center gap-2"
            >
              <span>{currentIndex === wordList.length - 1 ? '🎉 학습 완료하기' : '다음 단어 외우기'}</span>
              <span>(☀️ +1 획득)</span>
            </button>
          </div>
        ) : (
          /* 리스트 뷰 */
          <div className="space-y-3">
            {wordList.map((w, idx) => (
              <div
                key={w.id}
                className="p-4 rounded-2xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 flex items-center justify-between"
              >
                <div>
                  <div className="flex items-center gap-2">
                    <span className="font-black text-base text-[#2D5A27] dark:text-[#A1C954]">
                      {w.word}
                    </span>
                    <span className="text-[11px] text-stone-400">{w.phonetic}</span>
                  </div>
                  <div className="text-xs text-stone-600 dark:text-stone-300 font-medium">
                    {w.meaning}
                  </div>
                </div>
                <button
                  onClick={() => speakWord(w.word)}
                  className="w-8 h-8 rounded-full bg-stone-100 dark:bg-stone-800 text-sm flex items-center justify-center"
                >
                  🔊
                </button>
              </div>
            ))}
            <button
              onClick={() => {
                triggerSunlightAnimation(wordList.length);
                saveDailyProgress({ ...dailyProgress, studyCompleted: true });
                alert("🎉 리스트 학습을 완료했습니다!");
                setCurrentTab('home');
              }}
              className="w-full py-4 bg-[#2D5A27] text-white font-extrabold rounded-2xl shadow-md"
            >
              리스트 학습 완료 인정 (☀️ +{wordList.length})
            </button>
          </div>
        )}
      </div>
    );
  };

  // ============================================================================
  // [화면 4: 훈련 모드 선택 화면]
  // ============================================================================
  const TrainSelectScreen = () => {
    return (
      <div className="p-5 pb-24 space-y-5 animate-fadeIn">
        <div className="flex items-center justify-between">
          <button
            onClick={() => setCurrentTab('home')}
            className="w-10 h-10 rounded-2xl bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 flex items-center justify-center font-bold"
          >
            ←
          </button>
          <div className="text-base font-black text-[#2D5A27] dark:text-[#A1C954]">
            ⚡ 훈련 단어장 선택
          </div>
          <div className="w-10" />
        </div>

        <p className="text-xs text-stone-500 dark:text-stone-400 text-center">
          오늘 배운 단어를 3가지 인터랙티브 훈련 방식으로 머릿속에 각인하세요!
        </p>

        <div className="space-y-4 pt-2">
          {/* 1. 플래시카드 */}
          <div
            onClick={() => setCurrentTab('flashcard')}
            className="p-5 rounded-3xl bg-white dark:bg-[#1D2A1F] border-2 border-stone-200 dark:border-stone-800 hover:border-[#5F8D4E] transition-all cursor-pointer shadow-sm flex items-center gap-4 active:scale-98"
          >
            <div className="w-14 h-14 rounded-2xl bg-[#5F8D4E]/20 text-[#5F8D4E] text-2xl flex items-center justify-center">
              🃏
            </div>
            <div className="flex-1">
              <div className="font-bold text-base text-[#2C3E2D] dark:text-[#EDECE4]">
                플래시카드 (Flashcards)
              </div>
              <div className="text-xs text-stone-500 dark:text-stone-400">
                카드를 탭하여 앞뒤를 뒤집으며 직관적인 인출 기억 훈련
              </div>
            </div>
            <div className="text-stone-400 font-bold">→</div>
          </div>

          {/* 2. 워드 리콜 (기존 4지선다 개편) */}
          <div
            onClick={() => setCurrentTab('word_recall')}
            className="p-5 rounded-3xl bg-[#FAF6EC] dark:bg-[#203624] border-2 border-[#2D5A27] dark:border-[#A1C954] transition-all cursor-pointer shadow-md flex items-center gap-4 active:scale-98"
          >
            <div className="w-14 h-14 rounded-2xl bg-[#2D5A27] text-white text-2xl flex items-center justify-center">
              🧠
            </div>
            <div className="flex-1">
              <div className="font-black text-base text-[#2D5A27] dark:text-[#A1C954]">
                워드 리콜 (Word Recall)
              </div>
              <div className="text-xs text-[#5F8D4E] dark:text-[#9DB3A0] font-medium">
                4개 보기 중 올바른 의미를 3초 안에 고르는 초고속 회상 퀴즈
              </div>
            </div>
            <div className="text-[#2D5A27] dark:text-[#A1C954] font-bold">→</div>
          </div>

          {/* 3. 스펠링 훈련 */}
          <div
            onClick={() => setCurrentTab('spelling')}
            className="p-5 rounded-3xl bg-white dark:bg-[#1D2A1F] border-2 border-stone-200 dark:border-stone-800 hover:border-[#5F8D4E] transition-all cursor-pointer shadow-sm flex items-center gap-4 active:scale-98"
          >
            <div className="w-14 h-14 rounded-2xl bg-[#A1C954]/20 text-[#5F8D4E] text-2xl flex items-center justify-center">
              ✍️
            </div>
            <div className="flex-1">
              <div className="font-bold text-base text-[#2C3E2D] dark:text-[#EDECE4]">
                스펠링 훈련 (Spelling)
              </div>
              <div className="text-xs text-stone-500 dark:text-stone-400">
                가상 키보드로 철자를 하나씩 직접 타이핑하는 완벽 암기
              </div>
            </div>
            <div className="text-stone-400 font-bold">→</div>
          </div>
        </div>
      </div>
    );
  };

  // ============================================================================
  // [화면 5: 워드 리콜 (Word Recall) - 기존 4지선다 퀴즈 개편]
  // ============================================================================
  const WordRecallScreen = () => {
    const wordList = todayStudyWords;
    const [currentIndex, setCurrentIndex] = useState(0);
    const [selectedOption, setSelectedOption] = useState(null);
    const [isAnswered, setIsAnswered] = useState(false);

    const currentWord = wordList[currentIndex] || wordList[0];

    // 4지선다 보기 생성
    const options = useMemo(() => {
      if (!currentWord) return [];
      const correct = currentWord.meaning;
      const others = words
        .filter(w => w.id !== currentWord.id)
        .map(w => w.meaning)
        .sort(() => Math.random() - 0.5)
        .slice(0, 3);
      return [correct, ...others].sort(() => Math.random() - 0.5);
    }, [currentWord, words]);

    const handleSelect = (opt) => {
      if (isAnswered) return;
      setSelectedOption(opt);
      setIsAnswered(true);

      const isCorrect = opt === currentWord.meaning;
      if (isCorrect) {
        triggerSunlightAnimation(1); // 맞히면 햇살 1 획득!
      }

      setTimeout(() => {
        if (currentIndex < wordList.length - 1) {
          setCurrentIndex(currentIndex + 1);
          setSelectedOption(null);
          setIsAnswered(false);
        } else {
          saveDailyProgress({ ...dailyProgress, recallCompleted: true });
          alert("🎉 워드 리콜 훈련을 완료했습니다! (햇살 획득 완료)");
          setCurrentTab('home');
        }
      }, 1000);
    };

    return (
      <div className="p-5 pb-24 space-y-6 animate-fadeIn">
        <div className="flex items-center justify-between">
          <button
            onClick={() => setCurrentTab('train_select')}
            className="w-10 h-10 rounded-2xl bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 flex items-center justify-center font-bold"
          >
            ←
          </button>
          <div className="text-base font-black text-[#2D5A27] dark:text-[#A1C954]">
            🧠 워드 리콜 ({currentIndex + 1} / {wordList.length})
          </div>
          <button
            onClick={() => speakWord(currentWord?.word || '')}
            className="w-10 h-10 rounded-2xl bg-[#FAF6EC] dark:bg-[#1D2A1F] text-[#2D5A27] dark:text-[#A1C954] flex items-center justify-center font-bold"
          >
            🔊
          </button>
        </div>

        {/* 문제 카드 */}
        <div className="p-8 rounded-3xl bg-white dark:bg-[#1D2A1F] border border-[#F0E9D7] dark:border-[#2E4232] text-center space-y-2 shadow-sm">
          <div className="text-xs text-stone-400 font-bold uppercase tracking-wider">
            단어 인출 훈련
          </div>
          <div className="text-3xl font-black text-[#2D5A27] dark:text-[#A1C954]">
            {currentWord?.word}
          </div>
          <div className="text-xs text-stone-400 font-mono">
            {currentWord?.phonetic}
          </div>
        </div>

        {/* 4개 보기 선택지 (둥글둥글 카드) */}
        <div className="space-y-3">
          {options.map((opt, idx) => {
            const isSelected = selectedOption === opt;
            const isCorrect = opt === currentWord?.meaning;

            let cardStyle = "bg-white dark:bg-[#1D2A1F] border-stone-200 dark:border-stone-800 text-[#2C3E2D] dark:text-[#EDECE4]";
            if (isAnswered) {
              if (isCorrect) {
                cardStyle = "bg-[#E8F5E9] dark:bg-[#1b3d22] border-[#2D5A27] dark:border-[#A1C954] text-[#2D5A27] dark:text-[#A1C954] scale-[1.02] shadow-md";
              } else if (isSelected) {
                cardStyle = "bg-[#FFEBEE] dark:bg-[#3d1b1b] border-[#C24A4A] text-[#C24A4A] animate-shake";
              }
            }

            return (
              <button
                key={idx}
                disabled={isAnswered}
                onClick={() => handleSelect(opt)}
                className={`w-full py-4 px-5 rounded-2xl border-2 font-bold text-sm text-left transition-all flex items-center justify-between ${cardStyle} active:scale-98`}
              >
                <div className="flex items-center gap-3">
                  <span className="w-7 h-7 rounded-full bg-stone-100 dark:bg-stone-800 flex items-center justify-center text-xs font-bold">
                    {idx + 1}
                  </span>
                  <span>{opt}</span>
                </div>
                {isAnswered && isCorrect && <span className="text-base">✅</span>}
                {isAnswered && isSelected && !isCorrect && <span className="text-base">❌</span>}
              </button>
            );
          })}
        </div>
      </div>
    );
  };

  // ============================================================================
  // [화면 6: 플래시카드 훈련]
  // ============================================================================
  const FlashcardScreen = () => {
    const wordList = todayStudyWords;
    const [currentIndex, setCurrentIndex] = useState(0);
    const [isFlipped, setIsFlipped] = useState(false);

    const currentWord = wordList[currentIndex] || wordList[0];

    const handleNext = (known) => {
      triggerSunlightAnimation(1);
      setIsFlipped(false);
      if (currentIndex < wordList.length - 1) {
        setCurrentIndex(currentIndex + 1);
      } else {
        saveDailyProgress({ ...dailyProgress, flashcardCompleted: true });
        alert("🎉 플래시카드 훈련을 완료했습니다! (햇살 획득 완료)");
        setCurrentTab('home');
      }
    };

    return (
      <div className="p-5 pb-24 space-y-6 animate-fadeIn">
        <div className="flex items-center justify-between">
          <button
            onClick={() => setCurrentTab('train_select')}
            className="w-10 h-10 rounded-2xl bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 flex items-center justify-center font-bold"
          >
            ←
          </button>
          <div className="text-base font-black text-[#2D5A27] dark:text-[#A1C954]">
            🃏 플래시카드 ({currentIndex + 1} / {wordList.length})
          </div>
          <div className="w-10" />
        </div>

        {/* 플립 카드 */}
        <div
          onClick={() => setIsFlipped(!isFlipped)}
          className="min-h-[300px] p-8 rounded-3xl bg-white dark:bg-[#1D2A1F] border-2 border-[#EADBCA] dark:border-[#2E4232] shadow-md flex flex-col items-center justify-center text-center cursor-pointer transition-all transform active:scale-98"
        >
          <div className="text-[11px] text-stone-400 font-bold mb-4">
            탭하여 카드 뒤집기 (앞: 영단어 / 뒤: 한국어 뜻)
          </div>
          {!isFlipped ? (
            <div className="space-y-2">
              <div className="text-4xl font-black text-[#2D5A27] dark:text-[#A1C954]">
                {currentWord?.word}
              </div>
              <div className="text-xs text-stone-400 font-mono">
                {currentWord?.phonetic}
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="text-2xl font-black text-[#5F8D4E] dark:text-[#EDECE4]">
                {currentWord?.meaning}
              </div>
              <p className="text-xs text-stone-500 dark:text-stone-400 max-w-xs">
                "{currentWord?.exampleSentence}"
              </p>
            </div>
          )}
        </div>

        {/* 응답 버튼 */}
        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => handleNext(false)}
            className="py-4 rounded-2xl bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 font-bold text-sm"
          >
            몰라요 💧
          </button>
          <button
            onClick={() => handleNext(true)}
            className="py-4 rounded-2xl bg-[#2D5A27] text-white font-bold text-sm shadow-md"
          >
            알아요 ☀️ (+1)
          </button>
        </div>
      </div>
    );
  };

  // ============================================================================
  // [화면 7: 스펠링 훈련]
  // ============================================================================
  const SpellingScreen = () => {
    const wordList = todayStudyWords;
    const [currentIndex, setCurrentIndex] = useState(0);
    const [inputVal, setInputVal] = useState('');
    const currentWord = wordList[currentIndex] || wordList[0];

    const handleSubmit = (e) => {
      e.preventDefault();
      if (inputVal.trim().toLowerCase() === currentWord.word.toLowerCase()) {
        triggerSunlightAnimation(1);
        alert("정답입니다! 👏");
        setInputVal('');
        if (currentIndex < wordList.length - 1) {
          setCurrentIndex(currentIndex + 1);
        } else {
          saveDailyProgress({ ...dailyProgress, spellingCompleted: true });
          alert("🎉 스펠링 훈련을 모두 마쳤습니다! (햇살 획득 완료)");
          setCurrentTab('home');
        }
      } else {
        alert(`아쉬워요! 정답은 [ ${currentWord.word} ] 입니다. 다시 시도해 보세요.`);
      }
    };

    return (
      <div className="p-5 pb-24 space-y-6 animate-fadeIn">
        <div className="flex items-center justify-between">
          <button
            onClick={() => setCurrentTab('train_select')}
            className="w-10 h-10 rounded-2xl bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 flex items-center justify-center font-bold"
          >
            ←
          </button>
          <div className="text-base font-black text-[#2D5A27] dark:text-[#A1C954]">
            ✍️ 스펠링 훈련 ({currentIndex + 1} / {wordList.length})
          </div>
          <div className="w-10" />
        </div>

        <div className="p-6 rounded-3xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 text-center space-y-2">
          <div className="text-xs text-stone-400 font-bold">의미를 보고 철자를 입력하세요</div>
          <div className="text-2xl font-black text-[#5F8D4E] dark:text-[#A1C954]">
            {currentWord?.meaning}
          </div>
          <div className="text-xs text-stone-400 font-mono">
            힌트 길이: {currentWord?.word.length}글자
          </div>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text"
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            placeholder="단어 철자 입력 (예: cherish)"
            className="w-full py-4 px-5 rounded-2xl bg-white dark:bg-[#1D2A1F] border-2 border-[#5F8D4E] text-[#2C3E2D] dark:text-[#EDECE4] text-center text-lg font-bold outline-none focus:ring-4 focus:ring-[#A1C954]/30"
          />
          <button
            type="submit"
            className="w-full py-4 bg-[#2D5A27] text-white font-extrabold text-base rounded-2xl shadow-md"
          >
            정답 제출하고 다음 단어로
          </button>
        </form>
      </div>
    );
  };

  // ============================================================================
  // [화면 8: 에빙하우스 망각곡선 자동 복습]
  // ============================================================================
  const ReviewScreen = () => {
    const [ratio, setRatio] = useState(1.0); // 1.0, 0.7, 0.5, 0.3
    const [isReviewing, setIsReviewing] = useState(false);
    const [reviewWords, setReviewWords] = useState([]);
    const [reviewIndex, setReviewIndex] = useState(0);

    const startReview = () => {
      const sampled = sampleWordsByRatio(dueReviewWords, ratio);
      if (sampled.length === 0) {
        alert("현재 복습할 단어가 없습니다! 먼저 오늘 단어를 학습해 보세요.");
        return;
      }
      setReviewWords(sampled);
      setReviewIndex(0);
      setIsReviewing(true);
    };

    const handleWordResult = (isSuccess) => {
      triggerSunlightAnimation(1); // 복습에서도 무조건 단어당 햇살 1 지급!
      const current = reviewWords[reviewIndex];
      const updated = updateWordAfterReview(current, isSuccess);

      // 전체 단어 상태 갱신 및 저장
      const updatedAll = words.map(w => w.id === updated.id ? updated : w);
      setWords(updatedAll);
      saveWords(updatedAll);

      if (reviewIndex < reviewWords.length - 1) {
        setReviewIndex(reviewIndex + 1);
      } else {
        alert("🎉 에빙하우스 망각곡선 복습을 성공적으로 마쳤습니다! 복습 주기가 연장되었습니다.");
        setIsReviewing(false);
        setCurrentTab('home');
      }
    };

    if (isReviewing && reviewWords.length > 0) {
      const current = reviewWords[reviewIndex];
      return (
        <div className="p-5 pb-24 space-y-6 animate-fadeIn">
          <div className="flex items-center justify-between">
            <button
              onClick={() => setIsReviewing(false)}
              className="w-10 h-10 rounded-2xl bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 flex items-center justify-center font-bold"
            >
              ←
            </button>
            <div className="text-base font-black text-[#2D5A27] dark:text-[#A1C954]">
              🔄 망각곡선 복습 ({reviewIndex + 1} / {reviewWords.length})
            </div>
            <div className="w-10" />
          </div>

          <div className="p-8 rounded-3xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 text-center space-y-3 shadow-md">
            <span className="px-3 py-1 bg-[#5F8D4E]/20 text-[#5F8D4E] text-xs font-bold rounded-full">
              {current.repetitionStage}차 복습 주기 단어
            </span>
            <div className="text-3xl font-black text-[#2D5A27] dark:text-[#A1C954]">
              {current.word}
            </div>
            <div className="text-lg font-bold text-stone-700 dark:text-stone-200 pt-2 border-t border-stone-100 dark:border-stone-800">
              {current.meaning}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <button
              onClick={() => handleWordResult(false)}
              className="py-4 bg-[#C24A4A] text-white font-bold text-sm rounded-2xl shadow-md"
            >
              틀렸어요 (내일 다시)
            </button>
            <button
              onClick={() => handleWordResult(true)}
              className="py-4 bg-[#2D5A27] text-white font-bold text-sm rounded-2xl shadow-md"
            >
              기억나요! ☀️ (+1)
            </button>
          </div>
        </div>
      );
    }

    return (
      <div className="p-5 pb-24 space-y-6 animate-fadeIn">
        <div className="flex items-center justify-between">
          <button
            onClick={() => setCurrentTab('home')}
            className="w-10 h-10 rounded-2xl bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 flex items-center justify-center font-bold"
          >
            ←
          </button>
          <div className="text-base font-black text-[#2D5A27] dark:text-[#A1C954]">
            🔄 에빙하우스 망각곡선 복습
          </div>
          <div className="w-10" />
        </div>

        <div className="p-6 rounded-3xl bg-[#FAF6EC] dark:bg-[#162418] border border-[#EADBCA] dark:border-[#28382a] space-y-2">
          <div className="font-bold text-sm text-[#2D5A27] dark:text-[#A1C954]">
            🧠 망각곡선 3대 주기 시스템
          </div>
          <p className="text-xs text-stone-500 dark:text-stone-400 leading-relaxed">
            단어를 외우고 <strong>1일 후 ➔ 7일 후 ➔ 30일 후</strong>에 자동으로 출제됩니다.
            복습에 성공하면 주기가 늘어나 영구 기억으로 전환됩니다!
          </p>
        </div>

        {/* 복습 분량 퍼센티지 선택 */}
        <div className="space-y-3">
          <label className="block text-sm font-bold text-[#2C3E2D] dark:text-[#EDECE4]">
            복습 분량 선택 (랜덤 추출)
          </label>
          <div className="grid grid-cols-4 gap-2">
            {[
              { label: '30%', val: 0.3 },
              { label: '50%', val: 0.5 },
              { label: '70%', val: 0.7 },
              { label: '전체', val: 1.0 }
            ].map(item => (
              <button
                key={item.label}
                onClick={() => setRatio(item.val)}
                className={`py-3 rounded-2xl font-bold text-sm transition-all ${
                  ratio === item.val
                    ? 'bg-[#2D5A27] text-white shadow-md'
                    : 'bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 text-stone-700 dark:text-stone-300'
                }`}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 flex justify-between items-center text-sm font-bold">
          <span>현재 복습 대상 단어</span>
          <span className="text-[#2D5A27] dark:text-[#A1C954]">{dueReviewWords.length}단어</span>
        </div>

        <button
          onClick={startReview}
          className="w-full py-4 bg-[#2D5A27] hover:bg-[#23471f] text-white font-extrabold text-base rounded-2xl shadow-lg active:scale-98 transition-all flex items-center justify-center gap-2"
        >
          <span>⚡</span>
          <span>선택한 분량으로 복습 시작하기</span>
        </button>
      </div>
    );
  };

  // ============================================================================
  // [화면 9: 보카 트리 (Voca Tree) 7단계 성장 화면]
  // ============================================================================
  const VocaTreeScreen = () => {
    return (
      <div className="p-5 pb-24 space-y-6 animate-fadeIn text-center">
        <div className="flex items-center justify-between">
          <button
            onClick={() => setCurrentTab('home')}
            className="w-10 h-10 rounded-2xl bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300 flex items-center justify-center font-bold"
          >
            ←
          </button>
          <div className="text-base font-black text-[#2D5A27] dark:text-[#A1C954]">
            🌳 나의 보카 트리
          </div>
          <div className="px-3 py-1 bg-[#A1C954]/20 text-[#5F8D4E] dark:text-[#A1C954] text-xs font-extrabold rounded-full">
            ☀️ {treeInfo.sunlight} 햇살
          </div>
        </div>

        {/* 거대 트리 일러스트 영역 */}
        <div className="p-8 rounded-3xl bg-gradient-to-b from-[#FAF6EC] to-[#E8F5E9] dark:from-[#162418] dark:to-[#1D2A1F] border border-[#EADBCA] dark:border-[#2E4232] shadow-sm space-y-3">
          <div className="text-7xl animate-bounce duration-1000 select-none">
            {treeInfo.currentStage.emoji}
          </div>
          <h2 className="text-2xl font-black text-[#2D5A27] dark:text-[#A1C954]">
            Lv.{treeInfo.currentStage.level} {treeInfo.currentStage.name}
          </h2>
          <p className="text-xs text-stone-600 dark:text-stone-300 font-medium">
            "{treeInfo.currentStage.desc}"
          </p>

          {/* 성장 게이지 바 */}
          <div className="pt-4 space-y-1.5 text-left">
            <div className="flex justify-between text-xs font-bold text-stone-600 dark:text-stone-400">
              <span>다음 레벨 ({treeInfo.nextStage?.name || '최대'})</span>
              <span>{treeInfo.progressPercent}%</span>
            </div>
            <div className="w-full h-3 bg-stone-200 dark:bg-stone-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-[#5F8D4E] to-[#A1C954] transition-all duration-500"
                style={{ width: `${treeInfo.progressPercent}%` }}
              />
            </div>
            {treeInfo.nextStage && (
              <div className="text-[11px] text-stone-400 text-center pt-1">
                다음 성장까지 <strong>{treeInfo.remainingSunlight} 햇살</strong> 필요!
              </div>
            )}
          </div>
        </div>

        {/* 7단계 전체 레벨 로드맵 */}
        <div className="space-y-2 text-left">
          <div className="font-bold text-sm text-[#2C3E2D] dark:text-[#EDECE4] px-1">
            🌿 보카 트리 7단계 성장 단계표
          </div>
          <div className="space-y-2">
            {TREE_STAGES.map(st => {
              const isAchieved = treeInfo.sunlight >= st.minSunlight;
              const isCurrent = treeInfo.currentStage.level === st.level;
              return (
                <div
                  key={st.level}
                  className={`p-3 rounded-2xl border flex items-center justify-between ${
                    isCurrent
                      ? 'bg-[#A1C954]/20 border-[#5F8D4E] text-[#2D5A27] dark:text-[#A1C954]'
                      : isAchieved
                      ? 'bg-white dark:bg-[#1D2A1F] border-stone-200 dark:border-stone-800 text-stone-700 dark:text-stone-300'
                      : 'bg-stone-50 dark:bg-stone-900 border-dashed border-stone-300 dark:border-stone-800 text-stone-400'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-xl">{st.emoji}</span>
                    <div>
                      <div className="font-bold text-xs">
                        Lv.{st.level} {st.name}
                      </div>
                      <div className="text-[10px] text-stone-400">
                        {st.minSunlight} ~ {st.maxSunlight === 999999 ? '무제한' : st.maxSunlight} 햇살
                      </div>
                    </div>
                  </div>
                  {isCurrent && <span className="text-xs font-black px-2 py-0.5 rounded-full bg-[#2D5A27] text-white">현재</span>}
                  {isAchieved && !isCurrent && <span className="text-xs text-[#5F8D4E]">달성 ✓</span>}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    );
  };

  // ============================================================================
  // [좌측 사이드 드로어 메뉴 (design_guide/좌측 팝업.png)]
  // ============================================================================
  const SideDrawer = () => {
    if (!isDrawerOpen) return null;

    return (
      <div className="fixed inset-0 z-50 flex animate-fadeIn">
        {/* 오버레이 배경 */}
        <div
          onClick={() => setIsDrawerOpen(false)}
          className="fixed inset-0 bg-black/50 backdrop-blur-sm"
        />

        {/* 드로어 컨텐츠 본체 */}
        <div className="relative w-72 max-w-[80vw] h-full bg-[#FAF6EC] dark:bg-[#162418] border-r border-[#EADBCA] dark:border-[#28382a] p-6 flex flex-col justify-between shadow-2xl z-10 animate-slideRight">
          <div className="space-y-6">
            {/* 드로어 헤더 */}
            <div className="flex items-center justify-between pb-4 border-b border-stone-200 dark:border-stone-800">
              <div className="font-black text-xl text-[#2D5A27] dark:text-[#A1C954] flex items-center gap-2">
                <span>🌱</span> vocahigh
              </div>
              <button
                onClick={() => setIsDrawerOpen(false)}
                className="w-8 h-8 rounded-full bg-stone-200 dark:bg-stone-800 text-stone-600 dark:text-stone-300 flex items-center justify-center font-bold"
              >
                ✕
              </button>
            </div>

            {/* 1. 내 정보 섹션 (design_guide/좌측 팝업.png) */}
            <div className="space-y-2">
              <div className="text-xs font-bold text-[#5F8D4E] dark:text-[#A1C954] uppercase tracking-wider">
                내 정보
              </div>
              <div className="space-y-1 text-sm font-medium text-[#2C3E2D] dark:text-[#EDECE4]">
                <button
                  onClick={() => { setIsDrawerOpen(false); setCurrentTab('study'); }}
                  className="w-full text-left p-2.5 rounded-xl hover:bg-black/5 dark:hover:bg-white/5 flex items-center gap-2"
                >
                  <span>🏃</span> 이어 학습하기
                </button>
                <button
                  onClick={() => { setIsDrawerOpen(false); setModalType('stats'); }}
                  className="w-full text-left p-2.5 rounded-xl hover:bg-black/5 dark:hover:bg-white/5 flex items-center gap-2"
                >
                  <span>📊</span> 학습 현황
                </button>
                <button
                  onClick={() => { setIsDrawerOpen(false); setModalType('ranking'); }}
                  className="w-full text-left p-2.5 rounded-xl hover:bg-black/5 dark:hover:bg-white/5 flex items-center gap-2"
                >
                  <span>🏆</span> 학습 랭킹
                </button>
                <button
                  onClick={() => { setIsDrawerOpen(false); setCurrentTab('tree'); }}
                  className="w-full text-left p-2.5 rounded-xl hover:bg-black/5 dark:hover:bg-white/5 flex items-center gap-2 font-bold text-[#2D5A27] dark:text-[#A1C954]"
                >
                  <span>🌳</span> 보카 트리 (햇살 ☀️ {treeInfo.sunlight})
                </button>
              </div>
            </div>

            {/* 2. 단어장 섹션 */}
            <div className="space-y-2">
              <div className="text-xs font-bold text-[#5F8D4E] dark:text-[#A1C954] uppercase tracking-wider">
                단어장
              </div>
              <button
                onClick={() => { setIsDrawerOpen(false); setCurrentTab('curriculum_setup'); }}
                className="w-full text-left p-2.5 rounded-xl hover:bg-black/5 dark:hover:bg-white/5 flex items-center gap-2 text-sm font-medium text-[#2C3E2D] dark:text-[#EDECE4]"
              >
                <span>📚</span> 커리큘럼 보기 / 변경
              </button>
            </div>

            {/* 3. 도움말 및 기능 설명 */}
            <div className="space-y-2">
              <div className="text-xs font-bold text-[#5F8D4E] dark:text-[#A1C954] uppercase tracking-wider">
                기능 설명
              </div>
              <button
                onClick={() => { setIsDrawerOpen(false); setModalType('guide'); }}
                className="w-full text-left p-2.5 rounded-xl hover:bg-black/5 dark:hover:bg-white/5 flex items-center gap-2 text-sm font-medium text-[#2C3E2D] dark:text-[#EDECE4]"
              >
                <span>💡</span> 에빙하우스 망각곡선 원리
              </button>
              <button
                onClick={startTutorial}
                className="w-full text-left p-2.5 rounded-xl bg-[#2D5A27] text-white flex items-center gap-2 text-sm font-bold shadow-md hover:bg-[#23471f]"
              >
                <span>🎓</span> 기능 튜토리얼 (체험 모드)
              </button>
            </div>
          </div>

          {/* 하단 버전 */}
          <div className="text-center text-[10px] text-stone-400">
            vocahigh v3.0 • 교육용 에듀테크
          </div>
        </div>
      </div>
    );
  };

  // ============================================================================
  // [인터랙티브 기능 튜토리얼 오버레이 & 스포트라이트]
  // ============================================================================
  const TutorialOverlay = () => {
    if (!isTutorialActive) return null;

    return (
      <div className="fixed inset-0 z-50 pointer-events-auto">
        {/* 전체 검정 반투명 오버레이 박스 */}
        <div className="absolute inset-0 bg-black/75 backdrop-blur-[2px]" />

        {/* 상단 튜토리얼 샌드박스 알림 뱃지 및 종료 버튼 */}
        <div className="absolute top-4 left-4 right-4 z-50 flex items-center justify-between">
          <div className="px-3 py-1.5 rounded-full bg-[#A1C954] text-[#121B13] font-black text-xs shadow-lg flex items-center gap-1.5">
            <span>🛡️</span>
            <span>체험 튜토리얼 (기록은 저장되지 않아요)</span>
          </div>
          <button
            onClick={exitTutorial}
            className="px-3 py-1.5 rounded-full bg-white/20 hover:bg-white/30 text-white font-bold text-xs"
          >
            튜토리얼 나가기 ✕
          </button>
        </div>

        {/* 스포트라이트 단계별 타깃 안내 모달 */}
        <div className="absolute bottom-8 left-6 right-6 z-50 p-6 rounded-3xl bg-white dark:bg-[#1D2A1F] border-4 border-[#A1C954] shadow-2xl space-y-4 animate-scaleUp">
          <div className="flex items-center gap-2">
            <span className="w-7 h-7 rounded-full bg-[#2D5A27] text-white font-black text-xs flex items-center justify-center">
              {tutorialStep}
            </span>
            <h3 className="font-black text-base text-[#2D5A27] dark:text-[#A1C954]">
              {tutorialStep === 1 && "1단계: 커리큘럼 생성 & 출석 기준 체험"}
              {tutorialStep === 2 && "2단계: 워드 리콜 퀴즈로 햇살 ☀️+1 얻기"}
              {tutorialStep === 3 && "3단계: 오늘의 출석 도장 쾅! 확인하기"}
            </h3>
          </div>

          <p className="text-xs text-stone-600 dark:text-stone-300 leading-relaxed">
            {tutorialStep === 1 && "보카하이에 오신 것을 환영합니다! 커리큘럼에서 원하는 단어장과 출석 인정 체크박스를 선택하는 방법을 배웁니다."}
            {tutorialStep === 2 && "단어 카드를 보고 직관적으로 의미를 떠올리는 '워드 리콜'을 풀면 단어 1개당 무조건 햇살 1개가 팡팡 터져요!"}
            {tutorialStep === 3 && "설정한 목표를 마치면 기분 좋은 출석 도장이 날인됩니다. 지금 이 버튼만 누르실 수 있어요!"}
          </p>

          <button
            onClick={nextTutorialStep}
            className="w-full py-3.5 bg-[#2D5A27] hover:bg-[#23471f] text-white font-black text-sm rounded-2xl shadow-lg ring-4 ring-[#A1C954] animate-pulse"
          >
            {tutorialStep === 3 ? "튜토리얼 완료하고 시작하기 🚀" : "이해했어요! 다음 단계로 가기 →"}
          </button>
        </div>
      </div>
    );
  };

  // ============================================================================
  // [서브 모달 팝업: 학습 현황, 랭킹, 망각곡선 가이드]
  // ============================================================================
  const SubModal = () => {
    if (!modalType) return null;

    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn">
        <div className="w-full max-w-sm bg-white dark:bg-[#1D2A1F] border border-[#EADBCA] dark:border-[#2E4232] rounded-3xl p-6 shadow-2xl space-y-4">
          <div className="flex items-center justify-between pb-3 border-b border-stone-100 dark:border-stone-800">
            <h3 className="font-black text-lg text-[#2D5A27] dark:text-[#A1C954]">
              {modalType === 'stats' && '📊 나의 학습 현황'}
              {modalType === 'ranking' && '🏆 명예의 전당 (학습 랭킹)'}
              {modalType === 'guide' && '💡 에빙하우스 망각곡선 원리'}
            </h3>
            <button
              onClick={() => setModalType(null)}
              className="w-7 h-7 rounded-full bg-stone-100 dark:bg-stone-800 text-stone-600 dark:text-stone-300 flex items-center justify-center font-bold"
            >
              ✕
            </button>
          </div>

          {modalType === 'stats' && (
            <div className="space-y-3 text-sm">
              <div className="p-3 rounded-2xl bg-[#FAF6EC] dark:bg-[#162418] flex justify-between">
                <span>누적 외운 단어 수</span>
                <strong className="text-[#2D5A27] dark:text-[#A1C954]">{words.filter(w => w.repetitionStage > 0).length}개</strong>
              </div>
              <div className="p-3 rounded-2xl bg-[#FAF6EC] dark:bg-[#162418] flex justify-between">
                <span>보카 트리 누적 햇살</span>
                <strong className="text-[#5F8D4E]">☀️ {treeInfo.sunlight}</strong>
              </div>
              <div className="p-3 rounded-2xl bg-[#FAF6EC] dark:bg-[#162418] flex justify-between">
                <span>연속 출석일수 (Streak)</span>
                <strong>{dailyProgress.isAttendanceStamped ? '1일 연속 출석 중 🔥' : '오늘 출석 전'}</strong>
              </div>
            </div>
          )}

          {modalType === 'ranking' && (
            <div className="space-y-2 text-xs">
              {[
                { rank: 1, name: '민지 (열공중)', level: 'Lv.6 황금 지혜나무', words: '2,420단어' },
                { rank: 2, name: '준호 (수능만점)', level: 'Lv.5 보카 나무', words: '1,890단어' },
                { rank: 3, name: '서연 (토익마스터)', level: 'Lv.4 푸른 묘목', words: '980단어' },
                { rank: 4, name: '나 (학생 사용자)', level: `Lv.${treeInfo.currentStage.level} ${treeInfo.currentStage.name}`, words: `${treeInfo.sunlight}단어 (나)` }
              ].map(r => (
                <div key={r.rank} className={`p-3 rounded-xl flex items-center justify-between ${r.rank === 4 ? 'bg-[#A1C954]/20 font-bold text-[#2D5A27]' : 'bg-stone-50 dark:bg-stone-800'}`}>
                  <span>{r.rank}등 • {r.name}</span>
                  <span>{r.words}</span>
                </div>
              ))}
            </div>
          )}

          {modalType === 'guide' && (
            <div className="space-y-2 text-xs text-stone-600 dark:text-stone-300 leading-relaxed">
              <p>사람의 기억은 학습 직후부터 급격히 감소합니다 (에빙하우스의 망각곡선).</p>
              <p>보카하이는 단어를 외운 후 <strong>1일차, 7일차, 30일차</strong>의 결정적 타이밍에 복습을 제안하여 영구 기억으로 저장합니다.</p>
              <p className="text-[#C24A4A] font-bold">2일 동안 복습하지 않으면 단어가 누적 경고 상태로 전환되니 매일 조금씩 복습해 보세요!</p>
            </div>
          )}

          <button
            onClick={() => setModalType(null)}
            className="w-full py-3 bg-[#2D5A27] text-white font-bold text-sm rounded-xl shadow"
          >
            확인
          </button>
        </div>
      </div>
    );
  };

  // ============================================================================
  // [전체 렌더링: 스마트폰 모바일 뷰포트 & 상하단 바]
  // ============================================================================
  return (
    <div className={theme === 'dark' ? 'dark' : ''}>
      {/* 바깥 전체 배경 (자연 모티브 그라데이션) */}
      <div className="min-h-screen bg-stone-200 dark:bg-[#0c130d] text-stone-800 dark:text-stone-100 flex justify-center selection:bg-[#A1C954] selection:text-[#121B13]">
        
        {/* 중앙 스마트폰 전용 모바일 프레임 (Max Width: 430px) */}
        <div className="w-full max-w-[430px] min-h-screen bg-[#FAF6EC] dark:bg-[#121B13] border-x border-[#E5DEC9] dark:border-[#2A3A2C] flex flex-col relative shadow-2xl">
          
          {/* 플로팅 햇살 획득 파티클 이펙트 */}
          {floatingSun && (
            <div className="fixed top-16 left-1/2 -translate-x-1/2 z-50 px-4 py-2 bg-[#A1C954] text-[#121B13] font-black text-sm rounded-full shadow-2xl animate-bounce">
              ☀️ +1 햇살 획득!
            </div>
          )}

          {/* 상단 앱 헤더 (design_guide/메인 화면.png & 좌측 팝업.png) */}
          <header className="sticky top-0 z-30 h-14 bg-[#FAF6EC]/90 dark:bg-[#121B13]/90 backdrop-blur-md border-b border-[#EADBCA] dark:border-[#203022] px-4 flex items-center justify-between">
            {/* 좌측 햄버거 메뉴 버튼 */}
            <button
              onClick={() => setIsDrawerOpen(true)}
              className="w-10 h-10 rounded-2xl hover:bg-black/5 dark:hover:bg-white/5 flex items-center justify-center text-xl font-bold text-[#2D5A27] dark:text-[#A1C954]"
            >
              ☰
            </button>

            {/* 중앙 로고 */}
            <div
              onClick={() => setCurrentTab('home')}
              className="font-black text-lg text-[#2D5A27] dark:text-[#A1C954] cursor-pointer flex items-center gap-1.5"
            >
              <span>🌱</span> vocahigh
            </div>

            {/* 우측 다크/화이트 모드 토글 + 햇살 배지 */}
            <div className="flex items-center gap-2">
              <button
                onClick={toggleTheme}
                title={theme === 'light' ? '다크 모드로 전환' : '화이트 모드로 전환'}
                className="w-10 h-10 rounded-2xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 text-sm flex items-center justify-center shadow-sm"
              >
                {theme === 'light' ? '🌙' : '☀️'}
              </button>
            </div>
          </header>

          {/* 메인 컨텐츠 영역 */}
          <main className="flex-1 overflow-y-auto">
            {currentTab === 'curriculum_setup' && <CurriculumSetupScreen />}
            {currentTab === 'home' && <HomeScreen />}
            {currentTab === 'study' && <StudyVocabScreen />}
            {currentTab === 'train_select' && <TrainSelectScreen />}
            {currentTab === 'word_recall' && <WordRecallScreen />}
            {currentTab === 'flashcard' && <FlashcardScreen />}
            {currentTab === 'spelling' && <SpellingScreen />}
            {currentTab === 'review' && <ReviewScreen />}
            {currentTab === 'tree' && <VocaTreeScreen />}
            {currentTab === 'my' && <VocaTreeScreen />}
          </main>

          {/* 하단 고정 네비게이션 바 (Bottom Navigation) */}
          <nav className="fixed bottom-0 w-full max-w-[430px] h-16 bg-white/95 dark:bg-[#162217]/95 backdrop-blur-md border-t border-[#EADBCA] dark:border-[#203022] px-4 flex items-center justify-around z-30">
            <button
              onClick={() => setCurrentTab('home')}
              className={`flex flex-col items-center gap-1 text-[11px] font-bold ${
                currentTab === 'home' ? 'text-[#2D5A27] dark:text-[#A1C954]' : 'text-stone-400'
              }`}
            >
              <span className="text-lg">🏠</span>
              <span>홈</span>
            </button>
            <button
              onClick={() => setCurrentTab('study')}
              className={`flex flex-col items-center gap-1 text-[11px] font-bold ${
                currentTab === 'study' || currentTab === 'train_select' ? 'text-[#2D5A27] dark:text-[#A1C954]' : 'text-stone-400'
              }`}
            >
              <span className="text-lg">📖</span>
              <span>학습/훈련</span>
            </button>
            <button
              onClick={() => setCurrentTab('review')}
              className={`flex flex-col items-center gap-1 text-[11px] font-bold ${
                currentTab === 'review' ? 'text-[#2D5A27] dark:text-[#A1C954]' : 'text-stone-400'
              }`}
            >
              <span className="text-lg">🔄</span>
              <span>망각복습</span>
            </button>
            <button
              onClick={() => setCurrentTab('tree')}
              className={`flex flex-col items-center gap-1 text-[11px] font-bold ${
                currentTab === 'tree' ? 'text-[#2D5A27] dark:text-[#A1C954]' : 'text-stone-400'
              }`}
            >
              <span className="text-lg">🌳</span>
              <span>보카트리</span>
            </button>
            <button
              onClick={() => setIsDrawerOpen(true)}
              className="flex flex-col items-center gap-1 text-[11px] font-bold text-stone-400"
            >
              <span className="text-lg">👤</span>
              <span>내 정보</span>
            </button>
          </nav>

          {/* 좌측 사이드 드로어 */}
          <SideDrawer />

          {/* 서브 모달 팝업 */}
          <SubModal />

          {/* 기능 튜토리얼 스포트라이트 오버레이 */}
          <TutorialOverlay />
        </div>
      </div>
    </div>
  );
}
