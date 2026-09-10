-- ==============================================================================
-- 보카하이(vocahigh) 원클릭 전체 통합 마이그레이션 (003_vocahigh_all_in_one.sql)
-- 설명: Supabase SQL Editor에 이 전체 내용을 그대로 복사하여 [Run] 버튼을 누르면
--       보카하이의 모든 테이블(단어장, 단어, 커리큘럼, 보카트리 7단계, 출석도장)과
--       자동 레벨업 트리거 및 보안 정책(RLS)이 한 번에 완벽히 생성됩니다.
-- ==============================================================================

-- 1. 암호화 확장 활성화
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. 단어장 테이블
CREATE TABLE IF NOT EXISTS public.word_books (
    id VARCHAR(50) PRIMARY KEY, -- 'middle_800', 'high_1200', 'toeic_1000'
    title VARCHAR(100) NOT NULL,
    subtitle TEXT,
    total_words INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. 기본 단어 마스터 테이블
CREATE TABLE IF NOT EXISTS public.words (
    id VARCHAR(50) PRIMARY KEY,
    book_id VARCHAR(50) REFERENCES public.word_books(id) ON DELETE CASCADE,
    word VARCHAR(100) NOT NULL,
    meaning TEXT NOT NULL,
    phonetic VARCHAR(100),
    part_of_speech VARCHAR(50),
    image_url TEXT,
    example_sentence TEXT,
    example_translation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. 사용자 커리큘럼 테이블 (출석 인정 기준 4종 체크박스 배열 포함)
CREATE TABLE IF NOT EXISTS public.user_curriculums (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL DEFAULT 'student_user',
    book_id VARCHAR(50) NOT NULL,
    daily_goal INT NOT NULL DEFAULT 20,
    study_days TEXT[] NOT NULL DEFAULT '{"월", "화", "수", "목", "금"}',
    attendance_criteria TEXT[] NOT NULL DEFAULT '{"vocab_study", "recall"}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_user_curr UNIQUE (user_id)
);

-- 5. 보카 트리 (Voca Tree) 성장 및 햇살 테이블
-- 룰: 단어 하나당 무조건 햇살 1개 (☀️ +1)
CREATE TABLE IF NOT EXISTS public.user_trees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL DEFAULT 'student_user',
    sunlight_count INT NOT NULL DEFAULT 0,
    tree_level INT NOT NULL DEFAULT 1,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_user_tree_record UNIQUE (user_id)
);

-- 6. 일일 출석 도장 테이블
CREATE TABLE IF NOT EXISTS public.daily_attendance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL DEFAULT 'student_user',
    study_date DATE NOT NULL DEFAULT CURRENT_DATE,
    study_completed BOOLEAN DEFAULT FALSE,
    flashcard_completed BOOLEAN DEFAULT FALSE,
    recall_completed BOOLEAN DEFAULT FALSE,
    spelling_completed BOOLEAN DEFAULT FALSE,
    is_stamped BOOLEAN DEFAULT FALSE,
    stamped_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT unique_user_att UNIQUE (user_id, study_date)
);

-- 7. 망각곡선 복습 진행도 테이블
CREATE TABLE IF NOT EXISTS public.user_word_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL DEFAULT 'student_user',
    word_id VARCHAR(50) NOT NULL,
    repetition_stage INT DEFAULT 0, -- 1일(1차), 7일(2차), 30일(3차)
    last_reviewed_at TIMESTAMP WITH TIME ZONE,
    next_review_at TIMESTAMP WITH TIME ZONE,
    is_overdue BOOLEAN DEFAULT FALSE,
    correct_count INT DEFAULT 0,
    incorrect_count INT DEFAULT 0,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_user_word_prog UNIQUE (user_id, word_id)
);

-- 8. 기본 단어장 초기 시드 데이터 등록
INSERT INTO public.word_books (id, title, subtitle, total_words) VALUES
('middle_800', '중학 필수 영단어 800', '기초를 탄탄하게 세우는 중등 교과 필수 어휘', 800),
('high_1200', '고교 수능 빈출 마스터 1200', '역대 모의고사 및 수능 1등급 핵심 빈출 어휘', 1200),
('toeic_1000', '토익/토플 실전 보카 1000', '실전 비즈니스 및 아카데믹 고득점 전략 어휘', 1000)
ON CONFLICT (id) DO NOTHING;

