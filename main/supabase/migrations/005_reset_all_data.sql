-- ==============================================================================
-- 005_reset_all_data.sql
-- 보카하이(vocahigh) 데이터베이스 초기화(리셋) 쿼리
-- ==============================================================================

-- [방법 1] 테이블 구조(뼈대)는 그대로 두고, 안에 쌓인 데이터만 싹 비우기 (추천!)
TRUNCATE TABLE 
    daily_attendance,
    study_records,
    user_curriculums,
    user_trees,
    student_words
CASCADE;

-- [방법 2] 만약 기본 단어 데이터(words)까지 완전히 초기화하고 싶다면 아래 주석을 풀고 실행하세요:
-- TRUNCATE TABLE words CASCADE;

-- [참고] 회원가입된 구글 유저 목록(계정 자체)을 삭제하고 싶을 때는:
-- Supabase 대시보드 좌측 메뉴 [Authentication] -> [Users] 탭에서 
-- 삭제할 유저 오른쪽의 점 3개(...) 아이콘을 누르고 [Delete user]를 클릭하시면 됩니다.
