import random
from collections import Counter
import os

# ----- COLORS / STYLES -----
RED = '\033[31m'
BLACK = '\033[30m'
YELLOW = '\033[33m'
GREEN = '\033[38;2;0;255;0m'
MAGENTA = '\033[35m'
RESET = '\033[0m'
BG_WHITE = '\033[48;2;255;255;255m'
BG_GREY = '\033[48;2;235;235;235m'
BOLD = '\033[1m'

# ----- SUITS -----
HEART = '\u2665'
DIAMOND = '\u2666'
CLUB = '\u2663'
SPADE = '\u2660'
SPADE2 = '\u2664'

SUITS = [HEART, DIAMOND, SPADE, CLUB]

# ----- RANKS -----
RANK_ORDER = ["2","3","4","5","6","7","8","9","10","J","Q","K","A"]

# ----- CARD FORMATTING -----
def suit_color(suit):
    return RED if suit in (HEART, DIAMOND) else BLACK

def format_card(face, suit):
    face_display = face.center(2) if face != "10" else face
    col = suit_color(suit)
    return (
        f"{BOLD}{col}{BG_WHITE}{suit}  {RESET}",
        f"{BOLD}{col}{BG_WHITE} {face_display}{RESET}",
        f"{BOLD}{col}{BG_WHITE}  {suit}{RESET}"
    )

# ----- HIDDEN CARD -----
def format_hidden_card():
    return (
        f"{BG_WHITE}{BLACK}{SPADE}{BOLD} {RED}{HEART}{RESET}",
        f"{BOLD}{BLACK}{BG_WHITE} {SPADE2} {RESET}",
        f"{BOLD}{BG_WHITE}{RED}{DIAMOND} {BLACK}{CLUB}{RESET}"
    )

# ----- JOKER CARD -----
def format_joker():
    return (
        f"{BOLD}{BLACK}{BG_GREY}J  {RESET}",
        f"{BOLD}{BLACK}{BG_GREY} ♞ {RESET}",
        f"{BOLD}{BLACK}{BG_GREY}  J{RESET}"
    )

# ----- RENDER CARDS -----
def render(cards, hide=False):
    lines = ["", "", ""]
    for c in cards:
        if hide:
            a, b, c2 = format_hidden_card()
        else:
            if c[0] == "JOKER":
                a, b, c2 = format_joker()
            else:
                a, b, c2 = format_card(*c)
        lines[0] += a + " "
        lines[1] += b + " "
        lines[2] += c2 + " "
    return lines

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# ----- DECK -----
def create_deck():
    deck = [(r, s) for r in RANK_ORDER for s in SUITS]
    deck += [("JOKER", None), ("JOKER", None)]  # Max 2 jokers
    random.shuffle(deck)
    return deck

# ----- HAND EVALUATION -----
HAND_NAMES = [
    "High Card", "One Pair", "Two Pair", "Three of a Kind",
    "Straight", "Flush", "Full House", "Four of a Kind", "Straight Flush"
]

def evaluate(hand):
    """
    Returns (hand_rank, main_cards)
    Jokers are wild and intelligently used for straights, flushes, sets.
    """
    jokers = [c for c in hand if c[0]=="JOKER"]
    normal = [c for c in hand if c[0]!="JOKER"]

    ranks = []
    suits = []
    for c in normal:
        if c[0] == "A":
            ranks.append(14)
        elif c[0] == "K":
            ranks.append(13)
        elif c[0] == "Q":
            ranks.append(12)
        elif c[0] == "J":
            ranks.append(11)
        else:
            ranks.append(int(c[0]))
        suits.append(c[1])

    count = Counter(ranks)
    num_jokers = len(jokers)

    # ----- Check Flush (with Jokers) -----
    suit_counts = Counter(suits)
    flush_suit = None
    for s, qty in suit_counts.items():
        if qty + num_jokers >= 5:
            flush_suit = s
            break

    # ----- Check Straight (with Jokers) -----
    best_straight = 0
    for start in range(14, 4, -1):
        needed = []
        for i in range(5):
            r = start - i
            if r not in ranks:
                needed.append(r)
        if len(needed) <= num_jokers:
            best_straight = start
            break
    is_straight = best_straight > 0
    is_flush = flush_suit is not None
    if is_straight and is_flush:
        return (8,[best_straight])

    # ----- Four of a Kind -----
    for r in range(14,1,-1):
        if count.get(r,0) + num_jokers >= 4:
            return (7,[r])

    # ----- Full House -----
    three = None
    pair = None
    for r in range(14,1,-1):
        if count.get(r,0) + num_jokers >=3 and not three:
            three = r
    if three is not None:
        remaining_jokers = num_jokers - max(0,3-count.get(three,0))
        for r in range(14,1,-1):
            if r == three:
                continue
            if count.get(r,0) + remaining_jokers >=2:
                pair = r
                return (6,[three,pair])

    # ----- Flush -----
    if is_flush:
        sorted_flush = sorted([r for r,s in normal if s==flush_suit], reverse=True)
        while len(sorted_flush) < 5:
            sorted_flush.append(14)
        return (5,sorted_flush[:5])

    # ----- Straight -----
    if is_straight:
        return (4,[best_straight])

    # ----- Three of a Kind -----
    for r in range(14,1,-1):
        if count.get(r,0) + num_jokers >=3:
            return (3,[r])

    # ----- Two Pair -----
    pairs = []
    for r in range(14,1,-1):
        if count.get(r,0) >=2:
            pairs.append(r)
    if len(pairs) >=2:
        return (2,[pairs[0]])

    # ----- One Pair -----
    if len(pairs)==1:
        return (1,[pairs[0]])

    # ----- High Card -----
    if ranks:
        return (0,[max(ranks)])

    return (0,[0])