-- 9. 기본 핵심 단어 시드 데이터 등록
INSERT INTO public.words (id, book_id, word, meaning, phonetic, part_of_speech, image_url, example_sentence, example_translation) VALUES
('w-mid-1', 'middle_800', 'cherish', '소중히 여기다, 아끼다', '/ˈtʃer.ɪʃ/', '동사', 'https://images.unsplash.com/photo-1516589178581-6cd7833ae3b2?w=600&auto=format&fit=crop&q=80', 'I cherish the wonderful moments we spent together.', '나는 우리가 함께 보낸 소중한 순간들을 아낀다.'),
('w-mid-2', 'middle_800', 'courage', '용기, 담력', '/ˈkɝː.ɪdʒ/', '명사', 'https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=600&auto=format&fit=crop&q=80', 'It takes courage to stand up and speak the truth.', '일어서서 진실을 말하는 데는 용기가 필요하다.'),
('w-mid-3', 'middle_800', 'curious', '호기심이 많은, 신기한', '/ˈkjʊr.i.əs/', '형용사', 'https://images.unsplash.com/photo-1544717305-2782549b5136?w=600&auto=format&fit=crop&q=80', 'The curious puppy explored every corner of the yard.', '호기심 많은 강아지가 마당 구석구석을 탐험했다.'),
('w-high-1', 'high_1200', 'persistent', '끈기 있는, 지속적인', '/pərˈsɪs.tənt/', '형용사', 'https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=600&auto=format&fit=crop&q=80', 'Persistent efforts lead to great achievements.', '끈기 있는 노력은 위대한 성취로 이어진다.'),
('w-toeic-1', 'toeic_1000', 'feasible', '실현 가능한, 적절한', '/ˈfiː.zə.bəl/', '형용사', 'https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=600&auto=format&fit=crop&q=80', 'The proposal is financially feasible.', '그 제안은 재정적으로 실현 가능하다.')
ON CONFLICT (id) DO NOTHING;

-- 10. 햇살 누적에 따른 7단계 자동 레벨업 트리거 함수
CREATE OR REPLACE FUNCTION update_tree_level_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.sunlight_count >= 5000 THEN
        NEW.tree_level := 7; -- 불멸의 세계수
    ELSIF NEW.sunlight_count >= 2000 THEN
        NEW.tree_level := 6; -- 황금 지혜나무
    ELSIF NEW.sunlight_count >= 1000 THEN
        NEW.tree_level := 5; -- 보카 나무
    ELSIF NEW.sunlight_count >= 500 THEN
        NEW.tree_level := 4; -- 푸른 묘목
    ELSIF NEW.sunlight_count >= 300 THEN
        NEW.tree_level := 3; -- 어린 줄기
    ELSIF NEW.sunlight_count >= 100 THEN
        NEW.tree_level := 2; -- 새싹
    ELSE
        NEW.tree_level := 1; -- 씨앗
    END IF;
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_calc_tree_level ON public.user_trees;
CREATE TRIGGER trg_calc_tree_level
BEFORE INSERT OR UPDATE ON public.user_trees
FOR EACH ROW
EXECUTE FUNCTION update_tree_level_trigger();

-- 11. 누구나 안전하게 읽고 쓸 수 있도록 RLS 정책 완화 (Anon Key 지원)
ALTER TABLE public.word_books ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.words ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_curriculums ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_trees ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.daily_attendance ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_word_progress ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read word_books" ON public.word_books FOR SELECT USING (true);
CREATE POLICY "Allow public read words" ON public.words FOR SELECT USING (true);
CREATE POLICY "Allow all on user_curriculums" ON public.user_curriculums FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on user_trees" ON public.user_trees FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on daily_attendance" ON public.daily_attendance FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on user_word_progress" ON public.user_word_progress FOR ALL USING (true) WITH CHECK (true);
