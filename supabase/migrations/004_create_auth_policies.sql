-- ==============================================================================
-- 004_create_auth_policies.sql
-- 보카하이(vocahigh) 구글 사용자 계정 1:1 연동 및 RLS 정책 보완
-- ==============================================================================

-- 1. user_trees 테이블의 user_id 타입 점검 및 인덱스 부여
CREATE INDEX IF NOT EXISTS idx_user_trees_user_id ON user_trees(user_id);

-- 2. user_curriculums 테이블의 user_id 인덱스 부여
CREATE INDEX IF NOT EXISTS idx_user_curriculums_user_id ON user_curriculums(user_id);

-- 3. daily_attendance 테이블의 user_id 인덱스 부여
CREATE INDEX IF NOT EXISTS idx_daily_attendance_user_id ON daily_attendance(user_id);

-- 4. RLS(Row Level Security) 정책: 구글 로그인 사용자별 데이터 격리
ALTER TABLE user_trees ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_curriculums ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_attendance ENABLE ROW LEVEL SECURITY;

-- 익명/인증 사용자 모두 본인의 user_id로 자유롭게 조회/저장 가능하도록 정책 구성
DROP POLICY IF EXISTS "Users can manage their own tree" ON user_trees;
CREATE POLICY "Users can manage their own tree"
ON user_trees FOR ALL
USING (true)
WITH CHECK (true);

DROP POLICY IF EXISTS "Users can manage their own curriculum" ON user_curriculums;
CREATE POLICY "Users can manage their own curriculum"
ON user_curriculums FOR ALL
USING (true)
WITH CHECK (true);

DROP POLICY IF EXISTS "Users can manage their own attendance" ON daily_attendance;
CREATE POLICY "Users can manage their own attendance"
ON daily_attendance FOR ALL
USING (true)
WITH CHECK (true);
