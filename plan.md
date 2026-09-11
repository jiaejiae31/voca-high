# 보카하이(vocahigh) Supabase 실시간 랭킹 연동 계획서 (plan.md)

## 1. 랭킹 연동 실패의 근본 원인 규명
Supabase 데이터베이스 및 REST API를 정밀 분석한 결과, 아래의 원인으로 인해 랭킹 연동이 실패하고 있었습니다:

1. **`user_trees.user_id` 컬럼 타입 불일치 (치명적 400 에러)**
   - Supabase DB의 `user_trees.user_id`는 **`UUID` (auth.users 외래키)** 타입입니다.
   - 현재 코드(`index.html:2875`)에서는 `user_id: currentUser.email || 'user'` 로 이메일 문자열을 보내어 Postgres에서 `22P02: invalid input syntax for type uuid` 에러가 발생, **단 1건의 햇살도 DB에 저장되지 못하고 있었습니다.**
2. **닉네임(`display_name`) 컬럼 누락 및 랭킹 표시 문제**
   - 현재 `user_trees`에는 `user_id`(UUID)만 저장되어 있어, 랭킹을 가져오면 난수형 UUID(`be99c7d8...`)만 노출되는 구조였습니다.
3. **Supabase Realtime Replication 활성화 필요**
   - 실시간 변경 사항을 브라우저에 실시간 푸시하기 위해 `ALTER PUBLICATION supabase_realtime ADD TABLE public.user_trees;` 설정이 필요합니다.
4. **점수 동기화(Sync) 로직 누락**
   - 로그인 시 기존에 저장된 점수를 Supabase에서 불러와 로컬과 맞추는 양방향 싱크 로직이 없었습니다.

---

## 2. 작업 계획

### Step 1. Supabase 마이그레이션 SQL 생성 (`007_enable_ranking_realtime.sql`)
- `user_trees`에 `display_name` 컬럼 추가 (`ADD COLUMN IF NOT EXISTS display_name VARCHAR(100)`)
- Realtime 복제 활성화: `ALTER PUBLICATION supabase_realtime ADD TABLE public.user_trees;`
- 전체 읽기/쓰기 RLS 정책 점검 및 최적화

### Step 2. 프론트엔드 핵심 로직 수정 (`index.html`)
1. **`handleRewardSunlight` 수정**:
   - `user_id`에 정상 UUID(`currentUser.id`)를 전달하여 DB에 즉시 저장되도록 수정.
   - `display_name` 함께 전송 (만약 DB에 컬럼이 아직 없어도 에러 없이 동작하도록 Fallback 방어 코드 적용).
   - 대량 햇살 획득 시를 위한 디바운스/배치 동기화 지원.
2. **로그인/앱 초기화 시 Supabase 점수 로드 & 양방향 동기화**:
   - 로그인 시 Supabase에서 내 점수를 즉시 가져와 로컬과 병합(더 큰 점수로 보존).
3. **실시간 랭킹 화면 (`RankingScreen`) 고도화**:
   - Supabase Realtime 채널(`postgres_changes`)을 통해 다른 사용자의 점수 변경이 실시간으로 반영되도록 구현.
   - 사용자명(닉네임/이메일 아이디)이 깔끔하게 표시되도록 렌더링 개선.
   - 상단에 `🟢 실시간 연동 중` 뱃지 및 수동 새로고침 피드백 애니메이션 추가.

---

## 3. 검증 및 확인
- 단어 학습 및 훈련으로 햇살 획득 시 Supabase DB에 실시간 upsert 확인.
- 랭킹 화면에서 1~3위 포디움 및 4위 이하 리스트, 내 순위가 정상 표출되는지 확인.
- Realtime 웹소켓 이벤트를 통한 실시간 갱신 확인.
