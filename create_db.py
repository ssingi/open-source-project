import sqlite3

# 데이터베이스 연결 (파일이 없으면 새로 생성됨)
conn = sqlite3.connect('travel.db')
cursor = conn.cursor()

# attractions 테이블 생성
cursor.execute('''
CREATE TABLE IF NOT EXISTS attractions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    city TEXT NOT NULL
)
''')

# 데이터 삽입
attractions_data = [
    ("도쿄타워", "도쿄"),
    ("아사쿠사", "도쿄"),
    ("시부야", "도쿄"),
    ("도톤보리", "오사카"),
    ("유니버설 스튜디오", "오사카"),
    ("기온", "교토"),
    ("금각사", "교토"),
    ("후시미이나리", "교토"),
    ("삿포로", "홋카이도"),
    ("오타루", "홋카이도"),
    ("후라노", "홋카이도"),
    ("츄라우미 수족관", "오키나와"),
    ("국제거리", "오키나와")
]

cursor.executemany('INSERT INTO attractions (name, city) VALUES (?, ?)', attractions_data)

# 변경 사항 저장 및 연결 종료
conn.commit()
conn.close()

print("데이터베이스와 테이블이 성공적으로 생성되었습니다.")