# -*- coding: utf-8 -*-
"""
generate_index.py
- 커리큘럼 다중 관리: 커리큘럼 생성(CreateCurriculumScreen) & 나의 커리큘럼(MyCurriculumsScreen)
- 메인 홈 화면: 커리큘럼 미설정 시 생성 유도 카드 / 커리큘럼 설정 시 상단 커리큘럼 셀렉터 제공 (단어장 변경 버튼 삭제)
- 화면 하단 메뉴(네비게이션 탭 바) 완전 삭제
- 학습 단어장: 팝업에서 3가지 암기 모드(기본, 단어&뜻 보기 플립 토글, 단어만 보기) + 하나씩/리스트 선택
- 훈련 단어장: 팝업에서 3대 훈련 모드(플래시카드, 워드리콜, 스펠링) + 출제방향(영한/한영) + 타이머(5초/10초/무제한) + 하나씩/리스트 선택
"""

HTML_CONTENT = r'''<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>보카하이 (vocahigh) - 교육부 3000 단어 장기기억 시스템</title>
  
  <meta name="description" content="수파베이스(Supabase) 정식 회원가입 및 로그인 연동, 에빙하우스 망각곡선 복습, 워드 리콜 훈련, 보카 트리" />

  <!-- 웹 폰트: Inter & Noto Sans KR -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap" rel="stylesheet">

  <!-- 환경 설정 파일 로드 (GitHub 배포 시 설정 분리) -->
  <script src="./config.js"></script>

  <!-- Tailwind CSS 최신 CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          fontFamily: {
            sans: ['Inter', 'Noto Sans KR', 'sans-serif'],
          },
          colors: {
            forest: {
              DEFAULT: '#2D5A27',
              dark: '#1c3818',
              light: '#3d7835'
            },
            sage: {
              DEFAULT: '#5F8D4E',
              dark: '#4a6e3d'
            },
            limePoint: '#A1C954',
            warmCream: '#FAF6EC',
            coralAlert: '#C24A4A'
          },
          keyframes: {
            fadeIn: {
              '0%': { opacity: '0', transform: 'translateY(6px)' },
              '100%': { opacity: '1', transform: 'translateY(0)' },
            },
            scaleUp: {
              '0%': { opacity: '0', transform: 'scale(0.95)' },
              '100%': { opacity: '1', transform: 'scale(1)' },
            },
            slideRight: {
              '0%': { transform: 'translateX(-100%)' },
              '100%': { transform: 'translateX(0)' }
            },
            flipIn: {
              '0%': { transform: 'rotateY(90deg)', opacity: '0' },
              '100%': { transform: 'rotateY(0)', opacity: '1' }
            },
            shake: {
              '0%, 100%': { transform: 'translateX(0)' },
              '20%, 60%': { transform: 'translateX(-6px)' },
              '40%, 80%': { transform: 'translateX(6px)' }
            }
          },
          animation: {
            fadeIn: 'fadeIn 0.25s ease-out forwards',
            scaleUp: 'scaleUp 0.25s ease-out forwards',
            slideRight: 'slideRight 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards',
            flipIn: 'flipIn 0.3s ease-out forwards',
            shake: 'shake 0.4s ease-in-out forwards'
          }
        }
      }
    }
  </script>

  <!-- React 18 & ReactDOM 18 -->
  <script src="https://cdn.jsdelivr.net/npm/react@18.2.0/umd/react.production.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/react-dom@18.2.0/umd/react-dom.production.min.js"></script>

  <!-- Babel Standalone (JSX 컴파일러) -->
  <script src="https://cdn.jsdelivr.net/npm/@babel/standalone@7.24.4/babel.min.js"></script>

  <!-- Supabase JS Client v2 공식 CDN -->
  <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.39.8/dist/umd/supabase.min.js"></script>

  <style>
    ::-webkit-scrollbar {
      width: 6px;
      height: 6px;
    }
    ::-webkit-scrollbar-track {
      background: transparent;
    }
    ::-webkit-scrollbar-thumb {
      background: #c5beaa;
      border-radius: 9999px;
    }
    .dark ::-webkit-scrollbar-thumb {
      background: #2a3a2c;
    }
  </style>

  <script>
    window.addEventListener('error', function(e) {
      console.error('[Vocahigh Global Error]', e.message, e.filename, e.lineno);
      const fallbackBox = document.getElementById('global-error-fallback');
      if (fallbackBox) {
        fallbackBox.style.display = 'block';
        const msgElem = document.getElementById('global-error-msg');
        if (msgElem) msgElem.innerText = e.message + ' (' + e.filename + ':' + e.lineno + ')';
      }
    });
  </script>
</head>
<body class="bg-[#FAF6EC] dark:bg-[#121B13] text-[#2C3E2D] dark:text-[#EDECE4] font-sans antialiased min-h-screen transition-colors duration-300">

  <!-- 글로벌 치명적 에러 안내 박스 -->
  <div id="global-error-fallback" style="display:none;" class="fixed top-4 left-4 right-4 z-50 p-4 bg-red-100 border-2 border-red-500 rounded-2xl text-red-900 shadow-2xl text-xs space-y-2">
    <div class="font-extrabold flex items-center gap-2">
      <span>⚠️ 스크립트 실행 오류 감지</span>
    </div>
    <div id="global-error-msg" class="font-mono bg-white/70 p-2 rounded"></div>
    <button onclick="localStorage.clear(); location.reload();" class="px-3 py-1.5 bg-red-600 text-white font-bold rounded-lg text-xs">
      캐시 초기화 후 새로고침
    </button>
  </div>

  <div id="root" class="max-w-[430px] mx-auto min-h-screen relative shadow-2xl bg-[#FAF6EC] dark:bg-[#121B13] border-x border-[#EADBCA]/60 dark:border-[#203022]/60 flex flex-col justify-between">
    <!-- React 앱 마운트 영역 -->
  </div>

  <!-- 메인 리액트 애플리케이션 -->
  <script type="text/babel">
    const { useState, useEffect, useMemo, useRef, useCallback } = React;

    // ==========================================
    // 0. Supabase 환경 설정
    // ==========================================
    const DEFAULT_SUPABASE_URL = "https://tciluwoxihvbnzmtcchy.supabase.co";
    const DEFAULT_SUPABASE_ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRjaWx1d294aWh2Ym56bXRjY2h5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODkwNDAyNDMsImV4cCI6MjEwNDYxNjI0M30.H57GE6ZJ-XT6U_cSbJ9VdOhELOFcAZpAnN0F0cJGwMQ";

    const SUPABASE_URL = (typeof window !== 'undefined' && window.ENV?.SUPABASE_URL) 
      ? window.ENV.SUPABASE_URL 
      : DEFAULT_SUPABASE_URL;

    const SUPABASE_ANON_KEY = (typeof window !== 'undefined' && window.ENV?.SUPABASE_ANON_KEY) 
      ? window.ENV.SUPABASE_ANON_KEY 
      : DEFAULT_SUPABASE_ANON;

    let supabaseClient = null;
    let isSupabaseLoaded = false;

    try {
      if (window.supabase && typeof window.supabase.createClient === 'function') {
        supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
          auth: {
            persistSession: true,
            autoRefreshToken: true,
            detectSessionInUrl: true
          }
        });
        isSupabaseLoaded = true;
        console.log("✅ Supabase v2 클라이언트 초기화 완료");
      }
    } catch (e) {
      console.warn("⚠️ Supabase v2 번들 로드 지연 - Native 엔진 활성화", e);
    }

    // ==========================================
    // 1. 단어장 교재 메타데이터 (교육부 2종 + 커스텀)
    // ==========================================
    const STORAGE_PREFIX = 'VOCAHIGH_V12_';

    const BOOKS_DATA = [
      {
        id: "essential_2000",
        title: "필수 영단어 2000",
        subtitle: "교육부 지정 기초·중등·고교 핵심 (★ 2개 1,200단어 + ★ 1개 800단어)",
        totalWords: 2000,
        icon: "🌱",
        recommendedDaily: 20,
        levelBadge: "필수 기본 2000"
      },
      {
        id: "csat_1000",
        title: "수능 필수 1000",
        subtitle: "교육부 심화 및 수능 1등급 도약 빈출 (별표 없는 심화 1,000단어)",
        totalWords: 1000,
        icon: "🎯",
        recommendedDaily: 30,
        levelBadge: "수능 심화 1000"
      },
      {
        id: "custom",
        title: "커스텀 단어장",
        subtitle: "내가 직접 등록하고 관리하는 나만의 단어장",
        totalWords: 0,
        icon: "✏️",
        recommendedDaily: 20,
        levelBadge: "나만의 단어장"
      }
    ];

    // ==========================================
    // 2. 보카 트리 7단계 성장 기준
    // ==========================================
    const TREE_STAGES = [
      { level: 1, name: "씨앗", emoji: "🌱", minSunlight: 0, maxSunlight: 99, desc: "흙 속에 콕 박힌 단단하고 귀여운 황금 씨앗" },
      { level: 2, name: "새싹", emoji: "🌿", minSunlight: 100, maxSunlight: 299, desc: "파릇파릇 두 잎이 돋아난 아기 새싹" },
      { level: 3, name: "어린 줄기", emoji: "🎋", minSunlight: 300, maxSunlight: 499, desc: "곧게 뻗어가는 싱그러운 줄기" },
      { level: 4, name: "푸른 묘목", emoji: "🪴", minSunlight: 500, maxSunlight: 999, desc: "잔가지와 풍성한 잎을 갖춘 묘목" },
      { level: 5, name: "보카 나무", emoji: "🌳", minSunlight: 1000, maxSunlight: 1999, desc: "넓은 그늘을 드리우는 듬직한 초록 나무" },
      { level: 6, name: "황금 지혜나무", emoji: "🌟", minSunlight: 2000, maxSunlight: 4999, desc: "반짝이는 황금 열매와 꽃이 만개한 지혜나무" },
      { level: 7, name: "불멸의 세계수", emoji: "👑", minSunlight: 5000, maxSunlight: 999999, desc: "온 우주의 단어를 지키는 영원한 빛의 세계수" }
    ];

    function getTreeInfo(sunlight = 0) {
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
        const stageRange = nextStage.minSunlight - currentStage.minSunlight;
        const stageProgress = sunlight - currentStage.minSunlight;
        progressPercent = Math.min(100, Math.max(0, Math.round((stageProgress / stageRange) * 100)));
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

    // ==========================================
    // 3. Web Speech API (TTS 원어민 영어 발음)
    // ==========================================
    function playTTS(text) {
      if (!('speechSynthesis' in window)) {
        alert("이 브라우저는 음성 발음 기능을 지원하지 않습니다.");
        return;
      }
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'en-US';
      utterance.rate = 0.9;
      window.speechSynthesis.speak(utterance);
    }

    // ==========================================
    // 4. 교육부 3000 단어 폴백 데이터
    // ==========================================
    const FALLBACK_WORDS = [
      { id: 1, word: "aid", pos: "동/명", meaning: "도움, 돕다, 원조", example: "He came to my aid immediately.", bookId: "essential_2000", stars: "**", stage: 0 },
      { id: 2, word: "aim", pos: "동/명", meaning: "목표, 겨냥하다", example: "She aimed at the target accurately.", bookId: "essential_2000", stars: "**", stage: 0 },
      { id: 3, word: "ant", pos: "명", meaning: "개미", example: "Ants work diligently together in groups.", bookId: "essential_2000", stars: "**", stage: 0 },
      { id: 4, word: "bar", pos: "명/동", meaning: "막대, 술집, 막다", example: "He ate a bar of delicious dark chocolate.", bookId: "essential_2000", stars: "**", stage: 0 },
      { id: 5, word: "bay", pos: "명", meaning: "만(물굽이)", example: "The ships anchored safely in the quiet bay.", bookId: "essential_2000", stars: "**", stage: 0 },
      { id: 6, word: "beg", pos: "동", meaning: "간청하다, 구걸하다", example: "They begged for mercy and understanding.", bookId: "essential_2000", stars: "**", stage: 0 },
      { id: 7, word: "bet", pos: "동/명", meaning: "돈을 걸다, 내기", example: "I bet that our team will win the final.", bookId: "essential_2000", stars: "**", stage: 0 },
      { id: 8, word: "bin", pos: "명", meaning: "쓰레기통, 상자", example: "Please throw the trash into the proper bin.", bookId: "essential_2000", stars: "**", stage: 0 },
      { id: 9, word: "bit", pos: "명", meaning: "조금, 약간", example: "Wait a bit until the coffee cools down.", bookId: "essential_2000", stars: "**", stage: 0 },
      { id: 10, word: "bow", pos: "동/명", meaning: "인사하다, 활", example: "The actors bowed gracefully to the cheering audience.", bookId: "essential_2000", stars: "**", stage: 0 },
      { id: 11, word: "box", pos: "명/동", meaning: "상자, 권투하다", example: "Put the books into the cardboard box.", bookId: "essential_2000", stars: "**", stage: 0 },
      { id: 12, word: "boy", pos: "명", meaning: "소년, 아이", example: "The young boy smiled brightly at his teacher.", bookId: "essential_2000", stars: "**", stage: 0 },
      { id: 13, word: "bus", pos: "명", meaning: "버스", example: "We took the express bus to the station.", bookId: "essential_2000", stars: "**", stage: 0 },
      { id: 14, word: "buy", pos: "동", meaning: "사다, 구입하다", example: "I decided to buy a new study planner.", bookId: "essential_2000", stars: "**", stage: 0 },
      { id: 15, word: "can", pos: "조/명", meaning: "할 수 있다, 캔", example: "You can achieve all your study goals.", bookId: "essential_2000", stars: "**", stage: 0 },
      { id: 1201, word: "academic", pos: "형/명", meaning: "학업의, 학술적인", example: "He has outstanding academic achievements.", bookId: "essential_2000", stars: "*", stage: 0 },
      { id: 1202, word: "accurate", pos: "형", meaning: "정확한, 정밀한", example: "We need accurate data for the scientific report.", bookId: "essential_2000", stars: "*", stage: 0 },
      { id: 1203, word: "adequate", pos: "형", meaning: "충분한, 적절한", example: "Make sure you get adequate sleep every night.", bookId: "essential_2000", stars: "*", stage: 0 },
      { id: 2001, word: "abnormal", pos: "형", meaning: "비정상적인, 이상한", example: "The machine detected an abnormal temperature spike.", bookId: "csat_1000", stars: "", stage: 0 },
      { id: 2002, word: "abolish", pos: "동", meaning: "폐지하다, 없애다", example: "They fought tirelessly to abolish the unfair law.", bookId: "csat_1000", stars: "", stage: 0 }
    ];

    // ==========================================
    // 5. 로그인 & 회원가입 화면 (AuthScreen)
    // ==========================================
    function AuthScreen({ onLoginSuccess }) {
      const [isSignUp, setIsSignUp] = useState(false);
      const [email, setEmail] = useState('');
      const [password, setPassword] = useState('');
      const [name, setName] = useState('');
      const [errorMsg, setErrorMsg] = useState('');
      const [loading, setLoading] = useState(false);
      const [infoMsg, setInfoMsg] = useState('');

      const handleAuth = async (e) => {
        e.preventDefault();
        setErrorMsg('');
        setInfoMsg('');
        setLoading(true);

        const cleanEmail = email.trim().toLowerCase();
        if (!cleanEmail.includes('@')) {
          setLoading(false);
          return setErrorMsg('올바른 이메일 주소(예: user@gmail.com)를 입력해 주세요.');
        }
        if (password.length < 6) {
          setLoading(false);
          return setErrorMsg('비밀번호는 최소 6자 이상이어야 합니다.');
        }

        try {
          if (isSignUp) {
            const displayName = name.trim() || cleanEmail.split('@')[0];
            let signUpSuccess = false;
            let finalUser = null;

            if (isSupabaseLoaded && supabaseClient) {
              try {
                const { data, error } = await supabaseClient.auth.signUp({
                  email: cleanEmail,
                  password: password,
                  options: { data: { full_name: displayName } }
                });
                if (error) {
                  if (error.message.includes('rate limit')) throw new Error("RATE_LIMIT");
                  throw error;
                }
                if (data?.user) {
                  signUpSuccess = true;
                  finalUser = {
                    id: data.user.id,
                    email: data.user.email,
                    name: displayName,
                    avatar: `https://api.dicebear.com/7.x/bottts/svg?seed=${cleanEmail}`
                  };
                }
              } catch (cloudErr) {
                if (cloudErr.message === "RATE_LIMIT") {
                  setInfoMsg("⚡ Supabase 이메일 제한으로 인해 '즉시 안전 로컬 계정'으로 등록합니다.");
                } else {
                  console.warn("클라우드 회원가입 실패, Native 모드 전환:", cloudErr.message);
                }
              }
            }

            if (!signUpSuccess) {
              const usersKey = STORAGE_PREFIX + 'USERS_DB';
              const users = JSON.parse(localStorage.getItem(usersKey) || '{}');
              if (users[cleanEmail]) {
                setLoading(false);
                return setErrorMsg('이미 등록된 이메일 계정입니다. 로그인해 주세요.');
              }
              const userId = 'user_' + Math.random().toString(36).substring(2, 10);
              users[cleanEmail] = {
                id: userId,
                email: cleanEmail,
                name: displayName,
                passwordHash: btoa(password),
                createdAt: new Date().toISOString()
              };
              localStorage.setItem(usersKey, JSON.stringify(users));
              finalUser = {
                id: userId,
                email: cleanEmail,
                name: displayName,
                avatar: `https://api.dicebear.com/7.x/bottts/svg?seed=${cleanEmail}`
              };
            }

            setInfoMsg('🎉 회원가입이 완료되었습니다! 바로 학습을 시작합니다.');
            setTimeout(() => {
              onLoginSuccess(finalUser);
            }, 600);

          } else {
            let loginSuccess = false;
            let finalUser = null;

            if (isSupabaseLoaded && supabaseClient) {
              try {
                const { data, error } = await supabaseClient.auth.signInWithPassword({
                  email: cleanEmail,
                  password: password
                });
                if (!error && data?.user) {
                  loginSuccess = true;
                  finalUser = {
                    id: data.user.id,
                    email: data.user.email,
                    name: data.user.user_metadata?.full_name || cleanEmail.split('@')[0],
                    avatar: `https://api.dicebear.com/7.x/bottts/svg?seed=${cleanEmail}`
                  };
                }
              } catch (cloudErr) {
                console.warn("Supabase 로그인 에러:", cloudErr.message);
              }
            }

            if (!loginSuccess) {
              const usersKey = STORAGE_PREFIX + 'USERS_DB';
              const users = JSON.parse(localStorage.getItem(usersKey) || '{}');
              const found = users[cleanEmail];
              if (found && found.passwordHash === btoa(password)) {
                loginSuccess = true;
                finalUser = {
                  id: found.id,
                  email: found.email,
                  name: found.name,
                  avatar: `https://api.dicebear.com/7.x/bottts/svg?seed=${cleanEmail}`
                };
              }
            }

            if (loginSuccess && finalUser) {
              onLoginSuccess(finalUser);
            } else {
              setErrorMsg('이메일 또는 비밀번호가 일치하지 않습니다.');
            }
          }
        } catch (err) {
          setErrorMsg('인증 처리 중 오류가 발생했습니다: ' + err.message);
        } finally {
          setLoading(false);
        }
      };

      return (
        <div className="min-h-screen p-6 flex flex-col justify-center animate-fadeIn bg-gradient-to-b from-[#FAF6EC] via-[#FAF6EC] to-[#E8F5E9] dark:from-[#121B13] dark:to-[#1a2d1d]">
          <div className="text-center space-y-3 mb-8">
            <div className="inline-flex p-4 rounded-3xl bg-white dark:bg-[#1D2A1F] shadow-lg border border-[#EADBCA] dark:border-[#28382a] text-5xl animate-bounce">
              🌱
            </div>
            <h1 className="text-3xl font-black text-[#2D5A27] dark:text-[#A1C954] tracking-tight">
              vocahigh
            </h1>
            <p className="text-xs text-stone-500 dark:text-stone-300 font-medium">
              교육부 3,000 단어 장기기억 & 에빙하우스 망각곡선 복습 시스템
            </p>
          </div>

          <div className="bg-white dark:bg-[#1D2A1F] p-7 rounded-3xl border border-[#EADBCA] dark:border-[#28382a] shadow-xl space-y-5">
            <div className="flex border-b border-stone-100 dark:border-stone-800 pb-3">
              <button
                type="button"
                onClick={() => { setIsSignUp(false); setErrorMsg(''); setInfoMsg(''); }}
                className={`flex-1 py-2 text-center font-extrabold text-sm transition-all ${
                  !isSignUp ? 'text-[#2D5A27] dark:text-[#A1C954] border-b-2 border-[#2D5A27] dark:border-[#A1C954]' : 'text-stone-400'
                }`}
              >
                로그인
              </button>
              <button
                type="button"
                onClick={() => { setIsSignUp(true); setErrorMsg(''); setInfoMsg(''); }}
                className={`flex-1 py-2 text-center font-extrabold text-sm transition-all ${
                  isSignUp ? 'text-[#2D5A27] dark:text-[#A1C954] border-b-2 border-[#2D5A27] dark:border-[#A1C954]' : 'text-stone-400'
                }`}
              >
                회원가입
              </button>
            </div>

            {errorMsg && (
              <div className="p-3.5 rounded-2xl bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 text-xs text-red-700 dark:text-red-300 font-bold animate-shake">
                ⚠️ {errorMsg}
              </div>
            )}
            {infoMsg && (
              <div className="p-3.5 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 text-xs text-emerald-700 dark:text-emerald-300 font-bold">
                ℹ️ {infoMsg}
              </div>
            )}

            <form onSubmit={handleAuth} className="space-y-4 text-xs">
              {isSignUp && (
                <div className="space-y-1.5">
                  <label className="block font-bold text-stone-700 dark:text-stone-300">이름 또는 닉네임</label>
                  <input
                    type="text"
                    required
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="예: 홍길동"
                    className="w-full p-3.5 rounded-2xl border border-stone-200 dark:border-stone-700 bg-stone-50 dark:bg-stone-800 font-medium focus:outline-none focus:ring-2 focus:ring-[#2D5A27]"
                  />
                </div>
              )}

              <div className="space-y-1.5">
                <label className="block font-bold text-stone-700 dark:text-stone-300">이메일 계정</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="예: user@gmail.com"
                  className="w-full p-3.5 rounded-2xl border border-stone-200 dark:border-stone-700 bg-stone-50 dark:bg-stone-800 font-medium focus:outline-none focus:ring-2 focus:ring-[#2D5A27]"
                />
              </div>

              <div className="space-y-1.5">
                <label className="block font-bold text-stone-700 dark:text-stone-300">비밀번호</label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="6자 이상 비밀번호"
                  className="w-full p-3.5 rounded-2xl border border-stone-200 dark:border-stone-700 bg-stone-50 dark:bg-stone-800 font-medium focus:outline-none focus:ring-2 focus:ring-[#2D5A27]"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-4 bg-[#2D5A27] hover:bg-[#22471f] text-white font-extrabold text-sm rounded-2xl shadow-lg active:scale-95 transition-all flex items-center justify-center gap-2"
              >
                {loading ? (
                  <span>보안 인증 진행 중... ⏳</span>
                ) : (
                  <span>{isSignUp ? '🌱 회원가입하고 보카트리 심기' : '🚀 보카하이 로그인'}</span>
                )}
              </button>
            </form>
          </div>
        </div>
      );
    }

    // ==========================================
    // 6. 메인 홈 화면 (HomeScreen)
    // - 커리큘럼 미설정 시 생성 유도 카드
    // - 설정 시 상단 커리큘럼 셀렉터 제공 (단어장 변경 버튼 삭제)
    // - 상시 복습칸 (0개일 때도 유지)
    // ==========================================
    function HomeScreen({
      currentUser,
      curriculums,
      activeCurriculum,
      onSelectCurriculum,
      treeInfo,
      todayWords,
      dueWords,
      dailyProgress,
      onTabChange,
      onOpenDrawer,
      onOpenModal,
      onRequestStudySetup,
      onRequestTrainingSetup
    }) {
      const activeBook = BOOKS_DATA.find(b => b.id === activeCurriculum?.bookId) || BOOKS_DATA[0];

      return (
        <div className="p-5 pb-8 space-y-5 animate-fadeIn">
          
          {/* 상단 헤더: 좌측 ☰ 햄버거 버튼 & 타이틀 / 우측 DB 상태 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                onClick={onOpenDrawer}
                className="w-10 h-10 rounded-2xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 flex items-center justify-center text-lg shadow-sm hover:bg-stone-50 dark:hover:bg-stone-800 active:scale-95 transition-all text-stone-700 dark:text-stone-200"
                title="전체 메뉴 열기"
              >
                ☰
              </button>
              <div>
                <span className="font-black text-xl text-[#2D5A27] dark:text-[#A1C954] tracking-tight flex items-center gap-1">
                  <span>🌱</span> vocahigh
                </span>
                <div className="text-[10px] text-stone-500 dark:text-stone-400 font-bold truncate max-w-[150px]">
                  👤 {currentUser?.email || '학습자'}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => onOpenModal('db_status')}
                className="px-2.5 py-1 rounded-full bg-[#E8F5E9] dark:bg-[#16291a] border border-[#A1C954]/40 flex items-center gap-1.5 shadow-sm active:scale-95 transition-all"
                title="Supabase 클라우드 사용자별 연동 상태"
              >
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
                <span className="text-[11px] font-bold text-[#2D5A27] dark:text-[#A1C954]">인증 연동됨</span>
              </button>
            </div>
          </div>

          {/* ======================================================== */}
          {/* 분기 A: 커리큘럼이 설정되지 않았을 때 (생성 유도) */}
          {/* ======================================================== */}
          {(!activeCurriculum || curriculums.length === 0) ? (
            <div className="p-8 rounded-3xl bg-white dark:bg-[#1D2A1F] border-2 border-dashed border-[#A1C954] shadow-md text-center space-y-4 animate-scaleUp">
              <div className="text-5xl animate-bounce">🌱</div>
              <div className="space-y-1">
                <h3 className="text-lg font-black text-[#2D5A27] dark:text-[#A1C954]">
                  아직 커리큘럼이 설정되지 않았습니다
                </h3>
                <p className="text-xs text-stone-500 dark:text-stone-400 leading-relaxed">
                  보카하이의 체계적인 학습을 시작하려면 먼저 나에게 맞는 단어장과 하루 목표 단어 수를 정해 커리큘럼을 생성해 주세요!
                </p>
              </div>

              <button
                onClick={() => onTabChange('create_curriculum')}
                className="w-full py-4 bg-[#2D5A27] hover:bg-[#22471f] text-white font-black text-sm rounded-2xl shadow-xl active:scale-95 transition-all flex items-center justify-center gap-2"
              >
                <span>➕ 나만의 커리큘럼 생성하기</span>
                <span>🚀</span>
              </button>
            </div>
          ) : (
            /* ======================================================== */
            /* 분기 B: 커리큘럼이 정상 설정되어 있을 때 (메인 대시보드) */
            /* ======================================================== */
            <>
              {/* 상단 커리큘럼 선택기 (단어장 변경 버튼 대체) */}
              <div className="p-3.5 rounded-2xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 flex items-center justify-between shadow-sm">
                <div className="flex items-center gap-2">
                  <span className="text-base">📋</span>
                  <div>
                    <div className="text-[10px] font-bold text-stone-400">현재 학습 커리큘럼</div>
                    <div className="font-extrabold text-xs text-[#2D5A27] dark:text-[#A1C954] truncate max-w-[170px]">
                      {activeCurriculum.name}
                    </div>
                  </div>
                </div>

                {/* 커리큘럼 전환 드롭다운 */}
                <select
                  value={activeCurriculum.id}
                  onChange={(e) => onSelectCurriculum(e.target.value)}
                  className="p-1.5 px-2.5 rounded-xl border border-stone-200 dark:border-stone-700 bg-stone-50 dark:bg-stone-800 text-[11px] font-bold text-stone-700 dark:text-stone-200 focus:outline-none focus:ring-2 focus:ring-[#2D5A27]"
                >
                  {curriculums.map(c => (
                    <option key={c.id} value={c.id}>
                      {c.name} ({c.dailyGoal}개/일)
                    </option>
                  ))}
                </select>
              </div>

              {/* 보카 트리 위젯 카드 */}
              <div
                onClick={() => onTabChange('tree')}
                className="p-5 rounded-3xl bg-gradient-to-br from-[#FAF6EC] via-[#FAF6EC] to-[#E8F5E9] dark:from-[#162418] dark:to-[#1f3822] border border-[#EADBCA] dark:border-[#28382a] shadow-sm cursor-pointer hover:shadow-md transition-all relative overflow-hidden"
              >
                <div className="flex items-center justify-between">
                  <div>
                    <span className="px-2.5 py-0.5 text-[10px] font-extrabold rounded-full bg-[#A1C954]/30 text-[#2D5A27] dark:text-[#A1C954]">
                      보카 트리 Lv.{treeInfo.currentStage.level}
                    </span>
                    <h2 className="text-xl font-black text-[#2D5A27] dark:text-[#A1C954] mt-1">
                      {treeInfo.currentStage.name}
                    </h2>
                    <div className="text-xs text-stone-500 dark:text-stone-300 mt-0.5">
                      단어 1개마다 무조건 ☀️ 햇살 1개 획득!
                    </div>
                  </div>
                  <div className="text-5xl animate-bounce select-none">
                    {treeInfo.currentStage.emoji}
                  </div>
                </div>

                <div className="mt-4 space-y-1.5">
                  <div className="flex justify-between text-[11px] font-bold">
                    <span className="text-stone-500 dark:text-stone-400">성장 게이지</span>
                    <span className="text-[#2D5A27] dark:text-[#A1C954]">
                      ☀️ {treeInfo.sunlight} 햇살 ({treeInfo.progressPercent}%)
                    </span>
                  </div>
                  <div className="w-full h-3 rounded-full bg-stone-200 dark:bg-stone-800 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-[#5F8D4E] to-[#A1C954] transition-all duration-500 rounded-full"
                      style={{ width: `${treeInfo.progressPercent}%` }}
                    />
                  </div>
                  {treeInfo.nextStage && (
                    <div className="text-[10px] text-stone-400 text-right">
                      다음 단계 [{treeInfo.nextStage.name}]까지 ☀️ {treeInfo.remainingSunlight} 남음
                    </div>
                  )}
                </div>
              </div>

              {/* 에빙하우스 상시 복습칸 (0개일 때도 항상 표시됨!) */}
              <div
                onClick={() => onTabChange('review')}
                className={`p-4 rounded-3xl border flex items-center justify-between cursor-pointer shadow-sm transition-all hover:scale-[1.01] ${
                  dueWords.length > 0
                    ? 'bg-amber-50 dark:bg-[#2b2515] border-amber-200 dark:border-amber-800/60'
                    : 'bg-white dark:bg-[#1D2A1F] border-stone-200 dark:border-stone-800'
                }`}
              >
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{dueWords.length > 0 ? '🚨' : '🧠'}</span>
                  <div>
                    <div className="flex items-center gap-1.5">
                      <span className={`text-xs font-black ${
                        dueWords.length > 0 ? 'text-amber-900 dark:text-amber-200' : 'text-[#2D5A27] dark:text-[#A1C954]'
                      }`}>
                        에빙하우스 망각곡선 복습칸
                      </span>
                      <span className={`text-[10px] px-1.5 py-0.2 rounded-full font-bold ${
                        dueWords.length > 0
                          ? 'bg-amber-200 dark:bg-amber-900 text-amber-900 dark:text-amber-200'
                          : 'bg-stone-100 dark:bg-stone-800 text-stone-500'
                      }`}>
                        {dueWords.length > 0 ? `${dueWords.length}단어 대기` : '대기 0단어'}
                      </span>
                    </div>
                    <div className="text-[11px] text-stone-500 dark:text-stone-400 mt-0.5">
                      {dueWords.length > 0
                        ? `장기기억으로 굳힐 ${dueWords.length}개의 복습 단어가 기다려요!`
                        : '현재 복습할 단어가 없습니다 (망각 주기에 맞춰 자동으로 도착합니다)'}
                    </div>
                  </div>
                </div>
                <span className={`text-xs font-bold ${dueWords.length > 0 ? 'text-amber-800 dark:text-amber-300' : 'text-stone-400'}`}>
                  {dueWords.length > 0 ? '복습하기 →' : '안내 →'}
                </span>
              </div>

              {/* 오늘의 출석 도장 & 조건 달성 현황 */}
              <div className="p-5 rounded-3xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 shadow-sm space-y-3">
                <div className="flex items-center justify-between pb-3 border-b border-stone-100 dark:border-stone-800/80">
                  <div className="flex items-center gap-2">
                    <span className="text-xl">📅</span>
                    <div>
                      <div className="font-extrabold text-sm text-[#2C3E2D] dark:text-[#EDECE4]">오늘의 출석 도장</div>
                      <div className="text-[11px] text-stone-400">설정한 기준 달성 시 자동 날인</div>
                    </div>
                  </div>
                  <div>
                    {dailyProgress.isAttendanceStamped ? (
                      <span className="px-3 py-1 bg-emerald-500 text-white font-black text-xs rounded-full shadow-sm animate-scaleUp flex items-center gap-1">
                        <span>출석 완료</span> <span>💮</span>
                      </span>
                    ) : (
                      <span className="px-3 py-1 bg-stone-100 dark:bg-stone-800 text-stone-500 font-bold text-xs rounded-full">
                        미완료 ⏳
                      </span>
                    )}
                  </div>
                </div>

                {/* 체크박스 기준 진행 상황 */}
                <div className="grid grid-cols-2 gap-2 text-xs">
                  {[
                    { id: 'vocab_study', label: '학습 단어장', done: dailyProgress.studyCompleted },
                    { id: 'flashcard', label: '플래시카드', done: dailyProgress.flashcardCompleted },
                    { id: 'recall', label: '훈련 단어장', done: dailyProgress.recallCompleted },
                    { id: 'spelling', label: '스펠링 훈련', done: dailyProgress.spellingCompleted }
                  ].map(item => {
                    const isCriterion = activeCurriculum?.attendanceCriteria?.includes(item.id);
                    return (
                      <div
                        key={item.id}
                        className={`p-2.5 rounded-2xl flex items-center justify-between border ${
                          item.done
                            ? 'bg-[#E8F5E9] dark:bg-[#1b3820] border-[#A1C954]/50 text-[#2D5A27] dark:text-[#A1C954]'
                            : isCriterion
                            ? 'bg-stone-50 dark:bg-stone-800/50 border-stone-200 dark:border-stone-700 text-stone-600 dark:text-stone-300'
                            : 'bg-stone-50 dark:bg-stone-900 border-transparent text-stone-400 opacity-60'
                        }`}
                      >
                        <span className="font-bold flex items-center gap-1">
                          {isCriterion && <span className="text-[9px] px-1 py-0.5 rounded bg-[#2D5A27] text-white">필수</span>}
                          {item.label}
                        </span>
                        <span>{item.done ? '✅' : '○'}</span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* 현재 선택된 교재 & 학습 시작 큰 버튼 2개 */}
              <div className="space-y-2">
                <div className="p-4 rounded-3xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <span className="text-3xl">{activeBook.icon}</span>
                    <div>
                      <div className="font-extrabold text-sm text-[#2C3E2D] dark:text-[#EDECE4]">{activeBook.title}</div>
                      <div className="text-xs text-stone-400">목표: 하루 {activeCurriculum?.dailyGoal || 20}단어</div>
                    </div>
                  </div>
                  <span className="text-xs px-2.5 py-1 rounded-full bg-[#FAF6EC] dark:bg-stone-800 font-bold text-[#2D5A27] dark:text-[#A1C954]">
                    {activeBook.levelBadge}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-2 pt-1">
                  {/* 1. 학습 단어장 버튼 (옵션 팝업 호출) */}
                  <button
                    onClick={onRequestStudySetup}
                    className="py-4 bg-[#2D5A27] hover:bg-[#22471f] text-white font-extrabold text-sm rounded-2xl shadow-lg active:scale-98 transition-all flex flex-col items-center justify-center gap-1"
                  >
                    <div className="flex items-center gap-1">
                      <span>📖 학습 단어장</span>
                    </div>
                    <span className="text-[10px] text-emerald-200 font-normal">기본·뜻가림·단어만</span>
                  </button>

                  {/* 2. 훈련 단어장 버튼 (옵션 팝업 호출) */}
                  <button
                    onClick={onRequestTrainingSetup}
                    className="py-4 bg-[#5F8D4E] hover:bg-[#4d743f] text-white font-extrabold text-sm rounded-2xl shadow-lg active:scale-98 transition-all flex flex-col items-center justify-center gap-1"
                  >
                    <div className="flex items-center gap-1">
                      <span>🎯 훈련 단어장</span>
                      <span className="text-[10px] px-1.5 py-0.2 bg-white/20 rounded-full">☀️+1</span>
                    </div>
                    <span className="text-[10px] text-lime-200 font-normal">플래시·리콜·스펠링</span>
                  </button>
                </div>
              </div>
            </>
          )}

        </div>
      );
    }

    // ==========================================
    // 7. [팝업] 학습 단어장 3종 암기 모드 선택 모달 (StudySetupModal)
    // - 기본 (단어 + 뜻)
    // - 단어&뜻 보기 (왼쪽 스펠링, 오른쪽 클릭 시 뒤집히는 뜻 카드)
    // - 단어만 보기 (영어 단어만)
    // ==========================================
    function StudySetupModal({ isOpen, onClose, onStart }) {
      const [studyStyle, setStudyStyle] = useState('card_flip'); // 'basic' | 'card_flip' | 'word_only'
      const [viewMode, setViewMode] = useState('one_by_one'); // 'one_by_one' | 'list'

      if (!isOpen) return null;

      return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn">
          <div className="w-full max-w-sm bg-white dark:bg-[#1D2A1F] rounded-3xl p-6 shadow-2xl space-y-5 animate-scaleUp">
            <div className="flex justify-between items-center pb-2 border-b border-stone-100 dark:border-stone-800">
              <div className="flex items-center gap-2">
                <span className="text-xl">📖</span>
                <h3 className="font-black text-base text-[#2D5A27] dark:text-[#A1C954]">
                  학습 단어장 맞춤 옵션
                </h3>
              </div>
              <button onClick={onClose} className="w-7 h-7 rounded-full bg-stone-100 dark:bg-stone-800 font-bold text-xs text-stone-500">✕</button>
            </div>

            <div className="space-y-4 text-xs">
              
              {/* 1. 암기 모드 3종 선택 */}
              <div className="space-y-2">
                <label className="font-bold text-stone-700 dark:text-stone-300">1. 암기 스타일 선택</label>
                
                {/* 1) 기본 */}
                <div
                  onClick={() => setStudyStyle('basic')}
                  className={`p-3 rounded-2xl border-2 cursor-pointer transition-all flex items-center justify-between ${
                    studyStyle === 'basic'
                      ? 'border-[#2D5A27] bg-[#FAF6EC] dark:bg-[#203624] dark:border-[#A1C954] shadow-sm'
                      : 'border-stone-200 dark:border-stone-800'
                  }`}
                >
                  <div className="space-y-0.5">
                    <div className="font-black text-xs text-[#2C3E2D] dark:text-[#EDECE4]">
                      📘 기본 (단어 + 뜻 함께 보기)
                    </div>
                    <div className="text-[10px] text-stone-400">영어 스펠링과 뜻, 예문이 함께 보이는 종합 학습</div>
                  </div>
                  <span className={`text-xs ${studyStyle === 'basic' ? 'text-[#2D5A27] font-black' : 'text-stone-300'}`}>✓</span>
                </div>

                {/* 2) 단어&뜻 보기 (뒤집기 플립 토글) */}
                <div
                  onClick={() => setStudyStyle('card_flip')}
                  className={`p-3 rounded-2xl border-2 cursor-pointer transition-all flex items-center justify-between ${
                    studyStyle === 'card_flip'
                      ? 'border-[#2D5A27] bg-[#FAF6EC] dark:bg-[#203624] dark:border-[#A1C954] shadow-sm'
                      : 'border-stone-200 dark:border-stone-800'
                  }`}
                >
                  <div className="space-y-0.5">
                    <div className="font-black text-xs text-[#2C3E2D] dark:text-[#EDECE4]">
                      🃏 단어&뜻 보기 (뜻 가림 카드 뒤집기)
                    </div>
                    <div className="text-[10px] text-stone-400">왼쪽 스펠링 카드, 오른쪽은 클릭 시 뒤집히며 뜻 확인</div>
                  </div>
                  <span className={`text-xs ${studyStyle === 'card_flip' ? 'text-[#2D5A27] font-black' : 'text-stone-300'}`}>✓</span>
                </div>

                {/* 3) 단어만 보기 */}
                <div
                  onClick={() => setStudyStyle('word_only')}
                  className={`p-3 rounded-2xl border-2 cursor-pointer transition-all flex items-center justify-between ${
                    studyStyle === 'word_only'
                      ? 'border-[#2D5A27] bg-[#FAF6EC] dark:bg-[#203624] dark:border-[#A1C954] shadow-sm'
                      : 'border-stone-200 dark:border-stone-800'
                  }`}
                >
                  <div className="space-y-0.5">
                    <div className="font-black text-xs text-[#2C3E2D] dark:text-[#EDECE4]">
                      🔤 단어만 보기 (스펠링 집중)
                    </div>
                    <div className="text-[10px] text-stone-400">뜻 없이 영어 단어만 보며 머릿속으로 뜻 연상 훈련</div>
                  </div>
                  <span className={`text-xs ${studyStyle === 'word_only' ? 'text-[#2D5A27] font-black' : 'text-stone-300'}`}>✓</span>
                </div>
              </div>

              {/* 2. 보기 방식 선택 */}
              <div className="space-y-1.5">
                <label className="font-bold text-stone-700 dark:text-stone-300">2. 보기 방식</label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setViewMode('one_by_one')}
                    className={`py-2.5 rounded-xl font-bold transition-all ${
                      viewMode === 'one_by_one' ? 'bg-[#2D5A27] text-white shadow-md' : 'bg-stone-100 dark:bg-stone-800 text-stone-500'
                    }`}
                  >
                    🗂️ 하나씩 보기
                  </button>
                  <button
                    type="button"
                    onClick={() => setViewMode('list')}
                    className={`py-2.5 rounded-xl font-bold transition-all ${
                      viewMode === 'list' ? 'bg-[#2D5A27] text-white shadow-md' : 'bg-stone-100 dark:bg-stone-800 text-stone-500'
                    }`}
                  >
                    📋 리스트로 보기
                  </button>
                </div>
              </div>

            </div>

            <button
              onClick={() => {
                onClose();
                onStart(studyStyle, viewMode);
              }}
              className="w-full py-4 bg-[#2D5A27] text-white font-extrabold text-sm rounded-2xl shadow-lg active:scale-95 transition-all"
            >
              🚀 선택한 모드로 학습 시작하기
            </button>
          </div>
        </div>
      );
    }

    // ==========================================
    // 8. [팝업] 훈련 단어장 3대 훈련 모드 선택 모달 (TrainingSetupModal)
    // - 훈련 모드 3종: 플래시 카드 / 워드 리콜 / 스펠링 훈련
    // - 출제 방향: 영➔한 / 한➔영
    // - 풀이 방식: 단어 하나씩 / 리스트로 한 번에
    // - 타이머: 5초 / 10초 / 무제한
    // ==========================================
    function TrainingSetupModal({ isOpen, onClose, onStart }) {
      const [trainingType, setTrainingType] = useState('recall'); // 'flashcard' | 'recall' | 'spelling'
      const [direction, setDirection] = useState('en_to_ko'); // 'en_to_ko' | 'ko_to_en'
      const [format, setFormat] = useState('one_by_one'); // 'one_by_one' | 'list'
      const [timerSec, setTimerSec] = useState(10); // 5, 10, 0

      if (!isOpen) return null;

      return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn">
          <div className="w-full max-w-sm bg-white dark:bg-[#1D2A1F] rounded-3xl p-6 shadow-2xl space-y-4 animate-scaleUp">
            <div className="flex justify-between items-center pb-2 border-b border-stone-100 dark:border-stone-800">
              <div className="flex items-center gap-2">
                <span className="text-xl">🎯</span>
                <h3 className="font-black text-base text-[#2D5A27] dark:text-[#A1C954]">
                  훈련 단어장 모드 설정
                </h3>
              </div>
              <button onClick={onClose} className="w-7 h-7 rounded-full bg-stone-100 dark:bg-stone-800 font-bold text-xs text-stone-500">✕</button>
            </div>

            <div className="space-y-3.5 text-xs">
              
              {/* 1. 3대 훈련 모드 선택 */}
              <div className="space-y-1.5">
                <label className="font-bold text-stone-700 dark:text-stone-300">1. 훈련 방식 선택</label>
                <div className="grid grid-cols-3 gap-1.5">
                  {[
                    { id: 'recall', label: '🧠 워드리콜', sub: '4지선다' },
                    { id: 'flashcard', label: '🗂️ 플래시카드', sub: '뒤집기' },
                    { id: 'spelling', label: '✍️ 스펠링', sub: '타이핑' }
                  ].map(m => (
                    <button
                      key={m.id}
                      type="button"
                      onClick={() => setTrainingType(m.id)}
                      className={`p-2.5 rounded-2xl border text-center transition-all ${
                        trainingType === m.id
                          ? 'border-[#2D5A27] bg-[#FAF6EC] dark:bg-[#203624] text-[#2D5A27] dark:text-[#A1C954] font-black shadow-sm scale-105'
                          : 'border-stone-200 dark:border-stone-800 text-stone-500'
                      }`}
                    >
                      <div className="text-xs">{m.label}</div>
                      <div className="text-[9px] text-stone-400 mt-0.5">{m.sub}</div>
                    </button>
                  ))}
                </div>
              </div>

              {/* 2. 출제 방향 */}
              <div className="space-y-1.5">
                <label className="font-bold text-stone-700 dark:text-stone-300">2. 출제 방향</label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setDirection('en_to_ko')}
                    className={`py-2 rounded-xl font-bold transition-all ${
                      direction === 'en_to_ko' ? 'bg-[#2D5A27] text-white shadow-sm' : 'bg-stone-100 dark:bg-stone-800 text-stone-500'
                    }`}
                  >
                    🇺🇸 영 ➔ 🇰🇷 한
                  </button>
                  <button
                    type="button"
                    onClick={() => setDirection('ko_to_en')}
                    className={`py-2 rounded-xl font-bold transition-all ${
                      direction === 'ko_to_en' ? 'bg-[#2D5A27] text-white shadow-sm' : 'bg-stone-100 dark:bg-stone-800 text-stone-500'
                    }`}
                  >
                    🇰🇷 한 ➔ 🇺🇸 영
                  </button>
                </div>
              </div>

              {/* 3. 풀이 방식 */}
              <div className="space-y-1.5">
                <label className="font-bold text-stone-700 dark:text-stone-300">3. 풀이 방식</label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    type="button"
                    onClick={() => setFormat('one_by_one')}
                    className={`py-2 rounded-xl font-bold transition-all ${
                      format === 'one_by_one' ? 'bg-[#5F8D4E] text-white shadow-sm' : 'bg-stone-100 dark:bg-stone-800 text-stone-500'
                    }`}
                  >
                    단어 하나씩 풀기
                  </button>
                  <button
                    type="button"
                    onClick={() => setFormat('list')}
                    className={`py-2 rounded-xl font-bold transition-all ${
                      format === 'list' ? 'bg-[#5F8D4E] text-white shadow-sm' : 'bg-stone-100 dark:bg-stone-800 text-stone-500'
                    }`}
                  >
                    리스트로 한 번에
                  </button>
                </div>
              </div>

              {/* 4. 제한시간 타이머 */}
              <div className="space-y-1.5">
                <label className="font-bold text-stone-700 dark:text-stone-300">4. 문제당 타이머</label>
                <div className="grid grid-cols-3 gap-1.5">
                  {[
                    { sec: 5, label: '⚡ 5초' },
                    { sec: 10, label: '⏱️ 10초' },
                    { sec: 0, label: '♾️ 무제한' }
                  ].map(t => (
                    <button
                      key={t.sec}
                      type="button"
                      onClick={() => setTimerSec(t.sec)}
                      className={`py-2 rounded-xl font-bold text-[11px] transition-all ${
                        timerSec === t.sec ? 'bg-[#A1C954] text-[#121B13] font-black shadow-sm' : 'bg-stone-100 dark:bg-stone-800 text-stone-500'
                      }`}
                    >
                      {t.label}
                    </button>
                  ))}
                </div>
              </div>

            </div>

            <button
              onClick={() => {
                onClose();
                onStart({ trainingType, direction, format, timerSec });
              }}
              className="w-full py-4 bg-[#2D5A27] text-white font-extrabold text-sm rounded-2xl shadow-lg active:scale-95 transition-all"
            >
              🎯 훈련 시작하기 (☀️ 햇살 획득)
            </button>
          </div>
        </div>
      );
    }

    // ==========================================
    // 9. 학습 단어장 화면 (StudyScreen)
    // - 3가지 암기 모드: 기본 / 단어&뜻 플립 토글 / 단어만 보기
    // ==========================================
    function StudyScreen({ todayWords, initialStyle, initialMode, onComplete, onAddSun, onTabChange, onGoToTraining }) {
      const [style, setStyle] = useState(initialStyle || 'card_flip'); // 'basic' | 'card_flip' | 'word_only'
      const [mode, setMode] = useState(initialMode || 'one_by_one'); // 'one_by_one' | 'list'
      const [currentIndex, setCurrentIndex] = useState(0);

      // 단어&뜻 플립 상태 (각 단어별 공개 여부)
      const [flippedMap, setFlippedMap] = useState({});

      const currentWord = todayWords[currentIndex] || todayWords[0];

      const toggleFlip = (wordId) => {
        setFlippedMap(prev => ({ ...prev, [wordId]: !prev[wordId] }));
      };

      const handleNextOne = () => {
        onAddSun(1);
        if (currentIndex + 1 < todayWords.length) {
          setCurrentIndex(currentIndex + 1);
        } else {
          onComplete();
          if (confirm("🎉 오늘의 단어 학습을 완료했습니다!\n곧바로 '훈련 단어장'으로 이동하여 테스트를 시작할까요?")) {
            onGoToTraining();
          } else {
            onTabChange('home');
          }
        }
      };

      const handleFinishList = () => {
        onAddSun(todayWords.length);
        onComplete();
        if (confirm("🎉 전체 리스트 단어 학습을 완료했습니다!\n곧바로 '훈련 단어장'으로 이동하여 테스트를 시작할까요?")) {
          onGoToTraining();
        } else {
          onTabChange('home');
        }
      };

      if (!todayWords || todayWords.length === 0) {
        return (
          <div className="p-10 text-center space-y-4">
            <div>학습할 단어가 없습니다.</div>
            <button onClick={() => onTabChange('home')} className="px-4 py-2 bg-[#2D5A27] text-white rounded-xl">홈으로</button>
          </div>
        );
      }

      return (
        <div className="p-5 pb-8 space-y-5 animate-fadeIn">
          {/* 상단 네비게이션 & 토글 바 */}
          <div className="flex items-center justify-between">
            <button
              onClick={() => onTabChange('home')}
              className="w-10 h-10 rounded-2xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 text-stone-700 dark:text-stone-200 font-black text-base shadow-sm hover:bg-stone-50 active:scale-95 transition-all flex items-center justify-center"
              title="홈으로 돌아가기"
            >
              ←
            </button>
            
            {/* 암기 스타일 3종 스위치 */}
            <div className="flex p-1 rounded-2xl bg-stone-200 dark:bg-stone-800 text-[11px] font-bold">
              <button
                onClick={() => setStyle('basic')}
                className={`px-2.5 py-1 rounded-xl transition-all ${style === 'basic' ? 'bg-white dark:bg-[#1D2A1F] text-[#2D5A27] dark:text-[#A1C954] shadow-sm' : 'text-stone-500'}`}
              >
                기본
              </button>
              <button
                onClick={() => setStyle('card_flip')}
                className={`px-2.5 py-1 rounded-xl transition-all ${style === 'card_flip' ? 'bg-white dark:bg-[#1D2A1F] text-[#2D5A27] dark:text-[#A1C954] shadow-sm' : 'text-stone-500'}`}
              >
                단어&뜻
              </button>
              <button
                onClick={() => setStyle('word_only')}
                className={`px-2.5 py-1 rounded-xl transition-all ${style === 'word_only' ? 'bg-white dark:bg-[#1D2A1F] text-[#2D5A27] dark:text-[#A1C954] shadow-sm' : 'text-stone-500'}`}
              >
                단어만
              </button>
            </div>

            {/* 하나씩 / 리스트 스위치 */}
            <button
              onClick={() => setMode(mode === 'one_by_one' ? 'list' : 'one_by_one')}
              className="px-2.5 py-2 rounded-xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 text-[11px] font-bold text-stone-600 dark:text-stone-300"
            >
              {mode === 'one_by_one' ? '📋 리스트' : '🗂️ 카드'}
            </button>
          </div>

          {/* ======================================================= */}
          {/* MODE 1: 단어 하나씩 보기 */}
          {/* ======================================================= */}
          {mode === 'one_by_one' && (
            <div className="space-y-6">
              <div className="text-center text-xs font-black text-[#5F8D4E]">
                진행: {currentIndex + 1} / {todayWords.length} 단어
              </div>

              {/* 1. 스타일 A: 기본 종합 뷰 */}
              {style === 'basic' && (
                <div className="p-8 rounded-3xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 shadow-xl text-center space-y-5 animate-fadeIn">
                  <div className="flex items-center justify-center gap-2">
                    <span className="text-3xl font-black text-[#2D5A27] dark:text-[#A1C954]">{currentWord.word}</span>
                    <button onClick={() => playTTS(currentWord.word)} className="p-2 rounded-full hover:bg-stone-100 dark:hover:bg-stone-800">🔊</button>
                  </div>
                  <div className="text-lg font-bold text-stone-700 dark:text-stone-200">{currentWord.meaning}</div>
                  {currentWord.example && (
                    <div className="p-4 rounded-2xl bg-[#FAF6EC] dark:bg-[#162418] text-xs text-stone-600 dark:text-stone-300 italic">
                      "{currentWord.example}"
                    </div>
                  )}
                </div>
              )}

              {/* 2. 스타일 B: 단어&뜻 보기 (왼쪽 스펠링 카드, 오른쪽 클릭 시 뒤집히는 뜻 카드) */}
              {style === 'card_flip' && (
                <div className="grid grid-cols-2 gap-3 animate-fadeIn">
                  {/* 왼쪽 스펠링 카드 */}
                  <div className="h-64 rounded-3xl bg-white dark:bg-[#1D2A1F] border-2 border-stone-200 dark:border-stone-800 p-5 flex flex-col items-center justify-center text-center shadow-md">
                    <span className="text-xs text-stone-400 font-bold mb-2">스펠링 카드</span>
                    <div className="text-2xl font-black text-[#2D5A27] dark:text-[#A1C954] mb-3">
                      {currentWord.word}
                    </div>
                    <button
                      onClick={() => playTTS(currentWord.word)}
                      className="px-3 py-1.5 rounded-full bg-stone-100 dark:bg-stone-800 text-xs font-bold flex items-center gap-1 active:scale-95"
                    >
                      <span>🔊</span> <span>발음</span>
                    </button>
                  </div>

                  {/* 오른쪽 뜻 카드 (클릭 시 뒤집히며 뜻 확인/가림 토글) */}
                  <div
                    onClick={() => toggleFlip(currentWord.id)}
                    className={`h-64 rounded-3xl border-2 p-5 flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-300 shadow-md ${
                      flippedMap[currentWord.id]
                        ? 'bg-[#FAF6EC] dark:bg-[#1c3320] border-[#A1C954]'
                        : 'bg-stone-100 dark:bg-[#162217] border-dashed border-stone-300 dark:border-stone-700'
                    }`}
                  >
                    {flippedMap[currentWord.id] ? (
                      <div className="space-y-2 animate-flipIn">
                        <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold">뜻 카드 (공개됨)</span>
                        <div className="text-lg font-black text-stone-800 dark:text-stone-100">
                          {currentWord.meaning}
                        </div>
                        <div className="text-[10px] text-stone-400">클릭하면 다시 가려집니다</div>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        <span className="text-3xl">🃏</span>
                        <div className="text-xs font-black text-stone-500 dark:text-stone-300">
                          뜻 카드가 뒤집혀 있습니다
                        </div>
                        <div className="text-[10px] text-stone-400">터치하여 뜻 확인 👆</div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* 3. 스타일 C: 단어만 보기 */}
              {style === 'word_only' && (
                <div className="h-64 rounded-3xl bg-white dark:bg-[#1D2A1F] border-2 border-[#2D5A27] shadow-xl flex flex-col items-center justify-center text-center p-6 space-y-4 animate-fadeIn">
                  <div className="text-xs text-stone-400 font-bold">단어 집중 모드 (스펠링 암기)</div>
                  <div className="text-4xl font-black text-[#2D5A27] dark:text-[#A1C954] tracking-wide">
                    {currentWord.word}
                  </div>
                  <button
                    onClick={() => playTTS(currentWord.word)}
                    className="px-3.5 py-1.5 rounded-full bg-stone-100 dark:bg-stone-800 text-xs font-bold"
                  >
                    🔊 원어민 발음 듣기
                  </button>
                </div>
              )}

              <div className="flex gap-3">
                <button
                  disabled={currentIndex === 0}
                  onClick={() => setCurrentIndex(currentIndex - 1)}
                  className="flex-1 py-4 rounded-2xl bg-stone-200 dark:bg-stone-800 text-stone-600 dark:text-stone-300 font-bold disabled:opacity-40"
                >
                  이전 단어
                </button>
                <button
                  onClick={handleNextOne}
                  className="flex-1 py-4 rounded-2xl bg-[#2D5A27] text-white font-black shadow-lg"
                >
                  {currentIndex + 1 === todayWords.length ? '학습 완료 & 훈련으로 🚀' : '다음 단어 →'}
                </button>
              </div>
            </div>
          )}

          {/* ======================================================= */}
          {/* MODE 2: 리스트로 보기 */}
          {/* ======================================================= */}
          {mode === 'list' && (
            <div className="space-y-4 animate-fadeIn">
              <div className="text-xs font-bold text-stone-500 px-1">
                전체 단어 목록 ({todayWords.length}단어)
              </div>

              <div className="space-y-2.5">
                {todayWords.map((item, idx) => (
                  <div
                    key={item.id || idx}
                    className="p-4 rounded-2xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 shadow-sm"
                  >
                    {style === 'basic' && (
                      <div className="flex items-center justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <span className="text-xs text-stone-400 font-bold">#{idx + 1}</span>
                            <span className="text-base font-black text-[#2C3E2D] dark:text-[#EDECE4]">{item.word}</span>
                            <button onClick={() => playTTS(item.word)} className="text-stone-400 text-xs">🔊</button>
                          </div>
                          <div className="text-xs font-bold text-[#2D5A27] dark:text-[#A1C954]">{item.meaning}</div>
                        </div>
                      </div>
                    )}

                    {style === 'card_flip' && (
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-stone-400 font-bold">#{idx + 1}</span>
                          <span className="text-base font-black text-[#2C3E2D] dark:text-[#EDECE4]">{item.word}</span>
                          <button onClick={() => playTTS(item.word)} className="text-stone-400 text-xs">🔊</button>
                        </div>
                        <button
                          onClick={() => toggleFlip(item.id)}
                          className={`px-3 py-1.5 rounded-xl text-xs font-bold border transition-all ${
                            flippedMap[item.id] ? 'bg-[#E8F5E9] border-[#A1C954] text-[#2D5A27]' : 'bg-stone-100 border-stone-200 text-stone-400'
                          }`}
                        >
                          {flippedMap[item.id] ? item.meaning : '🃏 뜻 보기'}
                        </button>
                      </div>
                    )}

                    {style === 'word_only' && (
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-stone-400 font-bold">#{idx + 1}</span>
                          <span className="text-base font-black text-[#2C3E2D] dark:text-[#EDECE4]">{item.word}</span>
                        </div>
                        <button onClick={() => playTTS(item.word)} className="text-stone-400 text-xs">🔊 발음</button>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <button
                onClick={handleFinishList}
                className="w-full py-4 bg-[#2D5A27] text-white font-extrabold text-base rounded-2xl shadow-xl active:scale-95 transition-all mt-4"
              >
                🎉 전체 학습 완료! 훈련 단어장으로 이동 🚀
              </button>
            </div>
          )}

        </div>
      );
    }

    // ==========================================
    // 10. 훈련 단어장 통합 화면 (TrainingScreen)
    // - 플래시카드, 워드리콜, 스펠링 3종 모드 지원
    // ==========================================
    function TrainingScreen({ todayWords, words, trainingConfig, onComplete, onAddSun, onTabChange }) {
      const config = trainingConfig || { trainingType: 'recall', direction: 'en_to_ko', format: 'one_by_one', timerSec: 10 };
      const { trainingType, direction, format, timerSec } = config;

      // 단어 하나씩 모드 상태
      const [index, setIndex] = useState(0);
      const [selected, setSelected] = useState(null);
      const [isCorrect, setIsCorrect] = useState(null);
      const [timeLeft, setTimeLeft] = useState(timerSec);

      // 플래시카드 뒤집힘 상태
      const [flashFlipped, setFlashFlipped] = useState(false);

      // 스펠링 타이핑 입력값
      const [spellingInput, setSpellingInput] = useState('');

      // 리스트 풀이 상태
      const [listAnswers, setListAnswers] = useState({});
      const [listSubmitted, setListSubmitted] = useState(false);
      const [listScore, setListScore] = useState(0);

      const target = todayWords[index] || todayWords[0];

      // 객관식 4지선다 보기
      const options = useMemo(() => {
        if (!target) return [];
        const wrongs = words.filter(w => w.id !== target.id).sort(() => 0.5 - Math.random()).slice(0, 3);
        return [target, ...wrongs].sort(() => 0.5 - Math.random());
      }, [target, words]);

      // 타이머 이펙트
      useEffect(() => {
        if (format !== 'one_by_one' || timerSec === 0 || selected !== null) return;
        setTimeLeft(timerSec);
        const timer = setInterval(() => {
          setTimeLeft(prev => {
            if (prev <= 1) {
              clearInterval(timer);
              setSelected('TIMEOUT');
              setIsCorrect(false);
              return 0;
            }
            return prev - 1;
          });
        }, 1000);
        return () => clearInterval(timer);
      }, [index, format, timerSec, selected]);

      // 워드리콜 선택
      const handleRecallChoice = (opt) => {
        if (selected !== null) return;
        setSelected(opt.id);
        const ok = opt.id === target.id;
        setIsCorrect(ok);
        if (ok) onAddSun(1);
      };

      // 스펠링 확인
      const handleSpellingCheck = (e) => {
        e.preventDefault();
        const expected = direction === 'en_to_ko' ? target.meaning : target.word;
        const ok = spellingInput.trim().toLowerCase() === expected.toLowerCase();
        setIsCorrect(ok);
        setSelected('SUBMITTED');
        if (ok) onAddSun(1);
      };

      // 다음 문제 이동
      const handleNextOne = () => {
        setSelected(null);
        setIsCorrect(null);
        setFlashFlipped(false);
        setSpellingInput('');
        if (index + 1 < todayWords.length) {
          setIndex(index + 1);
        } else {
          onComplete();
          alert("🎉 훈련을 완료했습니다! (출석 인정 & ☀️ 햇살 획득)");
          onTabChange('home');
        }
      };

      // 리스트 채점
      const handleListSubmit = () => {
        let correctCnt = 0;
        todayWords.forEach(w => {
          if (listAnswers[w.id] === w.id) correctCnt++;
        });
        setListScore(correctCnt);
        setListSubmitted(true);
        onAddSun(correctCnt);
        onComplete();
      };

      if (!target) return <div className="p-10">단어가 없습니다.</div>;

      return (
        <div className="p-5 pb-8 space-y-5 animate-fadeIn">
          {/* 상단 헤더 */}
          <div className="flex items-center justify-between">
            <button
              onClick={() => onTabChange('home')}
              className="w-10 h-10 rounded-2xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 text-stone-700 dark:text-stone-200 font-black text-base shadow-sm hover:bg-stone-50 active:scale-95 transition-all flex items-center justify-center"
            >
              ←
            </button>
            <div className="text-center">
              <div className="text-xs font-black text-[#5F8D4E]">
                {trainingType === 'recall' && '🧠 워드 리콜'}
                {trainingType === 'flashcard' && '🗂️ 플래시카드'}
                {trainingType === 'spelling' && '✍️ 스펠링 훈련'}
                {' '}({direction === 'en_to_ko' ? '영➔한' : '한➔영'})
              </div>
              <div className="text-[10px] text-stone-400">
                {format === 'one_by_one' ? `${index + 1} / ${todayWords.length} 문항` : '시험지 리스트 풀이'}
              </div>
            </div>
            <div className="w-10" />
          </div>

          {/* ======================================================= */}
          {/* 1. 플래시카드 모드 */}
          {/* ======================================================= */}
          {trainingType === 'flashcard' && (
            <div className="space-y-6">
              <div
                onClick={() => setFlashFlipped(!flashFlipped)}
                className="h-80 rounded-3xl bg-white dark:bg-[#1D2A1F] border-2 border-[#A1C954] shadow-xl p-8 flex flex-col items-center justify-center text-center cursor-pointer transition-all hover:scale-[1.01]"
              >
                {!flashFlipped ? (
                  <div className="space-y-3">
                    <span className="text-4xl font-black text-[#2D5A27] dark:text-[#A1C954]">
                      {direction === 'en_to_ko' ? target.word : target.meaning}
                    </span>
                    <div className="text-xs text-stone-400">카드를 터치하면 뒤집힙니다 👆</div>
                  </div>
                ) : (
                  <div className="space-y-3 animate-fadeIn">
                    <span className="text-2xl font-black text-stone-700 dark:text-stone-200">
                      {direction === 'en_to_ko' ? target.meaning : target.word}
                    </span>
                    {target.example && <p className="text-xs text-stone-500 italic max-w-[260px]">"{target.example}"</p>}
                  </div>
                )}
              </div>

              <button
                onClick={() => {
                  onAddSun(1);
                  handleNextOne();
                }}
                className="w-full py-4 bg-[#2D5A27] text-white font-black text-base rounded-2xl shadow-lg"
              >
                {index + 1 === todayWords.length ? '플래시카드 완료 🎉' : '알고 있어요 (다음 카드) →'}
              </button>
            </div>
          )}

          {/* ======================================================= */}
          {/* 2. 워드리콜 모드 (하나씩 or 리스트) */}
          {/* ======================================================= */}
          {trainingType === 'recall' && format === 'one_by_one' && (
            <div className="space-y-5 animate-fadeIn">
              {timerSec > 0 && (
                <div className="space-y-1">
                  <div className="flex justify-between text-[11px] font-bold">
                    <span className="text-stone-400">남은 시간</span>
                    <span className={`font-black ${timeLeft <= 2 ? 'text-red-500 animate-ping' : 'text-[#2D5A27]'}`}>
                      ⏱️ {timeLeft}초
                    </span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-stone-200 dark:bg-stone-800 overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-[#2D5A27] to-[#A1C954] transition-all duration-1000"
                      style={{ width: `${(timeLeft / timerSec) * 100}%` }}
                    />
                  </div>
                </div>
              )}

              <div className="p-8 rounded-3xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 shadow-md text-center space-y-2">
                <div className="text-xs text-stone-400 font-bold">
                  {direction === 'en_to_ko' ? '알맞은 한글 뜻을 고르세요' : '알맞은 영어 단어를 고르세요'}
                </div>
                <div className="text-3xl font-black text-[#2D5A27] dark:text-[#A1C954]">
                  {direction === 'en_to_ko' ? target.word : target.meaning}
                </div>
              </div>

              <div className="space-y-2.5">
                {options.map((opt) => {
                  let style = "bg-white dark:bg-[#1D2A1F] border-stone-200 dark:border-stone-800 text-stone-700 dark:text-stone-300";
                  if (selected !== null) {
                    if (opt.id === target.id) style = "bg-emerald-500 text-white border-emerald-500 font-black";
                    else if (opt.id === selected) style = "bg-red-500 text-white border-red-500";
                  }
                  return (
                    <button
                      key={opt.id}
                      onClick={() => handleRecallChoice(opt)}
                      className={`w-full p-4 rounded-2xl border text-left font-bold text-sm transition-all ${style}`}
                    >
                      {direction === 'en_to_ko' ? opt.meaning : opt.word}
                    </button>
                  );
                })}
              </div>

              {selected !== null && (
                <div className="space-y-3 animate-scaleUp">
                  <div className={`p-3 text-center rounded-2xl text-xs font-bold ${
                    isCorrect ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {isCorrect ? '🎉 정답입니다! ☀️ +1 햇살 획득!' : `오답입니다. 정답: [${direction === 'en_to_ko' ? target.meaning : target.word}]`}
                  </div>
                  <button
                    onClick={handleNextOne}
                    className="w-full py-4 bg-[#2D5A27] text-white font-black text-base rounded-2xl shadow-lg"
                  >
                    {index + 1 === todayWords.length ? '훈련 완료 🏁' : '다음 문제 풀기 →'}
                  </button>
                </div>
              )}
            </div>
          )}

          {/* 리스트 시험지 모드 */}
          {trainingType === 'recall' && format === 'list' && (
            <div className="space-y-5 animate-fadeIn">
              <div className="space-y-4">
                {todayWords.map((item, idx) => {
                  const itemOpts = [item, ...words.filter(w => w.id !== item.id).slice(0, 3)].sort((a, b) => a.id - b.id);
                  return (
                    <div key={item.id} className="p-4 rounded-2xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 space-y-2">
                      <div className="flex justify-between text-xs">
                        <span className="font-bold text-stone-400">문항 #{idx + 1}</span>
                        {listSubmitted && (
                          <span className={`font-bold ${listAnswers[item.id] === item.id ? 'text-emerald-500' : 'text-red-500'}`}>
                            {listAnswers[item.id] === item.id ? '정답 ✓' : '오답 ✕'}
                          </span>
                        )}
                      </div>
                      <div className="font-black text-base text-[#2D5A27] dark:text-[#A1C954]">
                        {direction === 'en_to_ko' ? item.word : item.meaning}
                      </div>
                      <div className="grid grid-cols-1 gap-1.5 text-xs">
                        {itemOpts.map(opt => {
                          const isSel = listAnswers[item.id] === opt.id;
                          return (
                            <button
                              key={opt.id}
                              type="button"
                              onClick={() => !listSubmitted && setListAnswers(p => ({ ...p, [item.id]: opt.id }))}
                              className={`p-2.5 rounded-xl border text-left ${
                                isSel ? 'bg-[#2D5A27] text-white' : 'bg-stone-50 dark:bg-stone-800 text-stone-700 dark:text-stone-300'
                              }`}
                            >
                              {direction === 'en_to_ko' ? opt.meaning : opt.word}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  );
                })}
              </div>

              {!listSubmitted ? (
                <button onClick={handleListSubmit} className="w-full py-4 bg-[#2D5A27] text-white font-black rounded-2xl shadow-lg">
                  📝 답안 제출 및 채점하기
                </button>
              ) : (
                <div className="p-5 rounded-2xl bg-white dark:bg-[#1D2A1F] text-center space-y-2 border">
                  <div className="font-black text-lg">{todayWords.length}문항 중 {listScore}개 정답!</div>
                  <button onClick={() => onTabChange('home')} className="w-full py-3 bg-[#2D5A27] text-white font-bold rounded-xl">
                    홈으로 이동
                  </button>
                </div>
              )}
            </div>
          )}

          {/* ======================================================= */}
          {/* 3. 스펠링 타이핑 모드 */}
          {/* ======================================================= */}
          {trainingType === 'spelling' && (
            <div className="space-y-6 animate-fadeIn">
              <div className="p-8 rounded-3xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 shadow-md text-center space-y-2">
                <div className="text-xs text-stone-400 font-bold">의미를 보고 알맞은 철자를 입력하세요</div>
                <div className="text-2xl font-black text-[#2D5A27] dark:text-[#A1C954]">
                  {direction === 'en_to_ko' ? target.meaning : target.word}
                </div>
                <div className="text-xs text-stone-500 italic">
                  힌트: {(direction === 'en_to_ko' ? target.word : target.meaning)[0]}***
                </div>
              </div>

              <form onSubmit={handleSpellingCheck} className="space-y-3">
                <input
                  type="text"
                  required
                  value={spellingInput}
                  onChange={(e) => setSpellingInput(e.target.value)}
                  placeholder="철자 입력..."
                  className="w-full p-4 rounded-2xl border text-center font-bold text-lg focus:outline-none focus:ring-2 focus:ring-[#2D5A27] bg-white dark:bg-[#1D2A1F]"
                />

                {selected === null ? (
                  <button type="submit" className="w-full py-4 bg-[#2D5A27] text-white font-black rounded-2xl shadow-lg">
                    정답 확인 ✓
                  </button>
                ) : (
                  <div className="space-y-3 animate-scaleUp">
                    <div className={`p-3 text-center rounded-2xl text-xs font-bold ${
                      isCorrect ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {isCorrect ? '🎉 정답입니다! ☀️ +1 햇살 획득!' : `오답입니다. 정답: [${direction === 'en_to_ko' ? target.word : target.meaning}]`}
                    </div>
                    <button
                      type="button"
                      onClick={handleNextOne}
                      className="w-full py-4 bg-[#2D5A27] text-white font-black rounded-2xl shadow-lg"
                    >
                      {index + 1 === todayWords.length ? '스펠링 완료 🏁' : '다음 단어 →'}
                    </button>
                  </div>
                )}
              </form>
            </div>
          )}

        </div>
      );
    }

    // ==========================================
    // 11. [신규 화면] 커리큘럼 생성 (CreateCurriculumScreen)
    // ==========================================
    function CreateCurriculumScreen({ onSave, onTabChange }) {
      const [name, setName] = useState('수능 1등급 대비반');
      const [bookId, setBookId] = useState('essential_2000');
      const [dailyGoal, setDailyGoal] = useState(20);
      const [days, setDays] = useState(['월', '화', '수', '목', '금']);
      const [crit, setCrit] = useState(['vocab_study', 'recall']);

      const handleCreate = (e) => {
        e.preventDefault();
        if (!name.trim()) return alert("커리큘럼 이름을 입력해주세요.");
        if (days.length === 0) return alert("학습 요일을 하루 이상 선택해주세요.");
        if (crit.length === 0) return alert("출석 인정 기준을 최소 하나 이상 선택해주세요.");

        const newCurr = {
          id: 'curr_' + Date.now(),
          name: name.trim(),
          bookId,
          dailyGoal: Number(dailyGoal),
          days,
          attendanceCriteria: crit,
          createdAt: new Date().toISOString()
        };
        onSave(newCurr);
      };

      return (
        <div className="p-5 pb-8 space-y-6 animate-fadeIn">
          <div className="flex items-center justify-between">
            <button
              onClick={() => onTabChange('home')}
              className="w-10 h-10 rounded-2xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 text-stone-700 dark:text-stone-200 font-black text-base shadow-sm hover:bg-stone-50 active:scale-95 transition-all flex items-center justify-center"
            >
              ←
            </button>
            <div className="text-base font-black text-[#2D5A27] dark:text-[#A1C954]">새 커리큘럼 생성</div>
            <div className="w-10" />
          </div>

          <form onSubmit={handleCreate} className="space-y-5 text-xs">
            {/* 1. 커리큘럼 이름 */}
            <div className="space-y-1.5">
              <label className="font-bold text-stone-700 dark:text-stone-300">커리큘럼 이름 *</label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="예: 수능 1등급 완성반"
                className="w-full p-3.5 rounded-2xl border bg-white dark:bg-[#1D2A1F] font-bold text-sm focus:outline-none focus:ring-2 focus:ring-[#2D5A27]"
              />
            </div>

            {/* 2. 단어장 선택 */}
            <div className="space-y-2">
              <label className="font-bold text-stone-700 dark:text-stone-300">단어장(Book) 선택</label>
              <div className="space-y-2">
                {BOOKS_DATA.map(b => (
                  <div
                    key={b.id}
                    onClick={() => setBookId(b.id)}
                    className={`p-3.5 rounded-2xl border-2 cursor-pointer flex items-center justify-between transition-all ${
                      bookId === b.id ? 'border-[#2D5A27] bg-[#FAF6EC] dark:bg-[#203624] shadow-sm' : 'border-stone-200 dark:border-stone-800 bg-white dark:bg-[#1D2A1F]'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{b.icon}</span>
                      <div>
                        <div className="font-bold text-xs text-[#2C3E2D] dark:text-[#EDECE4]">{b.title}</div>
                        <div className="text-[10px] text-stone-400">{b.subtitle}</div>
                      </div>
                    </div>
                    <span className={`text-xs ${bookId === b.id ? 'text-[#2D5A27] font-black' : 'text-stone-300'}`}>✓</span>
                  </div>
                ))}
              </div>
            </div>

            {/* 3. 하루 목표 단어 수 */}
            <div className="space-y-1.5">
              <label className="font-bold text-stone-700 dark:text-stone-300">하루 목표 단어 수</label>
              <div className="grid grid-cols-4 gap-2">
                {[20, 30, 40, 50].map(cnt => (
                  <button
                    key={cnt}
                    type="button"
                    onClick={() => setDailyGoal(cnt)}
                    className={`py-2.5 rounded-xl font-bold transition-all ${
                      dailyGoal === cnt ? 'bg-[#2D5A27] text-white shadow-md' : 'bg-white dark:bg-[#1D2A1F] border text-stone-600 dark:text-stone-300'
                    }`}
                  >
                    {cnt}개
                  </button>
                ))}
              </div>
            </div>

            {/* 4. 학습 요일 */}
            <div className="space-y-1.5">
              <label className="font-bold text-stone-700 dark:text-stone-300">학습 요일</label>
              <div className="flex justify-between gap-1">
                {['월', '화', '수', '목', '금', '토', '일'].map(d => {
                  const sel = days.includes(d);
                  return (
                    <button
                      key={d}
                      type="button"
                      onClick={() => setDays(sel ? days.filter(x => x !== d) : [...days, d])}
                      className={`w-10 h-10 rounded-xl font-bold ${
                        sel ? 'bg-[#5F8D4E] text-white' : 'bg-white dark:bg-[#1D2A1F] border text-stone-400'
                      }`}
                    >
                      {d}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* 5. 출석 기준 */}
            <div className="space-y-1.5">
              <label className="font-bold text-stone-700 dark:text-stone-300">출석 인정 기준</label>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { id: 'vocab_study', label: '학습 단어장 완료' },
                  { id: 'recall', label: '훈련 단어장 완료' },
                  { id: 'flashcard', label: '플래시카드 완료' },
                  { id: 'spelling', label: '스펠링 훈련 완료' }
                ].map(item => {
                  const checked = crit.includes(item.id);
                  return (
                    <div
                      key={item.id}
                      onClick={() => setCrit(checked ? crit.filter(x => x !== item.id) : [...crit, item.id])}
                      className={`p-2.5 rounded-xl border flex items-center justify-between cursor-pointer ${
                        checked ? 'border-[#2D5A27] bg-[#E8F5E9] dark:bg-[#1b3820] text-[#2D5A27] font-bold' : 'border-stone-200 dark:border-stone-800 bg-white dark:bg-[#1D2A1F] text-stone-400'
                      }`}
                    >
                      <span>{item.label}</span>
                      <span>{checked ? '✓' : ''}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            <button
              type="submit"
              className="w-full py-4 bg-[#2D5A27] text-white font-black text-sm rounded-2xl shadow-xl active:scale-95 transition-all mt-4"
            >
              ➕ 커리큘럼 생성 완료 🚀
            </button>
          </form>
        </div>
      );
    }

    // ==========================================
    // 12. [신규 화면] 나의 커리큘럼 목록 (MyCurriculumsScreen)
    // ==========================================
    function MyCurriculumsScreen({ curriculums, activeCurriculumId, onSelect, onDelete, onTabChange }) {
      return (
        <div className="p-5 pb-8 space-y-6 animate-fadeIn">
          <div className="flex items-center justify-between">
            <button
              onClick={() => onTabChange('home')}
              className="w-10 h-10 rounded-2xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 text-stone-700 dark:text-stone-200 font-black text-base shadow-sm hover:bg-stone-50 active:scale-95 transition-all flex items-center justify-center"
            >
              ←
            </button>
            <div className="text-base font-black text-[#2D5A27] dark:text-[#A1C954]">나의 커리큘럼 목록</div>
            <button
              onClick={() => onTabChange('create_curriculum')}
              className="px-3 py-1.5 rounded-xl bg-[#2D5A27] text-white font-bold text-xs"
            >
              ➕ 생성
            </button>
          </div>

          <div className="space-y-3">
            {curriculums.map(c => {
              const book = BOOKS_DATA.find(b => b.id === c.bookId) || BOOKS_DATA[0];
              const isActive = c.id === activeCurriculumId;

              return (
                <div
                  key={c.id}
                  className={`p-5 rounded-3xl border-2 transition-all space-y-3 ${
                    isActive
                      ? 'border-[#2D5A27] bg-[#FAF6EC] dark:bg-[#203624] dark:border-[#A1C954] shadow-md'
                      : 'border-stone-200 dark:border-stone-800 bg-white dark:bg-[#1D2A1F]'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-xl">{book.icon}</span>
                      <div>
                        <div className="font-black text-sm text-[#2C3E2D] dark:text-[#EDECE4]">{c.name}</div>
                        <div className="text-[10px] text-stone-400">{book.title} • 하루 {c.dailyGoal}단어</div>
                      </div>
                    </div>
                    {isActive ? (
                      <span className="px-2.5 py-1 rounded-full bg-[#2D5A27] text-white font-black text-[10px]">
                        현재 학습 중 ✓
                      </span>
                    ) : (
                      <button
                        onClick={() => onSelect(c.id)}
                        className="px-2.5 py-1 rounded-full bg-stone-100 dark:bg-stone-800 text-stone-600 dark:text-stone-300 font-bold text-[10px]"
                      >
                        선택하기
                      </button>
                    )}
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-stone-100 dark:border-stone-800 text-[11px] text-stone-400">
                    <div>요일: {c.days?.join(', ')}</div>
                    {curriculums.length > 1 && (
                      <button
                        onClick={() => onDelete(c.id)}
                        className="text-red-500 hover:text-red-700 font-bold text-xs"
                      >
                        삭제 🗑️
                      </button>
                    )}
                  </div>
                </div>
              );
            })}

            {curriculums.length === 0 && (
              <div className="p-12 text-center text-stone-400 text-xs">
                생성된 커리큘럼이 없습니다. 우측 상단의 '➕ 생성' 버튼을 눌러보세요.
              </div>
            )}
          </div>
        </div>
      );
    }

    // ==========================================
    // 13. [독립 화면] 학습 현황 (StatsScreen)
    // ==========================================
    function StatsScreen({ onTabChange, treeInfo, words, dueWords, dailyProgress }) {
      const memorizedCount = words.filter(w => (w.stage || 0) >= 3).length;
      const learningCount = words.filter(w => (w.stage || 0) > 0 && (w.stage || 0) < 3).length;

      return (
        <div className="p-5 pb-8 space-y-6 animate-fadeIn">
          <div className="flex items-center justify-between">
            <button
              onClick={() => onTabChange('home')}
              className="w-10 h-10 rounded-2xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 text-stone-700 dark:text-stone-200 font-black text-base shadow-sm hover:bg-stone-50 active:scale-95 transition-all flex items-center justify-center"
            >
              ←
            </button>
            <h2 className="text-base font-black text-[#2D5A27] dark:text-[#A1C954]">📊 나의 학습 현황</h2>
            <div className="w-10" />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="p-4 rounded-3xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 space-y-1">
              <div className="text-xs text-stone-400 font-bold">완벽 암기 단어</div>
              <div className="text-2xl font-black text-[#2D5A27] dark:text-[#A1C954]">{memorizedCount}단어</div>
            </div>
            <div className="p-4 rounded-3xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 space-y-1">
              <div className="text-xs text-stone-400 font-bold">학습 중인 단어</div>
              <div className="text-2xl font-black text-amber-600">{learningCount}단어</div>
            </div>
            <div className="p-4 rounded-3xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 space-y-1">
              <div className="text-xs text-stone-400 font-bold">오늘 복습 대기</div>
              <div className="text-2xl font-black text-purple-600">{dueWords.length}단어</div>
            </div>
            <div className="p-4 rounded-3xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 space-y-1">
              <div className="text-xs text-stone-400 font-bold">누적 획득 햇살</div>
              <div className="text-2xl font-black text-amber-500">☀️ {treeInfo.sunlight}</div>
            </div>
          </div>
        </div>
      );
    }

    // ==========================================
    // 14. [독립 화면] 학습 랭킹 (RankingScreen)
    // ==========================================
    function RankingScreen({ onTabChange, treeInfo, currentUser }) {
      return (
        <div className="p-5 pb-8 space-y-6 animate-fadeIn">
          <div className="flex items-center justify-between">
            <button
              onClick={() => onTabChange('home')}
              className="w-10 h-10 rounded-2xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 text-stone-700 dark:text-stone-200 font-black text-base shadow-sm hover:bg-stone-50 active:scale-95 transition-all flex items-center justify-center"
            >
              ←
            </button>
            <h2 className="text-base font-black text-[#2D5A27] dark:text-[#A1C954]">🏆 학습 랭킹 명예의 전당</h2>
            <div className="w-10" />
          </div>

          <div className="p-6 rounded-3xl bg-gradient-to-r from-[#2D5A27] to-[#5F8D4E] text-white flex items-center justify-between shadow-lg">
            <div>
              <div className="text-[11px] text-[#A1C954] font-bold">나의 현재 순위</div>
              <div className="text-base font-black">상위 4% (전국 4위) 달성 중! 🎉</div>
            </div>
            <span className="text-2xl">👑</span>
          </div>
        </div>
      );
    }

    // ==========================================
    // 15. [독립 화면] 전체 단어 리스트 (WordListScreen)
    // ==========================================
    function WordListScreen({ onTabChange, allWords }) {
      const [searchQuery, setSearchQuery] = useState('');
      const [categoryFilter, setCategoryFilter] = useState('all');
      const [displayLimit, setDisplayLimit] = useState(50);

      const filteredWords = useMemo(() => {
        return allWords.filter(item => {
          if (categoryFilter !== 'all' && item.bookId !== categoryFilter) return false;
          if (!searchQuery.trim()) return true;
          const q = searchQuery.toLowerCase().trim();
          return item.word.toLowerCase().includes(q) || (item.meaning && item.meaning.includes(q));
        });
      }, [allWords, categoryFilter, searchQuery]);

      return (
        <div className="p-5 pb-8 space-y-5 animate-fadeIn">
          <div className="flex items-center justify-between">
            <button
              onClick={() => onTabChange('home')}
              className="w-10 h-10 rounded-2xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 text-stone-700 dark:text-stone-200 font-black text-base shadow-sm hover:bg-stone-50 active:scale-95 transition-all flex items-center justify-center"
            >
              ←
            </button>
            <h2 className="text-base font-black text-[#2D5A27] dark:text-[#A1C954]">
              📖 전체 단어 리스트 ({allWords.length})
            </h2>
            <div className="w-10" />
          </div>

          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="영단어 또는 한글 뜻 검색..."
            className="w-full p-3.5 rounded-2xl border bg-white dark:bg-[#1D2A1F] text-xs font-bold focus:outline-none focus:ring-2 focus:ring-[#2D5A27]"
          />

          <div className="space-y-2.5">
            {filteredWords.slice(0, displayLimit).map(item => (
              <div key={item.id} className="p-4 rounded-2xl bg-white dark:bg-[#1D2A1F] border flex items-center justify-between shadow-sm">
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs font-mono font-bold text-stone-400">#{item.id}</span>
                    <span className="font-black text-sm">{item.word}</span>
                    <button onClick={() => playTTS(item.word)} className="text-stone-400 text-xs">🔊</button>
                  </div>
                  <div className="text-xs font-bold text-[#2D5A27] dark:text-[#A1C954]">{item.meaning}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      );
    }

    // ==========================================
    // 16. [독립 화면] 커스텀 단어장 (CustomVocabScreen)
    // ==========================================
    function CustomVocabScreen({ onTabChange, customWords, onAddWord, onDeleteWord, onStartCustomStudy }) {
      const [newWord, setNewWord] = useState('');
      const [newMeaning, setNewMeaning] = useState('');

      const handleSubmit = (e) => {
        e.preventDefault();
        if (!newWord.trim() || !newMeaning.trim()) return alert("단어와 뜻을 입력하세요.");
        onAddWord({
          id: 'custom_' + Date.now(),
          word: newWord.trim(),
          meaning: newMeaning.trim(),
          example: `I practiced '${newWord.trim()}'.`,
          bookId: 'custom',
          stage: 0
        });
        setNewWord('');
        setNewMeaning('');
      };

      return (
        <div className="p-5 pb-8 space-y-6 animate-fadeIn">
          <div className="flex items-center justify-between">
            <button
              onClick={() => onTabChange('home')}
              className="w-10 h-10 rounded-2xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 text-stone-700 dark:text-stone-200 font-black text-base shadow-sm hover:bg-stone-50 active:scale-95 transition-all flex items-center justify-center"
            >
              ←
            </button>
            <h2 className="text-base font-black text-[#2D5A27] dark:text-[#A1C954]">✏️ 나만의 커스텀 단어장</h2>
            <div className="w-10" />
          </div>

          <form onSubmit={handleSubmit} className="p-4 rounded-2xl bg-white dark:bg-[#1D2A1F] border space-y-2 text-xs">
            <input
              type="text"
              required
              value={newWord}
              onChange={(e) => setNewWord(e.target.value)}
              placeholder="영단어 입력..."
              className="w-full p-2.5 rounded-xl border bg-stone-50 dark:bg-stone-800"
            />
            <input
              type="text"
              required
              value={newMeaning}
              onChange={(e) => setNewMeaning(e.target.value)}
              placeholder="한글 뜻 입력..."
              className="w-full p-2.5 rounded-xl border bg-stone-50 dark:bg-stone-800"
            />
            <button type="submit" className="w-full py-2.5 bg-[#2D5A27] text-white font-bold rounded-xl">
              ➕ 단어 등록
            </button>
          </form>

          <div className="space-y-2">
            {customWords.map(w => (
              <div key={w.id} className="p-3.5 rounded-2xl bg-white dark:bg-[#1D2A1F] border flex justify-between items-center text-xs">
                <div>
                  <span className="font-bold">{w.word}</span>: <span>{w.meaning}</span>
                </div>
                <button onClick={() => onDeleteWord(w.id)} className="text-red-500 font-bold">🗑️</button>
              </div>
            ))}
          </div>
        </div>
      );
    }

    // ==========================================
    // 17. 기능 튜토리얼 & 망각곡선 화면
    // ==========================================
    function TutorialScreen({ onTabChange }) {
      return (
        <div className="p-5 pb-8 space-y-6 animate-fadeIn">
          <div className="flex items-center justify-between">
            <button onClick={() => onTabChange('home')} className="w-10 h-10 rounded-2xl bg-white dark:bg-[#1D2A1F] border font-black">←</button>
            <h2 className="text-base font-black text-[#2D5A27] dark:text-[#A1C954]">💡 기능 튜토리얼</h2>
            <div className="w-10" />
          </div>
          <div className="p-5 rounded-3xl bg-white dark:bg-[#1D2A1F] border text-xs space-y-3">
            <p className="font-bold">1. 커리큘럼 생성 ➔ 2. 학습 단어장 암기 ➔ 3. 훈련 단어장 인출 ➔ 4. 보카 트리 햇살 획득!</p>
          </div>
        </div>
      );
    }

    function EbbinghausScreen({ onTabChange }) {
      return (
        <div className="p-5 pb-8 space-y-6 animate-fadeIn">
          <div className="flex items-center justify-between">
            <button onClick={() => onTabChange('home')} className="w-10 h-10 rounded-2xl bg-white dark:bg-[#1D2A1F] border font-black">←</button>
            <h2 className="text-base font-black text-[#2D5A27] dark:text-[#A1C954]">🧠 망각곡선 원리</h2>
            <div className="w-10" />
          </div>
          <div className="p-5 rounded-3xl bg-white dark:bg-[#1D2A1F] border text-xs space-y-3">
            <p>인간은 1일 만에 67%를 망각합니다. 보카하이의 상시 복습칸을 통해 영구 기억으로 잠그세요!</p>
          </div>
        </div>
      );
    }

    function TreeScreen({ treeInfo, onTabChange }) {
      return (
        <div className="p-5 pb-8 space-y-6 animate-fadeIn">
          <div className="flex items-center justify-between">
            <button onClick={() => onTabChange('home')} className="w-10 h-10 rounded-2xl bg-white dark:bg-[#1D2A1F] border font-black">←</button>
            <div className="text-base font-black text-[#2D5A27] dark:text-[#A1C954]">나의 텃밭 (보카 트리)</div>
            <div className="w-10" />
          </div>
          <div className="p-8 rounded-3xl bg-gradient-to-b from-[#FAF6EC] to-[#E8F5E9] dark:from-[#162418] dark:to-[#1e3822] text-center space-y-3 border">
            <div className="text-7xl animate-bounce">{treeInfo.currentStage.emoji}</div>
            <div className="font-black text-lg">Lv.{treeInfo.currentStage.level} {treeInfo.currentStage.name}</div>
            <div className="text-xs font-bold text-amber-600">☀️ 총 모은 햇살: {treeInfo.sunlight}개</div>
          </div>
        </div>
      );
    }

    // ==========================================
    // 18. 최상위 App 컴포넌트
    // ==========================================
    function App() {
      const [currentUser, setCurrentUser] = useState(null);
      const [currentTab, setCurrentTab] = useState('home');
      const [isDrawerOpen, setIsDrawerOpen] = useState(false);
      const [modalType, setModalType] = useState(null);
      const [floatingSun, setFloatingSun] = useState(false);
      const [theme, setTheme] = useState('light');

      // 학습 및 훈련 설정 팝업 상태
      const [isStudySetupOpen, setIsStudySetupOpen] = useState(false);
      const [studyInitialStyle, setStudyInitialStyle] = useState('card_flip');
      const [studyInitialMode, setStudyInitialMode] = useState('one_by_one');

      const [isTrainingSetupOpen, setIsTrainingSetupOpen] = useState(false);
      const [trainingConfig, setTrainingConfig] = useState({
        trainingType: 'recall',
        direction: 'en_to_ko',
        format: 'one_by_one',
        timerSec: 10
      });

      // 단어 데이터 상태
      const [allWords, setAllWords] = useState(FALLBACK_WORDS);
      const [customWords, setCustomWords] = useState([]);
      const [treeSunlight, setTreeSunlight] = useState(120);

      // 다중 커리큘럼 상태
      const [curriculums, setCurriculums] = useState([]);
      const [activeCurriculumId, setActiveCurriculumId] = useState(null);

      // 일일 진행 상황
      const [dailyProgress, setDailyProgress] = useState({
        studyCompleted: false,
        flashcardCompleted: false,
        recallCompleted: false,
        spellingCompleted: false,
        isAttendanceStamped: false
      });

      // [1] CSV 3,000단어 로드
      useEffect(() => {
        fetch('./voca_common.csv')
          .then(res => res.ok ? res.text() : Promise.reject())
          .then(csvText => {
            const lines = csvText.split('\n');
            const parsed = [];
            for (let i = 1; i < lines.length; i++) {
              const line = lines[i].trim();
              if (!line) continue;
              const parts = line.split(',');
              if (parts.length >= 7) {
                const idNum = parseInt(parts[0], 10) || i;
                parsed.push({
                  id: idNum,
                  word: parts[1],
                  pos: parts[2] || '',
                  meaning: parts[3] || parts[1],
                  stars: parts[4] || '',
                  bookId: parts[6] || (idNum <= 2000 ? 'essential_2000' : 'csat_1000'),
                  example: `I practiced '${parts[1]}'.`,
                  stage: 0
                });
              }
            }
            if (parsed.length > 0) setAllWords(parsed);
          })
          .catch(() => {});
      }, []);

      // [2] 사용자 세션 및 다중 커리큘럼 복원
      useEffect(() => {
        const savedSession = localStorage.getItem(STORAGE_PREFIX + 'SESSION');
        if (savedSession) {
          try {
            const u = JSON.parse(savedSession);
            setCurrentUser(u);

            const userCurrKey = STORAGE_PREFIX + u.id + '_CURRICULUMS';
            const savedCurrs = localStorage.getItem(userCurrKey);
            if (savedCurrs) {
              const parsedCurrs = JSON.parse(savedCurrs);
              setCurriculums(parsedCurrs);
              const savedActiveId = localStorage.getItem(STORAGE_PREFIX + u.id + '_ACTIVE_CURR');
              if (savedActiveId && parsedCurrs.some(c => c.id === savedActiveId)) {
                setActiveCurriculumId(savedActiveId);
              } else if (parsedCurrs.length > 0) {
                setActiveCurriculumId(parsedCurrs[0].id);
              }
            }
          } catch (e) {}
        }
        const savedCustom = localStorage.getItem(STORAGE_PREFIX + 'CUSTOM_WORDS');
        if (savedCustom) setCustomWords(JSON.parse(savedCustom));
        const savedSun = localStorage.getItem(STORAGE_PREFIX + 'SUNLIGHT');
        if (savedSun) setTreeSunlight(parseInt(savedSun, 10) || 120);
      }, []);

      // 활성 커리큘럼 객체
      const activeCurriculum = useMemo(() => {
        return curriculums.find(c => c.id === activeCurriculumId) || null;
      }, [curriculums, activeCurriculumId]);

      // 커리큘럼 생성 핸들러
      const handleCreateCurriculum = (newCurr) => {
        const nextList = [newCurr, ...curriculums];
        setCurriculums(nextList);
        setActiveCurriculumId(newCurr.id);
        if (currentUser) {
          localStorage.setItem(STORAGE_PREFIX + currentUser.id + '_CURRICULUMS', JSON.stringify(nextList));
          localStorage.setItem(STORAGE_PREFIX + currentUser.id + '_ACTIVE_CURR', newCurr.id);
        }
        alert("🎉 커리큘럼이 성공적으로 생성되었습니다!");
        setCurrentTab('home');
      };

      // 커리큘럼 선택 핸들러
      const handleSelectCurriculum = (id) => {
        setActiveCurriculumId(id);
        if (currentUser) {
          localStorage.setItem(STORAGE_PREFIX + currentUser.id + '_ACTIVE_CURR', id);
        }
      };

      // 커리큘럼 삭제 핸들러
      const handleDeleteCurriculum = (id) => {
        if (!confirm("이 커리큘럼을 삭제하시겠습니까?")) return;
        const nextList = curriculums.filter(c => c.id !== id);
        setCurriculums(nextList);
        if (activeCurriculumId === id) {
          setActiveCurriculumId(nextList.length > 0 ? nextList[0].id : null);
        }
        if (currentUser) {
          localStorage.setItem(STORAGE_PREFIX + currentUser.id + '_CURRICULUMS', JSON.stringify(nextList));
        }
      };

      // 햇살 추가
      const addSun = useCallback((count = 1) => {
        setTreeSunlight(prev => {
          const next = prev + count;
          localStorage.setItem(STORAGE_PREFIX + 'SUNLIGHT', next.toString());
          return next;
        });
        setFloatingSun(true);
        setTimeout(() => setFloatingSun(false), 1200);
      }, []);

      const toggleTheme = () => {
        const next = theme === 'light' ? 'dark' : 'light';
        setTheme(next);
        if (next === 'dark') document.documentElement.classList.add('dark');
        else document.documentElement.classList.remove('dark');
      };

      const handleAddCustomWord = (wordObj) => {
        const nextList = [wordObj, ...customWords];
        setCustomWords(nextList);
        localStorage.setItem(STORAGE_PREFIX + 'CUSTOM_WORDS', JSON.stringify(nextList));
      };

      const handleDeleteCustomWord = (id) => {
        const nextList = customWords.filter(w => w.id !== id);
        setCustomWords(nextList);
        localStorage.setItem(STORAGE_PREFIX + 'CUSTOM_WORDS', JSON.stringify(nextList));
      };

      // 오늘 학습할 단어 추출
      const todayWords = useMemo(() => {
        if (!activeCurriculum) return [];
        if (activeCurriculum.bookId === 'custom') {
          return customWords.length > 0 ? customWords.slice(0, activeCurriculum.dailyGoal) : FALLBACK_WORDS.slice(0, activeCurriculum.dailyGoal);
        }
        const filtered = allWords.filter(w => w.bookId === activeCurriculum.bookId);
        return filtered.slice(0, activeCurriculum.dailyGoal);
      }, [allWords, customWords, activeCurriculum]);

      const dueWords = useMemo(() => {
        return allWords.filter(w => (w.stage || 0) > 0 && (w.stage || 0) < 3).slice(0, 10);
      }, [allWords]);

      const treeInfo = useMemo(() => getTreeInfo(treeSunlight), [treeSunlight]);

      const handleLogout = () => {
        if (confirm("로그아웃 하시겠습니까?")) {
          localStorage.removeItem(STORAGE_PREFIX + 'SESSION');
          setCurrentUser(null);
          setIsDrawerOpen(false);
          setCurrentTab('home');
        }
      };

      if (!currentUser) {
        return (
          <AuthScreen
            onLoginSuccess={(u) => {
              setCurrentUser(u);
              localStorage.setItem(STORAGE_PREFIX + 'SESSION', JSON.stringify(u));
              const userCurrKey = STORAGE_PREFIX + u.id + '_CURRICULUMS';
              const savedCurrs = localStorage.getItem(userCurrKey);
              if (savedCurrs) {
                const parsed = JSON.parse(savedCurrs);
                setCurriculums(parsed);
                if (parsed.length > 0) setActiveCurriculumId(parsed[0].id);
              }
            }}
          />
        );
      }

      return (
        <div className="flex-1 flex flex-col justify-between">
          
          {floatingSun && (
            <div className="fixed top-20 right-8 z-50 pointer-events-none animate-bounce">
              <div className="px-3.5 py-1.5 rounded-full bg-[#A1C954] text-[#121B13] font-black text-sm shadow-2xl flex items-center gap-1.5 border border-white">
                <span>☀️</span> <span>+1 햇살 획득!</span>
              </div>
            </div>
          )}

          {/* ======================================================== */}
          {/* 좌측 사이드바 드로어 */}
          {/* ======================================================== */}
          {isDrawerOpen && (
            <div className="fixed inset-0 z-50 flex animate-fadeIn">
              <div onClick={() => setIsDrawerOpen(false)} className="fixed inset-0 bg-black/60 backdrop-blur-sm" />
              <div className="relative w-80 max-w-[85vw] h-full bg-[#FAF6EC] dark:bg-[#162418] border-r border-[#EADBCA] dark:border-[#28382a] p-6 flex flex-col justify-between shadow-2xl z-10 animate-slideRight overflow-y-auto">
                
                <div className="space-y-6">
                  <div className="flex items-center justify-between pb-4 border-b border-stone-200 dark:border-stone-800">
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">🌱</span>
                      <span className="font-black text-xl text-[#2D5A27] dark:text-[#A1C954] tracking-tight">
                        vocahigh
                      </span>
                    </div>
                    <button
                      onClick={() => setIsDrawerOpen(false)}
                      className="w-8 h-8 rounded-full bg-stone-200 dark:bg-stone-800 text-stone-600 dark:text-stone-300 font-bold flex items-center justify-center hover:bg-stone-300 transition-all"
                    >
                      ✕
                    </button>
                  </div>

                  {/* 1. 내 정보 */}
                  <div className="space-y-2">
                    <div className="text-xs font-black text-[#5F8D4E] dark:text-[#A1C954] tracking-wide px-1">
                      1. 내 정보
                    </div>
                    <div className="space-y-1 text-xs font-bold text-[#2C3E2D] dark:text-[#EDECE4]">
                      <button
                        onClick={() => {
                          setIsDrawerOpen(false);
                          if (!activeCurriculum) return alert("먼저 커리큘럼을 생성해 주세요.");
                          setIsStudySetupOpen(true);
                        }}
                        className="w-full text-left p-3 rounded-2xl hover:bg-black/5 dark:hover:bg-white/5 flex items-center gap-2.5 transition-all"
                      >
                        <span>▶</span> <span>이어 학습하기</span>
                      </button>
                      <button
                        onClick={() => { setIsDrawerOpen(false); setCurrentTab('stats'); }}
                        className="w-full text-left p-3 rounded-2xl hover:bg-black/5 dark:hover:bg-white/5 flex items-center gap-2.5 transition-all"
                      >
                        <span>📊</span> <span>학습 현황</span>
                      </button>
                      <button
                        onClick={() => { setIsDrawerOpen(false); setCurrentTab('ranking'); }}
                        className="w-full text-left p-3 rounded-2xl hover:bg-black/5 dark:hover:bg-white/5 flex items-center gap-2.5 transition-all"
                      >
                        <span>🏆</span> <span>학습 랭킹</span>
                      </button>
                      <button
                        onClick={() => { setIsDrawerOpen(false); setCurrentTab('tree'); }}
                        className="w-full text-left p-3 rounded-2xl hover:bg-black/5 dark:hover:bg-white/5 flex items-center gap-2.5 transition-all text-[#2D5A27] dark:text-[#A1C954]"
                      >
                        <span>🌳</span> <span>나의 텃밭 (보카 트리)</span>
                      </button>
                    </div>
                  </div>

                  {/* 2. 단어장 (커리큘럼 생성 & 나의 커리큘럼 분리) */}
                  <div className="space-y-2">
                    <div className="text-xs font-black text-[#5F8D4E] dark:text-[#A1C954] tracking-wide px-1">
                      2. 단어장
                    </div>
                    <div className="space-y-1 text-xs font-bold text-[#2C3E2D] dark:text-[#EDECE4]">
                      <button
                        onClick={() => { setIsDrawerOpen(false); setCurrentTab('create_curriculum'); }}
                        className="w-full text-left p-3 rounded-2xl hover:bg-black/5 dark:hover:bg-white/5 flex items-center gap-2.5 transition-all text-[#2D5A27] dark:text-[#A1C954]"
                      >
                        <span>⚙️</span> <span>커리큘럼 생성</span>
                      </button>
                      <button
                        onClick={() => { setIsDrawerOpen(false); setCurrentTab('my_curriculums'); }}
                        className="w-full text-left p-3 rounded-2xl hover:bg-black/5 dark:hover:bg-white/5 flex items-center gap-2.5 transition-all"
                      >
                        <span>📋</span> <span>나의 커리큘럼</span>
                      </button>
                      <button
                        onClick={() => { setIsDrawerOpen(false); setCurrentTab('word_list'); }}
                        className="w-full text-left p-3 rounded-2xl hover:bg-black/5 dark:hover:bg-white/5 flex items-center gap-2.5 transition-all"
                      >
                        <span>📖</span> <span>전체 단어 리스트</span>
                      </button>
                      <button
                        onClick={() => { setIsDrawerOpen(false); setCurrentTab('custom_vocab'); }}
                        className="w-full text-left p-3 rounded-2xl hover:bg-black/5 dark:hover:bg-white/5 flex items-center gap-2.5 transition-all"
                      >
                        <span>✏️</span> <span>커스텀 단어장</span>
                      </button>
                    </div>
                  </div>

                  {/* 3. 기능 설명 */}
                  <div className="space-y-2">
                    <div className="text-xs font-black text-[#5F8D4E] dark:text-[#A1C954] tracking-wide px-1">
                      3. 기능 설명
                    </div>
                    <div className="space-y-1 text-xs font-bold text-[#2C3E2D] dark:text-[#EDECE4]">
                      <button
                        onClick={() => { setIsDrawerOpen(false); setCurrentTab('tutorial'); }}
                        className="w-full text-left p-3 rounded-2xl hover:bg-black/5 dark:hover:bg-white/5 flex items-center gap-2.5 transition-all"
                      >
                        <span>💡</span> <span>기능 튜토리얼</span>
                      </button>
                      <button
                        onClick={() => { setIsDrawerOpen(false); setCurrentTab('ebbinghaus'); }}
                        className="w-full text-left p-3 rounded-2xl hover:bg-black/5 dark:hover:bg-white/5 flex items-center gap-2.5 transition-all"
                      >
                        <span>🧠</span> <span>망각곡선 원리</span>
                      </button>
                    </div>
                  </div>
                </div>

                {/* 하단 사용자 정보 */}
                <div className="pt-4 border-t border-stone-200 dark:border-stone-800 space-y-3">
                  <div className="flex items-center gap-3">
                    <img src={currentUser.avatar} alt="프로필" className="w-9 h-9 rounded-2xl border border-[#A1C954] bg-white" />
                    <div className="overflow-hidden">
                      <div className="font-extrabold text-xs text-[#2C3E2D] dark:text-[#EDECE4] truncate">{currentUser.name}</div>
                      <div className="text-[10px] text-stone-400 truncate max-w-[150px]">{currentUser.email}</div>
                    </div>
                  </div>

                  <button
                    onClick={toggleTheme}
                    className="w-full py-2.5 px-4 rounded-xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 flex items-center justify-between text-xs font-bold"
                  >
                    <span>화면 모드</span>
                    <span>{theme === 'light' ? '🌙 다크 모드로' : '☀️ 라이트 모드로'}</span>
                  </button>

                  <button
                    onClick={handleLogout}
                    className="w-full py-2.5 px-4 rounded-xl bg-red-500/10 text-red-600 hover:bg-red-500/20 flex items-center justify-center gap-1.5 text-xs font-extrabold transition-all"
                  >
                    <span>로그아웃</span> <span>👋</span>
                  </button>
                </div>

              </div>
            </div>
          )}

          {/* ======================================================== */}
          {/* 옵션 설정 모달 2종: 학습 단어장 팝업 & 훈련 단어장 팝업 */}
          {/* ======================================================== */}
          <StudySetupModal
            isOpen={isStudySetupOpen}
            onClose={() => setIsStudySetupOpen(false)}
            onStart={(chosenStyle, chosenMode) => {
              setStudyInitialStyle(chosenStyle);
              setStudyInitialMode(chosenMode);
              setCurrentTab('study');
            }}
          />

          <TrainingSetupModal
            isOpen={isTrainingSetupOpen}
            onClose={() => setIsTrainingSetupOpen(false)}
            onStart={(configObj) => {
              setTrainingConfig(configObj);
              setCurrentTab('training');
            }}
          />

          {/* ======================================================== */}
          {/* 메인 화면 뷰 컨텐츠 (하단 메뉴 바 삭제됨) */}
          {/* ======================================================== */}
          <main className="flex-1">
            {currentTab === 'home' && (
              <HomeScreen
                currentUser={currentUser}
                curriculums={curriculums}
                activeCurriculum={activeCurriculum}
                onSelectCurriculum={handleSelectCurriculum}
                treeInfo={treeInfo}
                todayWords={todayWords}
                dueWords={dueWords}
                dailyProgress={dailyProgress}
                onTabChange={setCurrentTab}
                onOpenDrawer={() => setIsDrawerOpen(true)}
                onOpenModal={setModalType}
                onRequestStudySetup={() => setIsStudySetupOpen(true)}
                onRequestTrainingSetup={() => setIsTrainingSetupOpen(true)}
              />
            )}

            {currentTab === 'create_curriculum' && (
              <CreateCurriculumScreen
                onSave={handleCreateCurriculum}
                onTabChange={setCurrentTab}
              />
            )}

            {currentTab === 'my_curriculums' && (
              <MyCurriculumsScreen
                curriculums={curriculums}
                activeCurriculumId={activeCurriculumId}
                onSelect={handleSelectCurriculum}
                onDelete={handleDeleteCurriculum}
                onTabChange={setCurrentTab}
              />
            )}

            {currentTab === 'stats' && (
              <StatsScreen
                onTabChange={setCurrentTab}
                treeInfo={treeInfo}
                words={allWords}
                dueWords={dueWords}
                dailyProgress={dailyProgress}
              />
            )}

            {currentTab === 'ranking' && (
              <RankingScreen
                onTabChange={setCurrentTab}
                treeInfo={treeInfo}
                currentUser={currentUser}
              />
            )}

            {currentTab === 'tree' && (
              <TreeScreen treeInfo={treeInfo} onTabChange={setCurrentTab} />
            )}

            {currentTab === 'word_list' && (
              <WordListScreen onTabChange={setCurrentTab} allWords={allWords} />
            )}

            {currentTab === 'custom_vocab' && (
              <CustomVocabScreen
                onTabChange={setCurrentTab}
                customWords={customWords}
                onAddWord={handleAddCustomWord}
                onDeleteWord={handleDeleteCustomWord}
                onStartCustomStudy={() => {
                  if (!activeCurriculum) return alert("먼저 커리큘럼을 생성해 주세요.");
                  setIsStudySetupOpen(true);
                }}
              />
            )}

            {currentTab === 'tutorial' && (
              <TutorialScreen onTabChange={setCurrentTab} />
            )}

            {currentTab === 'ebbinghaus' && (
              <EbbinghausScreen onTabChange={setCurrentTab} />
            )}

            {/* 학습 단어장 (3가지 암기 스타일 지원) */}
            {currentTab === 'study' && (
              <StudyScreen
                todayWords={todayWords}
                initialStyle={studyInitialStyle}
                initialMode={studyInitialMode}
                onComplete={() => setDailyProgress(prev => ({ ...prev, studyCompleted: true }))}
                onAddSun={addSun}
                onTabChange={setCurrentTab}
                onGoToTraining={() => setIsTrainingSetupOpen(true)}
              />
            )}

            {/* 훈련 단어장 (플래시카드, 워드리콜, 스펠링 3종 통합) */}
            {currentTab === 'training' && (
              <TrainingScreen
                todayWords={todayWords}
                words={allWords}
                trainingConfig={trainingConfig}
                onComplete={() => setDailyProgress(prev => ({ ...prev, recallCompleted: true }))}
                onAddSun={addSun}
                onTabChange={setCurrentTab}
              />
            )}

            {currentTab === 'review' && (
              <div className="p-5 pb-8 space-y-6 animate-fadeIn">
                <div className="flex items-center justify-between">
                  <button
                    onClick={() => setCurrentTab('home')}
                    className="w-10 h-10 rounded-2xl bg-white dark:bg-[#1D2A1F] border border-stone-200 dark:border-stone-800 text-stone-700 dark:text-stone-200 font-black text-base shadow-sm hover:bg-stone-50 active:scale-95 transition-all flex items-center justify-center"
                  >
                    ←
                  </button>
                  <div className="text-base font-black text-[#2D5A27] dark:text-[#A1C954]">
                    🧠 에빙하우스 망각곡선 복습
                  </div>
                  <div className="w-10" />
                </div>

                <div className="p-6 rounded-3xl bg-[#FAF6EC] dark:bg-[#162418] border border-[#EADBCA] dark:border-[#28382a] space-y-2">
                  <div className="font-bold text-sm text-[#2D5A27] dark:text-[#A1C954]">
                    {dueWords.length > 0 ? "에빙하우스 망각곡선 복습 대기" : "현재 복습할 단어가 없습니다"}
                  </div>
                  <p className="text-xs text-stone-500 dark:text-stone-400">
                    {dueWords.length > 0
                      ? "망각 직전의 단어를 복습하여 영구 기억으로 안전하게 고정시킵니다."
                      : "모든 단어가 장기 기억 안전권에 있습니다. 새로운 단어를 학습해보세요!"}
                  </p>
                </div>

                <div className="p-4 rounded-2xl bg-white dark:bg-[#1D2A1F] border flex justify-between text-sm font-bold">
                  <span>오늘 복습 대상 단어</span>
                  <span className="text-[#2D5A27] dark:text-[#A1C954]">{dueWords.length}단어</span>
                </div>

                {dueWords.length > 0 ? (
                  <button
                    onClick={() => setIsTrainingSetupOpen(true)}
                    className="w-full py-4 bg-[#2D5A27] text-white font-extrabold text-base rounded-2xl shadow-lg active:scale-95 transition-all"
                  >
                    ⚡ 지금 훈련 단어장으로 복습하기
                  </button>
                ) : (
                  <button
                    onClick={() => setCurrentTab('home')}
                    className="w-full py-4 bg-stone-200 dark:bg-stone-800 text-stone-700 dark:text-stone-300 font-bold text-sm rounded-2xl"
                  >
                    홈으로 돌아가기 🏠
                  </button>
                )}
              </div>
            )}
          </main>

          {/* ======================================================== */}
          {/* Supabase DB 연동 상태 모달 */}
          {/* ======================================================== */}
          {modalType === 'db_status' && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fadeIn">
              <div className="w-full max-w-sm bg-white dark:bg-[#1D2A1F] rounded-3xl p-6 shadow-2xl space-y-4">
                <div className="flex justify-between items-center pb-2 border-b">
                  <h3 className="font-bold text-base text-[#2D5A27] dark:text-[#A1C954]">
                    ⚡ 구글 계정 및 Supabase DB 연동
                  </h3>
                  <button onClick={() => setModalType(null)} className="font-bold text-stone-500">✕</button>
                </div>

                <div className="space-y-3 text-xs">
                  <div className="p-3 rounded-2xl bg-emerald-50 dark:bg-emerald-950/40 border border-emerald-200 dark:border-emerald-800 space-y-1">
                    <div className="flex items-center gap-1.5 font-bold text-emerald-800 dark:text-emerald-300">
                      <span className="w-2 h-2 rounded-full bg-emerald-500" />
                      <span>정식 Supabase Auth 인증 연동됨</span>
                    </div>
                  </div>

                  <div className="space-y-1.5 text-stone-600 dark:text-stone-300">
                    <div className="flex justify-between py-1 border-b border-stone-100 dark:border-stone-800">
                      <span className="font-bold">로그인 계정:</span>
                      <span className="font-mono text-[11px] font-bold text-[#2D5A27] dark:text-[#A1C954]">{currentUser.email}</span>
                    </div>
                    <div className="flex justify-between py-1 border-b border-stone-100 dark:border-stone-800">
                      <span className="font-bold">고유 UUID:</span>
                      <span className="font-mono text-[10px] text-stone-400 truncate max-w-[170px]">{currentUser.id}</span>
                    </div>
                  </div>

                  <button
                    onClick={() => setModalType(null)}
                    className="w-full py-3 rounded-2xl bg-[#2D5A27] text-white font-bold"
                  >
                    확인 완료
                  </button>
                </div>
              </div>
            </div>
          )}

        </div>
      );
    }

    // React 18 마운트
    const rootElem = document.getElementById('root');
    const root = ReactDOM.createRoot(rootElem);
    root.render(<App />);
  </script>
</body>
</html>
'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(HTML_CONTENT)

print("[SUCCESS] index.html updated with multi-curriculum, bottom menu removal, and study/training enhancements!")
