import sys
import zipfile
import xml.etree.ElementTree as ET
import csv
import re

xlsx_path = 'dataset/2022_교육부_기본어휘_3000(스샘).xlsx'

with zipfile.ZipFile(xlsx_path) as z:
    ss_xml = z.read('xl/sharedStrings.xml')
    ss_root = ET.fromstring(ss_xml)
    ns = {'ns': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    strings = [''.join([t.text for t in si.findall('.//ns:t', ns) if t.text]) for si in ss_root.findall('ns:si', ns)]
    
    s_xml = z.read('xl/worksheets/sheet1.xml')
    s_root = ET.fromstring(s_xml)
    rows = s_root.findall('.//ns:row', ns)
    
    words_data = []
    for r in rows[1:]:
        cells = r.findall('ns:c', ns)
        c_dict = {}
        for c in cells:
            ref = c.attrib.get('r', '')
            col = ''.join([ch for ch in ref if ch.isalpha()])
            t = c.attrib.get('t')
            v = c.find('ns:v', ns)
            val = v.text if v is not None else ''
            if t == 's' and val:
                val = strings[int(val)]
            c_dict[col] = (val, t)
            
        no = c_dict.get('A', ('', ''))[0]
        raw_text = c_dict.get('B', ('', ''))[0]
        lemma, lemma_t = c_dict.get('C', ('', ''))
        deriv = c_dict.get('D', ('', ''))[0]
        stars = c_dict.get('E', ('', ''))[0]
        note = c_dict.get('F', ('', ''))[0]
        
        # boolean 처리: false/true 등
        if lemma_t == 'b' or lemma in ('0', '1'):
            # B열(원본 텍스트)에서 단어 추출
            # e.g., 'false' -> 'false', 'true*' -> 'true'
            clean_b = re.sub(r'[\*\(\)].*$', '', raw_text).strip()
            if clean_b:
                lemma = clean_b
        
        words_data.append({
            'no': int(no) if no.isdigit() else 0,
            'raw': raw_text,
            'word': lemma,
            'deriv': deriv,
            'stars': stars,
            'note': note
        })

print(f"Total parsed: {len(words_data)}")

# 난이도 등급 매핑:
# 1등급: '**' (1200개) -> 초등 권장 기초
# 2등급: '*' (800개) -> 중고등 기본
# 3등급: '0' (1000개) -> 고등/수능 심화
level_rank = {'**': 1, '*': 2, '0': 3}

# 정렬: 1. 난이도등급, 2. 단어길이, 3. 알파벳
sorted_words = sorted(words_data, key=lambda x: (
    level_rank.get(x['stars'], 99),
    len(x['word']),
    x['word'].lower()
))

# 1~2000번: 필수 영단어 2000 (하위 2000개)
# 2001~3000번: 수능 필수 1000 (상위 1000개)
for idx, w in enumerate(sorted_words, 1):
    w['order_num'] = idx
    if idx <= 2000:
        w['category'] = '필수 영단어 2000'
        w['category_id'] = 'essential_2000'
    else:
        w['category'] = '수능 필수 1000'
        w['category_id'] = 'csat_1000'

# CSV 작성
with open('voca_common.csv', 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['순번', '표제어', '파생어', '원문', '교육부_별표', '난이도_분류', '교재_ID'])
    for w in sorted_words:
        writer.writerow([w['order_num'], w['word'], w['deriv'], w['raw'], w['stars'], w['category'], w['category_id']])

print("voca_common.csv created successfully!")
print("First 5 in voca_common.csv:")
for w in sorted_words[:5]:
    print(f"#{w['order_num']} {w['word']} ({w['stars']}) - {w['category']}")

print("\nBorder check (#1999 ~ #2002):")
for w in sorted_words[1998:2002]:
    print(f"#{w['order_num']} {w['word']} ({w['stars']}) - {w['category']}")

print("\nLast 5 in voca_common.csv:")
for w in sorted_words[-5:]:
    print(f"#{w['order_num']} {w['word']} ({w['stars']}) - {w['category']}")
