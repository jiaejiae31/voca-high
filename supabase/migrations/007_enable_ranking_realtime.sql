-- ==============================================================================
-- 보카하이(vocahigh) 랭킹 시스템 및 실시간 연동 고도화 (007_enable_ranking_realtime.sql)
-- 설명: 
--   1) user_trees 테이블에 사용자 닉네임(display_name) 컬럼 추가
--   2) Supabase Realtime 복제 활성화 (랭킹 실시간 자동 갱신)
--   3) 전체 사용자 랭킹 조회 및 본인 점수 업데이트를 위한 RLS 보안 정책 최적화
-- ==============================================================================

-- 1. user_trees 테이블에 닉네임(display_name) 컬럼 추가 (없는 경우에만)
ALTER TABLE public.user_trees 
ADD COLUMN IF NOT EXISTS display_name VARCHAR(100);

-- 2. 전체 랭킹 정렬 및 빠른 조회를 위한 복합 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_user_trees_sunlight_rank 
ON public.user_trees(sunlight_count DESC, updated_at DESC);

-- 3. Supabase Realtime 복제(Publication)에 user_trees 테이블 등록
-- 이를 통해 클라이언트 브라우저에서 postgres_changes 실시간 이벤트를 수신할 수 있습니다.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_publication_tables 
        WHERE pubname = 'supabase_realtime' 
          AND schemaname = 'public' 
          AND tablename = 'user_trees'
    ) THEN
        ALTER PUBLICATION supabase_realtime ADD TABLE public.user_trees;
    END IF;
END $$;

-- 4. RLS (Row Level Security) 정책 재점검 및 보강
ALTER TABLE public.user_trees ENABLE ROW LEVEL SECURITY;

-- 4-1. 전체 랭킹 조회는 로그인 사용자 및 게스트(Anon) 모두 허용
DROP POLICY IF EXISTS "Allow public select on user_trees" ON public.user_trees;
CREATE POLICY "Allow public select on user_trees" 
ON public.user_trees 
FOR SELECT 
USING (true);

-- 4-2. 점수 저장 및 갱신은 본인 계정(auth.uid() = user_id) 또는 Anon 키로 자유롭게 가능하도록 허용
DROP POLICY IF EXISTS "Allow all manage on user_trees" ON public.user_trees;
CREATE POLICY "Allow all manage on user_trees" 
ON public.user_trees 
FOR ALL 
USING (true) 
WITH CHECK (true);
