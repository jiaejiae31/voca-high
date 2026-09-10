-- ==============================================================================
-- 보카하이(vocahigh) 커리큘럼, 출석 기준 및 보카 트리 마이그레이션
-- 파일명: 002_create_curriculum_and_tree.sql
-- 설명: 커리큘럼(4종 출석 체크박스 포함), 보카 트리(햇살 ☀️ 및 7단계 레벨), 일일 출석 도장 관리
-- ==============================================================================

-- 1. 사용자 커리큘럼 테이블 (출석 체크 인정 기준 4종 체크박스 배열 포함)
CREATE TABLE IF NOT EXISTS public.user_curriculums (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    book_id VARCHAR(50) NOT NULL, -- 'middle_800', 'high_1200', 'toeic_1000'
    daily_goal INT NOT NULL DEFAULT 20, -- 하루 학습 목표 단어 수 (10, 20, 30, 50)
    study_days TEXT[] NOT NULL DEFAULT '{"월", "화", "수", "목", "금"}', -- 학습 요일 배열
    attendance_criteria TEXT[] NOT NULL DEFAULT '{"vocab_study", "recall"}', -- 출석 인정 기준 체크박스 ('vocab_study', 'flashcard', 'recall', 'spelling')
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_user_curriculum UNIQUE (user_id)
);

-- 2. 보카 트리 (Voca Tree) 성장 및 햇살 관리 테이블
-- 룰: 단어 하나당 무조건 햇살 1개 (☀️ +1)
CREATE TABLE IF NOT EXISTS public.user_trees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    sunlight_count INT NOT NULL DEFAULT 0, -- 누적 햇살 수 (단어당 +1)
    tree_level INT NOT NULL DEFAULT 1,     -- 1:씨앗(0~99), 2:새싹(100~299), 3:줄기(300~499), 4:묘목(500~999), 5:나무(1000~1999), 6:지혜나무(2000~4999), 7:세계수(5000+)
    last_sunlight_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT unique_user_tree UNIQUE (user_id)
);

-- 3. 일일 출석 도장 및 학습 진도 기록 테이블
CREATE TABLE IF NOT EXISTS public.daily_attendance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    study_date DATE NOT NULL DEFAULT CURRENT_DATE,
    study_completed BOOLEAN DEFAULT FALSE,      -- 학습 단어장 완료 여부
    flashcard_completed BOOLEAN DEFAULT FALSE,  -- 플래시카드 완료 여부
    recall_completed BOOLEAN DEFAULT FALSE,     -- 워드 리콜 완료 여부
    spelling_completed BOOLEAN DEFAULT FALSE,   -- 스펠링 훈련 완료 여부
    is_stamped BOOLEAN DEFAULT FALSE,           -- 출석 도장 날인 여부
    stamped_at TIMESTAMP WITH TIME ZONE,
    CONSTRAINT unique_user_daily_attendance UNIQUE (user_id, study_date)
);

-- 4. 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_curriculum_user ON public.user_curriculums(user_id);
CREATE INDEX IF NOT EXISTS idx_tree_user ON public.user_trees(user_id);
CREATE INDEX IF NOT EXISTS idx_attendance_user_date ON public.daily_attendance(user_id, study_date);

-- 5. Row Level Security (RLS) 활성화
ALTER TABLE public.user_curriculums ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_trees ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.daily_attendance ENABLE ROW LEVEL SECURITY;

-- 6. RLS 보안 정책 (본인 데이터만 완벽하게 접근/수정 가능)
CREATE POLICY "Users can manage their own curriculum" 
ON public.user_curriculums FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their own tree" 
ON public.user_trees FOR ALL USING (auth.uid() = user_id);

CREATE POLICY "Users can manage their own daily attendance" 
ON public.daily_attendance FOR ALL USING (auth.uid() = user_id);

-- 7. 햇살 적립 시 보카 트리 레벨 자동 계산 함수 및 트리거
CREATE OR REPLACE FUNCTION update_voca_tree_level()
RETURNS TRIGGER AS $$
BEGIN
    -- 누적 햇살 수치에 따른 7단계 레벨 계산
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

CREATE TRIGGER trigger_update_tree_level
BEFORE INSERT OR UPDATE ON public.user_trees
FOR EACH ROW
EXECUTE FUNCTION update_voca_tree_level();
