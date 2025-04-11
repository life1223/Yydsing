
import streamlit as st
import random
from collections import Counter

st.set_page_config(page_title="牌影", page_icon="logo.png")
st.image("logo.png", use_container_width=True)

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

# UI 介面
st.markdown("<style>div.block-container{padding-top:2rem;}</style>", unsafe_allow_html=True)

with st.container():
    st.markdown("### 請輸入目前已開出的牌（例如：A 5 9 K）")
    user_input = st.text_input("目前已開出的牌（用空格分隔）", placeholder="輸入如：A 5 9 K")

    st.markdown("### 模擬次數")
    simulations = st.slider("", 1000, 20000, 10000, step=1000)

    if st.button("開始模擬"):
        used_cards = user_input.strip().upper().split()
        result_counter, total = simulate_many_rounds(used_cards, simulations)

        st.markdown("## 勝率預測結果")
        col1, col2, col3 = st.columns([1, 1, 1])  # 三欄等寬

        with col1:
            st.metric("莊贏機率", f"{result_counter['莊贏'] / total:.2%}")

        with col2:
            st.metric("閒贏機率", f"{result_counter['閒贏'] / total:.2%}")

        with col3:
            st.metric("和局機率", f"{result_counter['和局'] / total:.2%}")