# ----- STATS -----
player_wins = 0
dealer_wins = 0
pending_push_multiplier = 1

def get_player_percent():
    total = player_wins + dealer_wins
    return int(player_wins / total * 100) if total > 0 else 50

def get_dealer_percent():
    return 100 - get_player_percent()

# ----- SHOW TABLE -----
def show_table(player_hand, dealer_hand, hide_dealer=True):
    clear()
    print(f"{BOLD}♠ 5-CARD DRAW ♣{RESET}\n")

    print(f"{BOLD}{RED}Dealer:{RESET}")
    for line in render(dealer_hand, hide=hide_dealer):
        print(line)
    print(f"Dealer Win%: {GREEN if get_dealer_percent() >= 50 else RED}{get_dealer_percent()}{RESET}\n")

    print(f"{BOLD}{BLACK}Your Hand:{RESET}")
    for line in render(player_hand):
        print(line)
    print(f"Player Win%: {GREEN if get_player_percent() >= 50 else RED}{get_player_percent()}{RESET}\n")

# ----- DEALER STRATEGY -----
def dealer_discard_strategy(hand):
    ranks = [c[0] for c in hand if c[0]!="JOKER"]
    count = Counter(ranks)
    keep = set()

    # Never discard Jokers
    for i,c in enumerate(hand):
        if c[0]=="JOKER":
            keep.add(i)

    # Keep pairs or better
    for rank, qty in count.items():
        if qty >=2:
            for i,c in enumerate(hand):
                if c[0]==rank:
                    keep.add(i)

    # Keep high cards
    for i,c in enumerate(hand):
        if c[0] in ("10","J","Q","K","A"):
            keep.add(i)

    discard = [i for i in range(len(hand)) if i not in keep]
    return discard

# ----- ROUND PLAY -----
def play_round():
    global player_wins, dealer_wins, pending_push_multiplier

    deck = create_deck()
    player = [deck.pop() for _ in range(5)]
    dealer = [deck.pop() for _ in range(5)]

    show_table(player, dealer)
    choice = input("\nWhich card(s) do you want to KEEP? (1–5) or 'a' to keep all: ").strip()

    if choice.lower() == 'a':
        pass
    elif choice == '':
        player = [deck.pop() for _ in range(5)]
    else:
        idxs_to_keep = sorted({int(i)-1 for i in choice if i.isdigit() and 0 <= int(i)-1 <5})
        kept_cards = [c for i,c in enumerate(player) if i in idxs_to_keep]
        new_cards = [deck.pop() for _ in range(5-len(kept_cards))]
        player = kept_cards + new_cards

    dealer_discard_idxs = dealer_discard_strategy(dealer)
    for i in sorted(dealer_discard_idxs, reverse=True):
        dealer.pop(i)
        dealer.append(deck.pop())

    show_table(player, dealer)
    input("\nPress Enter to reveal dealer")
    show_table(player, dealer, hide_dealer=False)

    p_score = evaluate(player)
    d_score = evaluate(dealer)

    print(f"{BOLD}Dealer has: {RED}{HAND_NAMES[d_score[0]]}")
    print(f"You have: {BLACK}{HAND_NAMES[p_score[0]]}\n{RESET}")

    if p_score > d_score:
        print(f"{BLACK}{BOLD}You win!{RESET}")
        player_wins += pending_push_multiplier
        pending_push_multiplier = 1
    elif p_score < d_score:
        print(f"{RED}{BOLD}Dealer wins{RESET}")
        dealer_wins += pending_push_multiplier
        pending_push_multiplier = 1
    else:
        print(f"{YELLOW}Push! Next round's win counts double.{RESET}")
        pending_push_multiplier *= 2

# ----- GAME LOOP -----
def game():
    try:
        while True:
            play_round()
            again = input("\nPlay another round? (y/n): ").lower()
            if again == 'n':
                print("\nThanks for playing! Goodbye!")
                break
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user. Goodbye!")

# ----- START GAME -----
if __name__ == "__main__":
    game()
