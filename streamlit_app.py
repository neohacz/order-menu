import streamlit as st
import sqlite3

# 데이터베이스 초기화
conn = sqlite3.connect('orders.db')
c = conn.cursor()

# 테이블 생성
c.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        family_name TEXT,
        menu_item TEXT,
        hot_or_iced TEXT,
        quantity INTEGER
    )
''')
conn.commit()

# Streamlit 대시보드
st.title("주문 취합 대시보드")

st.header("가족별 주문 입력")

# 가족 이름 입력
family_name = st.text_input("가족 이름")

# 메뉴 리스트
menu_list = [
    "none", "롱블랙", "플랫화이트", "카페 라떼", "모카", "바닐라 라떼", 
    "카라멜 마끼야또", "피치 에스프레소", "초코 라떼", "말차 라떼", 
    "레몬 에이드", "복숭아티", "레몬티", "루이보스", "케모마일", 
    "얼 그레이", "쿠키"
]

# 메뉴 선택
menu_item = st.selectbox("메뉴 선택", menu_list)

# HOT/ICED 선택
hot_or_iced = st.selectbox("HOT/ICED 선택", ["HOT", "ICED"])

# 수량 선택
quantity = st.selectbox("수량 선택", [1, 2, 3, 4])

# 주문 추가 버튼
if st.button("주문 추가"):
    if family_name and menu_item != "none":
        # 데이터베이스에 주문 추가
        c.execute('''
            INSERT INTO orders (family_name, menu_item, hot_or_iced, quantity)
            VALUES (?, ?, ?, ?)
        ''', (family_name, menu_item, hot_or_iced, quantity))
        conn.commit()
        st.success(f"{family_name}의 주문이 추가되었습니다.")
    else:
        st.error("가족 이름과 메뉴를 모두 선택해주세요.")

# 데이터베이스에서 주문 불러오기
c.execute('SELECT * FROM orders')
rows = c.fetchall()

# 메뉴별 주문 취합
menu_orders = {}
family_orders = {}
orders = {}

for row in rows:
    family, menu, hot_or_iced, quantity = row
    order = f"{hot_or_iced} {menu} {quantity}"
    
    # 가족별 주문 저장
    if family in orders:
        orders[family].append(order)
    else:
        orders[family] = [order]
    
    # 메뉴별 주문 수량 합산
    menu_key = f"{hot_or_iced} {menu}"
    if menu_key in menu_orders:
        menu_orders[menu_key] += quantity
    else:
        menu_orders[menu_key] = quantity
    
    # 메뉴별 주문한 가족 리스트 작성
    if menu_key in family_orders:
        if family not in family_orders[menu_key]:
            family_orders[menu_key].append(family)
    else:
        family_orders[menu_key] = [family]

st.header("취합된 주문 목록")
for menu, quantity in menu_orders.items():
    st.write(f"{menu} ({quantity})")

st.header("메뉴별 주문한 가족들")
for menu, families in family_orders.items():
    st.write(f"{menu}: {', '.join(families)}")

st.header("가족별 주문 목록")
for family, items in orders.items():
    st.write(f"{family}: {', '.join(items)}")

# 데이터베이스 연결 종료
conn.close()
