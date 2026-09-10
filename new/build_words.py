import re
import json

with open('data.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 객체 파싱
items = []
pattern = re.compile(r'id:\s*"([^"]+)",\s*bookId:\s*"([^"]+)",\s*word:\s*"([^"]+)",\s*meaning:\s*"([^"]+)"')
for match in pattern.finditer(text):
    bid, bbook, bword, bmean = match.groups()
    items.append({
        'id': bid,
        'bookId': bbook,
        'word': bword,
        'meaning': bmean,
        'stage': 0
    })

print(f"Extracted {len(items)} words from data.js")

# 추가 교육부 필수 영단어 100개 세트 생성
extra_common = [
    ("apple", "사과"), ("banana", "바나나"), ("book", "책"), ("desk", "책상"), ("school", "학교"),
    ("teacher", "선생님"), ("student", "학생"), ("friend", "친구"), ("water", "물"), ("family", "가족"),
    ("house", "집"), ("car", "자동차"), ("tree", "나무"), ("flower", "꽃"), ("sun", "태양"),
    ("moon", "달"), ("star", "별"), ("sky", "하늘"), ("rain", "비"), ("wind", "바람"),
    ("music", "음악"), ("food", "음식"), ("bread", "빵"), ("milk", "우유"), ("coffee", "커피"),
    ("time", "시간"), ("day", "날, 하루"), ("night", "밤"), ("morning", "아침"), ("dream", "꿈"),
    ("hope", "희망"), ("love", "사랑"), ("peace", "평화"), ("smile", "미소"), ("heart", "마음, 심장"),
    ("light", "빛"), ("shadow", "그림자"), ("world", "세상, 세계"), ("earth", "지구, 땅"), ("ocean", "대양, 바다"),
    ("mountain", "산"), ("river", "강"), ("road", "길, 도로"), ("city", "도시"), ("village", "마을"),
    ("country", "나라, 국가"), ("people", "사람들"), ("child", "아이"), ("parent", "부모"), ("animal", "동물"),
    ("bird", "새"), ("dog", "개"), ("cat", "고양이"), ("fish", "물고기"), ("horse", "말"),
    ("flower", "꽃"), ("grass", "풀, 잔디"), ("forest", "숲"), ("garden", "정원"), ("season", "계절"),
    ("spring", "봄"), ("summer", "여름"), ("autumn", "가을"), ("winter", "겨울"), ("weather", "날씨"),
    ("cloud", "구름"), ("snow", "눈"), ("ice", "얼음"), ("fire", "불"), ("air", "공기"),
    ("energy", "에너지"), ("power", "힘, 권력"), ("life", "삶, 생명"), ("nature", "자연"), ("health", "건강"),
    ("body", "몸, 신체"), ("eye", "눈"), ("hand", "손"), ("foot", "발"), ("mind", "마음, 정신"),
    ("thought", "생각"), ("idea", "아이디어, 발상"), ("story", "이야기"), ("history", "역사"), ("future", "미래"),
    ("present", "현재, 선물"), ("memory", "기억, 추억"), ("truth", "진실"), ("fact", "사실"), ("problem", "문제"),
    ("solution", "해결책"), ("answer", "정답"), ("question", "질문"), ("voice", "목소리"), ("sound", "소리"),
    ("color", "색깔"), ("picture", "그림, 사진"), ("art", "예술"), ("science", "과학"), ("nature", "자연")
]

for idx, (w, m) in enumerate(extra_common, 1):
    items.append({
        'id': f'w-voca-{idx}',
        'bookId': 'voca_3000',
        'word': w,
        'meaning': m,
        'stage': 0
    })

print(f"Total built words: {len(items)}")

with open('built_words.json', 'w', encoding='utf-8') as f:
    json.dump(items, f, ensure_ascii=False, indent=2)
