-- ==============================================================================
-- 보카하이(vocahigh) 커스텀 단어장 및 다중 커리큘럼 동기화 마이그레이션 (006_custom_books_and_sync.sql)
-- 설명: 커스텀 단어장(제목, 설명, 단어 목록) 저장 테이블 생성, 
--       다중 커리큘럼 저장을 위한 제약조건 완화,
--       전체 랭킹 조회를 위한 user_trees RLS 정책 보강
-- ==============================================================================

-- 1. 커스텀 단어장 메타정보 테이블
CREATE TABLE IF NOT EXISTS public.custom_vocab_books (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    title VARCHAR(150) NOT NULL,
    description TEXT,
    word_count INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. 커스텀 단어장 수록 단어 테이블
CREATE TABLE IF NOT EXISTS public.custom_vocab_words (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    book_id UUID REFERENCES public.custom_vocab_books(id) ON DELETE CASCADE,
    user_id TEXT NOT NULL,
    word VARCHAR(100) NOT NULL,
    meaning TEXT NOT NULL,
    part_of_speech VARCHAR(50) DEFAULT '기타',
    example_sentence TEXT,
    stage INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_custom_books_user ON public.custom_vocab_books(user_id);
CREATE INDEX IF NOT EXISTS idx_custom_words_book ON public.custom_vocab_words(book_id);
CREATE INDEX IF NOT EXISTS idx_custom_words_user ON public.custom_vocab_words(user_id);

-- 3. 다중 커리큘럼 지원을 위한 user_curriculums 제약조건 조정
-- 기존 UNIQUE (user_id) 제약조건이 있다면 제거하여 사용자가 여러 개의 커리큘럼을 생성할 수 있도록 지원
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.table_constraints 
        WHERE constraint_name = 'unique_user_curr' 
          AND table_name = 'user_curriculums'
    ) THEN
        ALTER TABLE public.user_curriculums DROP CONSTRAINT unique_user_curr;
    END IF;
END $$;

-- 4. 커리큘럼 이름 및 활성화 여부 컬럼 추가 (없는 경우)
ALTER TABLE public.user_curriculums 
ADD COLUMN IF NOT EXISTS title VARCHAR(100) DEFAULT '나의 단어 커리큘럼',
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- 5. RLS 보안 정책 적용
ALTER TABLE public.custom_vocab_books ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.custom_vocab_words ENABLE ROW LEVEL SECURITY;

-- 익명 키(Anon) 및 인증 사용자 모두 읽기/쓰기 허용 (보안 규칙 적용)
CREATE POLICY "Allow all on custom_vocab_books" ON public.custom_vocab_books FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "Allow all on custom_vocab_words" ON public.custom_vocab_words FOR ALL USING (true) WITH CHECK (true);

-- 6. 전체 사용자 랭킹 조회를 위해 user_trees SELECT 정책 보장
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'user_trees' AND policyname = 'Allow public select on user_trees'
    ) THEN
        CREATE POLICY "Allow public select on user_trees" ON public.user_trees FOR SELECT USING (true);
    END IF;
END $$;
