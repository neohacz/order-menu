import streamlit as st

# 초기 주문 데이터
orders = {}

# Streamlit 대시보드
st.title("주문 취합 대시보드")

st.header("가족별 주문 입력")

# 가족 이름 입력
family_name = st.text_input("가족 이름")

# 메뉴 입력
menu_items = st.text_area("메뉴 (예: 아이스아메리카노, 아이스아몬드라떼, 복숭아티2)")

# 주문 추가 버튼
if st.button("주문 추가"):
    if family_name and menu_items:
        orders[family_name] = menu_items.split(", ")
        st.success(f"{family_name}의 주문이 추가되었습니다.")
    else:
        st.error("가족 이름과 메뉴를 모두 입력해주세요.")

# 메뉴별 주문 취합
menu_orders = {}
family_orders = {}

for family, items in orders.items():
    for item in items:
        # 메뉴와 수량 분리
        if item[-1].isdigit():
            menu = item[:-1]
            quantity = int(item[-1])
        else:
            menu = item
            quantity = 1
        
        # 메뉴별 주문 수량 합산
        if menu in menu_orders:
            menu_orders[menu] += quantity
        else:
            menu_orders[menu] = quantity
        
        # 메뉴별 주문한 가족 리스트 작성
        if menu in family_orders:
            if family not in family_orders[menu]:
                family_orders[menu].append(family)
        else:
            family_orders[menu] = [family]

st.header("주문 목록")
for menu, quantity in menu_orders.items():
    st.write(f"{menu} ({quantity})")

st.header("메뉴별 주문한 가족들")
for menu, families in family_orders.items():
    st.write(f"{menu}: {', '.join(families)}")
