
import streamlit as st
import random
from collections import Counter

# 頁面設定 + icon
st.set_page_config(page_title="牌影", page_icon="logo.png")

# 顯示 logo
st.image("logo.png", width=200)

# 美化背景與按鈕樣式（黑色系）
st.markdown("""
<style>
body {
    background-color: #0f0f0f;
    color: #ffffff;
}
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #0f0f0f 0%, #1c1c1c 100%);
}
div.stButton > button {
    background-color: #333333;
    color: white;
    border-radius: 8px;
    font-size: 16px;
    padding: 8px 24px;
    border: 1px solid #555;
}
h1, h2, h3, h4, h5, h6, p, label {
    color: #e0e0e0;
}
div.stSlider > div > div {
    background: #555 !important;
}
</style>
""", unsafe_allow_html=True)

# 選牌區塊（改用 multiselect）
card_options = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
selected_cards = st.multiselect("請點選已開出的牌（可重複選擇）：", options=card_options * 32, max_selections=416)

if selected_cards:
    st.write("你已選擇：", " ".join(selected_cards))

simulations = st.slider("模擬次數", 1000, 20000, 10000, step=1000)

# 撲克邏輯
def get_card_value(card):
    if card in ['J', 'Q', 'K', '10']:
        return 0
    elif card == 'A':
        return 1
    else:
        return int(card)

def create_single_deck():
    return ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'] * 4

def create_shoe():
    return create_single_deck() * 8

def calculate_points(cards):
    return sum(get_card_value(card) for card in cards) % 10

def should_player_draw(player_points):
    return player_points <= 5

def should_banker_draw(banker_points, player_third_card):
    if player_third_card is None:
        return banker_points <= 5
    third_value = get_card_value(player_third_card)
    if banker_points <= 2:
        return True
    elif banker_points == 3:
        return third_value != 8
    elif banker_points == 4:
        return 2 <= third_value <= 7
    elif banker_points == 5:
        return 4 <= third_value <= 7
    elif banker_points == 6:
        return third_value in [6, 7]
    else:
        return False

def remove_used_cards(deck, used_cards):
    temp_deck = deck.copy()
    for card in used_cards:
        try:
            temp_deck.remove(card)
        except ValueError:
            continue
    return temp_deck

def simulate_round(deck):
    d = deck.copy()
    random.shuffle(d)
    player = [d.pop(), d.pop()]
    banker = [d.pop(), d.pop()]
    player_points = calculate_points(player)
    banker_points = calculate_points(banker)
    player_third = None
    banker_third = None

    if player_points < 8 and banker_points < 8:
        if should_player_draw(player_points):
            player_third = d.pop()
            player.append(player_third)
        if should_banker_draw(banker_points, player_third):
            banker_third = d.pop()
            banker.append(banker_third)

    final_p = calculate_points(player)
    final_b = calculate_points(banker)

    if final_p > final_b:
        return "閒贏"
    elif final_b > final_p:
        return "莊贏"
    else:
        return "和局"

def simulate_many_rounds(used_cards, simulations=10000):
    deck = create_shoe()
    deck = remove_used_cards(deck, used_cards)
    result_counter = Counter()

    for _ in range(simulations):
        try:
            result = simulate_round(deck)
            result_counter[result] += 1
        except IndexError:
            break

    total = sum(result_counter.values())
    return result_counter, total

# 執行模擬
if st.button("開始模擬"):
    result_counter, total = simulate_many_rounds(selected_cards, simulations)

    st.subheader("勝率預測結果")
    col1, col2, col3 = st.columns(3)
    col1.metric("閒贏機率", f"{result_counter['閒贏'] / total:.2%}")
    col2.metric("莊贏機率", f"{result_counter['莊贏'] / total:.2%}")
    col3.metric("和局機率", f"{result_counter['和局'] / total:.2%}")
