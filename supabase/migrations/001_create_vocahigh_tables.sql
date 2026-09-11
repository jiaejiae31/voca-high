-- ==============================================================================
-- 보카하이(vocahigh) 데이터베이스 초기 마이그레이션
-- 파일명: 001_create_vocahigh_tables.sql
-- 설명: 단어장, 망각곡선 복습 주기, 학습 이력 관리 및 강력한 RLS 보안 정책 적용
-- ==============================================================================

-- 1. 암호화 확장 기능 활성화 (보안 및 민감 데이터 암호화 지원)
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. 단어 카테고리/단어장 테이블
CREATE TABLE IF NOT EXISTS public.word_books (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. 단어 마스터 테이블 (그림, 예문, 유의어, 반의어 포함)
CREATE TABLE IF NOT EXISTS public.words (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_id UUID REFERENCES public.word_books(id) ON DELETE CASCADE,
    word VARCHAR(100) NOT NULL,
    meaning TEXT NOT NULL,
    phonetic VARCHAR(100),
    image_url TEXT,
    example_sentence TEXT,
    example_translation TEXT,
    synonyms TEXT[] DEFAULT '{}',
    antonyms TEXT[] DEFAULT '{}',
    difficulty_level VARCHAR(20) DEFAULT 'intermediate', -- basic, intermediate, advanced
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. 망각곡선 기반 사용자별 학습 및 복습 상태 테이블
CREATE TABLE IF NOT EXISTS public.user_word_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    word_id UUID REFERENCES public.words(id) ON DELETE CASCADE,
    
    -- 망각곡선 복습 주기 관련 필드
    repetition_stage INT DEFAULT 0,            -- 현재 복습 차수 (0: 미학습, 1: 1일후, 2: 3일후, 3: 7일후, 4: 14일후, 5: 30일후)
    last_reviewed_at TIMESTAMP WITH TIME ZONE, -- 최근 복습한 일시
    next_review_at TIMESTAMP WITH TIME ZONE,   -- 다음 예정 복습 일시
    is_overdue BOOLEAN DEFAULT FALSE,          -- 2일 이상 미복습 누적 여부
    
    -- 누적 정답/오답 통계
    correct_count INT DEFAULT 0,
    incorrect_count INT DEFAULT 0,
    total_reviews INT DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, word_id)
);

-- 5. 인덱스 생성 (빠른 복습 대상 단어 조회 및 성능 최적화)
CREATE INDEX IF NOT EXISTS idx_user_word_progress_review ON public.user_word_progress(user_id, next_review_at, is_overdue);
CREATE INDEX IF NOT EXISTS idx_words_book_id ON public.words(book_id);

-- 6. 보안 설정: Row Level Security (RLS) 활성화
ALTER TABLE public.word_books ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.words ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_word_progress ENABLE ROW LEVEL SECURITY;

-- 7. RLS 정책 정의 (본인 데이터만 조회/수정/삭제 가능)
CREATE POLICY "Users can only access their own word books" 
ON public.word_books 
FOR ALL 
USING (auth.uid() = user_id);

CREATE POLICY "Users can only view words in their accessible books" 
ON public.words 
FOR ALL 
USING (
    EXISTS (
        SELECT 1 FROM public.word_books 
        WHERE public.word_books.id = words.book_id 
        AND public.word_books.user_id = auth.uid()
    )
);

CREATE POLICY "Users can only manage their own progress" 
ON public.user_word_progress 
FOR ALL 
USING (auth.uid() = user_id);

-- 8. 2일 미복습 시 누적 상태 자동 갱신 트리거 함수
CREATE OR REPLACE FUNCTION check_overdue_words()
RETURNS TRIGGER AS $$
BEGIN
    -- 다음 복습 예정일로부터 2일(48시간) 초과 시 is_overdue를 TRUE로 설정
    IF NEW.next_review_at IS NOT NULL AND NEW.next_review_at + INTERVAL '2 days' < NOW() THEN
        NEW.is_overdue := TRUE;
    ELSE
        NEW.is_overdue := FALSE;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_overdue_status
BEFORE INSERT OR UPDATE ON public.user_word_progress
FOR EACH ROW
EXECUTE FUNCTION check_overdue_words();
