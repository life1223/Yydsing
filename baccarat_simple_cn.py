import streamlit as st
import random
from collections import Counter

# 設定頁面標題與 icon
st.set_page_config(page_title="牌影", page_icon="logo.png")

# 自訂 CSS 美化介面
st.markdown("""
    <style>
        body {
            background: linear-gradient(180deg, #000000, #1a1a1a);
            color: white;
        }
        .block-container {
            padding-top: 2rem;
        }
        .logo {
            display: flex;
            justify-content: center;
            margin-bottom: 2rem;
        }
        .title-img {
            width: 200px;
        }
        .card {
            background: #222;
            padding: 1.5rem;
            border-radius: 1rem;
            text-align: center;
            color: white;
            font-family: sans-serif;
        }
        .card-title {
            font-size: 1rem;
            color: #aaa;
        }
        .card-value {
            font-size: 2rem;
            font-weight: bold;
            color: white;
        }
        .stTextInput > div > input {
            background-color: #111;
            color: white;
            border-radius: 0.5rem;
        }
        .stSlider > div {
            color: white;
        }
        .stButton>button {
            background-color: #333333;
            color: white;
            border-radius: 0.5rem;
            padding: 0.75rem 2rem;
        }
    </style>
""", unsafe_allow_html=True)

# 顯示 logo
st.markdown('<div class="logo"><img src="logo.png" class="title-img"/></div>', unsafe_allow_html=True)

# 使用者輸入
st.markdown("請輸入目前已開出的牌（例如：A 5 9 K）")
user_input = st.text_input("目前已開出的牌（用空格分隔）", placeholder="輸入如：A 5 9 K")
simulations = st.slider("模擬次數", 1000, 20000, 10000, step=1000)

# 執行模擬
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

if st.button("開始模擬"):
    used_cards = user_input.strip().upper().split()
    result_counter, total = simulate_many_rounds(used_cards, simulations)

    st.markdown("### 勝率預測結果")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown('<div class="card"><div class="card-title">莊贏機率</div><div class="card-value">{:.2%}</div></div>'.format(result_counter['莊贏'] / total), unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card"><div class="card-title">閒贏機率</div><div class="card-value">{:.2%}</div></div>'.format(result_counter['閒贏'] / total), unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="card"><div class="card-title">和局機率</div><div class="card-value">{:.2%}</div></div>'.format(result_counter['和局'] / total), unsafe_allow_html=True)
