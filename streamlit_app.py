import streamlit as st
import sqlite3

# 데이터베이스 초기화
conn = sqlite3.connect('orders.db', check_same_thread=False)  # check_same_thread=False 설정 추가
c = conn.cursor()

# 테이블 생성
c.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    "롱블랙 (아메리카노)", "플랫화이트", "카페 라떼", "모카", "바닐라 라떼", 
    "카라멜 마끼야또", "피치 에스프레소", "초코 라떼", "말차 라떼", 
    "레몬 에이드", "복숭아티", "레몬티", "루이보스", "케모마일", 
    "얼 그레이", "쿠키"
]

# 메뉴 선택
menu_item = st.selectbox("메뉴 선택", menu_list)

# HOT/ICED 선택 (쿠키가 아닌 경우에만)
if menu_item != "쿠키":
    hot_or_iced = st.selectbox("HOT/ICED 선택", ["HOT", "ICED"])
else:
    hot_or_iced = "N/A"  # 쿠키의 경우 HOT/ICED 선택 없음

# 수량 선택
quantity = st.selectbox("수량 선택", [1, 2, 3, 4])

# 주문 추가 버튼
if st.button("주문 추가"):
    if family_name:
        try:
            # 데이터베이스에 주문 추가
            c.execute('''
                INSERT INTO orders (family_name, menu_item, hot_or_iced, quantity)
                VALUES (?, ?, ?, ?)
            ''', (family_name, menu_item, hot_or_iced, quantity))
            conn.commit()
            st.success(f"{family_name}의 주문이 추가되었습니다.")
        except sqlite3.Error as e:
            conn.rollback()
            st.error(f"데이터베이스에 주문을 추가하는 중 오류가 발생했습니다: {e}")
    else:
        st.error("가족 이름을 입력해주세요.")

# 데이터베이스에서 주문 불러오기
try:
    c.execute('SELECT rowid, family_name, menu_item, hot_or_iced, quantity FROM orders')
    rows = c.fetchall()
except sqlite3.OperationalError as e:
    st.error(f"데이터베이스에서 데이터를 불러오는 중 오류가 발생했습니다: {e}")
    rows = []

# 메뉴별 주문 취합
menu_orders = {}
family_orders = {}
orders = {}

for row in rows:
    try:
        order_id, family, menu, hot_or_iced, quantity = row
        order = f"{hot_or_iced} {menu} {quantity}" if hot_or_iced != "N/A" else f"{menu} {quantity}"
        
        # 가족별 주문 저장
        if family in orders:
            orders[family].append((order_id, order))
        else:
            orders[family] = [(order_id, order)]
        
        # 메뉴별 주문 수량 합산
        menu_key = f"{hot_or_iced} {menu}" if hot_or_iced != "N/A" else menu
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
    except ValueError as e:
        st.error(f"데이터베이스에서 불러온 행의 구조가 예상과 다릅니다: {e}")

st.header("취합된 주문 목록")
for menu, quantity in menu_orders.items():
    st.write(f"{menu} ({quantity})")

st.header("메뉴별 주문한 가족들")
for menu, families in family_orders.items():
    st.write(f"{menu}: {', '.join(families)}")

st.header("가족별 주문 목록")
for family, items in orders.items():
    st.write(f"{family}:")
    for order_id, order in items:
        if st.button(f"삭제 {order}", key=f"delete_{order_id}"):
            try:
                # 데이터베이스에서 해당 주문 삭제
                c.execute('DELETE FROM orders WHERE rowid = ?', (order_id,))
                conn.commit()
                st.experimental_rerun()  # 페이지를 새로고침하여 변경사항 반영
            except sqlite3.Error as e:
                conn.rollback()
                st.error(f"데이터베이스에서 주문을 삭제하는 중 오류가 발생했습니다: {e}")

st.header("모든 주문을 삭제합니다.")
# 비밀번호 입력 필드
password = st.text_input("관리자 비밀번호를 입력하세요:", type="password")
if password == "1234":
    if st.button("초기화"):
        try:
            # 데이터베이스에서 모든 주문 삭제
            c.execute('DELETE FROM orders')
            conn.commit()
            st.success("모든 주문이 초기화되었습니다.")
            st.experimental_rerun()  # 페이지를 새로고침하여 변경사항 반영            
        except sqlite3.Error as e:
            conn.rollback()
            st.error(f"데이터베이스에서 주문을 초기화하는 중 오류가 발생했습니다: {e}")
else:
    st.warning("비밀번호를 입력하면 초기화를 할 수 있습니다.")

# 데이터베이스 연결 종료
conn.close()
