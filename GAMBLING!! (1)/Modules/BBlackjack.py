import random, time
import scorekeeper  # Importing pcoins from scorekeeper module

# Initialize gambled funds to 0 if not set yet
if not hasattr(scorekeeper, 'gambledfunds'):
    scorekeeper.gambledfunds = 0

def game():
    # --- Colors / styles ---
    RED = '\033[31m'
    BLACK = '\033[30m'
    gray = '\033[2m'
    YELLOW = '\033[33m'
    ORANGE = "\033[38;2;255;165;0m"
    GREEN = "\033[38;2;0;255;0m"
    RESET = '\033[0m'
    BG_WHITE = '\033[48;2;255;255;255m'
    BOLD = '\033[1m'

    # suits (unicode)
    HEART = '\u2665'
    DIAMOND = '\u2666'
    CLUB = '\u2663'
    SPADE = '\u2660'
    heart2 = '\u2661'
    diamond2 = '\u2662'
    club2 = '\u2667'
    spade2 = '\u2664'

    cards = ['2','3','4','5','6','7','8','9','10','J','Q','K','A']
    player_hand = []
    dealer_hand = []

    coins = {f'{YELLOW}{BOLD}⛁ {RESET}': 5, f'{YELLOW}{BOLD}⛀ {RESET}': 1}
    player_coins = scorekeeper.pcoins  # Using the imported value

    def hide(): print("\033[?25l", end="")
    def show(): print("\033[?25h", end="")
    def clear(): print("\033[H\033[J", end="")

    def typewriter(text, delay=0.1):
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()

    def place_bet():
        nonlocal player_coins
        while True:
            try:
                bet = int(input(f"{BOLD}{YELLOW}Bet (1-{player_coins}): {RESET}"))
                if 1 <= bet <= player_coins:
                    break
            except:
                pass
        player_coins -= bet

        coin_list = []
        remaining = bet
        for coin, value in sorted(coins.items(), key=lambda x: -x[1]):
            count = remaining // value
            coin_list.extend([coin] * count)
            remaining -= count * value
        return bet, coin_list

    def suit_color(suit): return RED if suit in (HEART, DIAMOND) else BLACK

    def format_card(face, suit):
        face_display = face.center(2) if face != "10" else face
        col = suit_color(suit)
        return (
            f"{BOLD}{col}{BG_WHITE}{suit}  {RESET}",
            f"{BOLD}{col}{BG_WHITE} {face_display}{RESET}",
            f"{BOLD}{col}{BG_WHITE}  {suit}{RESET}"
        )

    def format_hidden_card():
        return (
            f"{BG_WHITE}{BLACK}{SPADE}{BOLD} {RED}{HEART}{RESET}",
            f"{BOLD}{BLACK}{BG_WHITE} {spade2} {RESET}",
            f"{BOLD}{BG_WHITE}{RED}{DIAMOND} {BLACK}{CLUB}{RESET}"
        )

    def render_hand(hand, hide_all=False, hide_first=False):
        lines = ["", "", ""]
        for idx, (face, suit) in enumerate(hand):
            if hide_all or (hide_first and idx == 0):
                a, b, c = format_hidden_card()
            else:
                a, b, c = format_card(face, suit)
            lines[0] += a + " "
            lines[1] += b + " "
            lines[2] += c + " "
        return lines

    def draw_random_card(to_hand):
        face = random.choice(cards)
        suit = random.choice([HEART, DIAMOND, SPADE, CLUB])
        to_hand.append((face, suit))
        return face, suit

    def calc_score(hand):
        score = 0
        aces = 0
        for face, _ in hand:
            if face.isdigit():
                score += int(face)
            elif face in ('J','Q','K'):
                score += 10
            else:  # Ace
                aces += 1
        for _ in range(aces):
            if score + 11 <= 21:
                score += 11
            else:
                score += 1
        return score

    def show_table(hide_all=False, hide_dealer_first=False, bet_coins=None):
        clear()
        print(f"{gray}{BOLD}  ___ _      _   ___ _  __{RESET}{BOLD}{RED}  _  _   ___ _  __{RESET}")
        print(f"{gray}{BOLD} | _ ) |    /_\\ / __| |/ /{RESET}{BOLD}{RED} | |/_\\ / __| |/ /{RESET}")
        print(f"{gray}{BOLD} | _ \\ |__ / _ \\ (__| ' <{RESET}{BOLD}{RED} || / _ \\ (__| ' < {RESET}")
        print(f"{gray}{BOLD} |___/____/_/ \\_\\___|_|\\_{RESET}{BOLD}{RED}\\__/_/ \\_\\___|_|\\_\\{RESET}\n")

        if hide_all:
            print(f"Dealer:")
        elif hide_dealer_first:
            print(f"Dealer:{BOLD}{ORANGE}{gray} {calc_score([dealer_hand[1]])}{RESET}")
        else:
            print(f"Dealer:{BOLD}{ORANGE} {calc_score(dealer_hand)}{RESET}")
        for line in render_hand(dealer_hand, hide_all, hide_dealer_first):
            print(line)

        if not hide_all:
            print(f"\nYour Hand:{BOLD}{GREEN} {calc_score(player_hand)}{RESET}")
        else:
            print(f"\nYour Hand:")
        for line in render_hand(player_hand, hide_all):
            print(line)

        if bet_coins and not hide_all:
            print(''.join(bet_coins))

    # --- GAME LOOP ---
    last_bet = None
    current_bet_coins = []
    was_push = False

    while True:
        if player_coins <= 0:
            if scorekeeper.gambledfunds < 1:  # If no college funds used yet
                show_table(hide_all=True, bet_coins=current_bet_coins)
                print(f"\n{BOLD}{RED}You lose!{RESET}")
                print("\n\n\n")
                time.sleep(1)
                print(f"{BOLD}{YELLOW}Unless", end="")
                time.sleep(0.1)
                typewriter("......", 0.25)
                time.sleep(0.5)
                typewriter(f"You have college funds, right???{RESET}", 0.05)
                scorekeeper.gambledfunds += 1  # Track that funds have been used
                funds = input("").strip().lower()

                if funds in ('yes', 'yea', 'yeah'):
                    print(f"{YELLOW}{BOLD}Hell Yeah!{RESET}")
                    time.sleep(0.5)
                    print(f"{BOLD}Next round, you start with 50 coins from college funds.{RESET}")
                    time.sleep(1)
                    scorekeeper.pcoins = 50  # Reset coins in scorekeeper module
                    return game()  # Restart game
                else:
                    print(f"{BOLD}{RED}You're such a bum!!!{RESET}")
                    break
            else:
                break
        player_hand.clear()
        dealer_hand.clear()
        dealer_target = random.randint(17, 19)

        draw_random_card(player_hand)
        draw_random_card(dealer_hand)
        draw_random_card(player_hand)
        draw_random_card(dealer_hand)

        show_table(hide_all=True)

        if not was_push:
            bet_amount, current_bet_coins = place_bet()
            last_bet = bet_amount * 2
        else:
            print(f"{BOLD}{YELLOW}Push!{RESET}")
            bet_amount = last_bet // 2
            was_push = False  # reset for next round

        show_table(hide_dealer_first=True, bet_coins=current_bet_coins)

        while True:
            score = calc_score(player_hand)
            cmd = input("Press Enter to HIT or type 's' to stay: ").strip().lower()
            if cmd == 's':
                break
            draw_random_card(player_hand)
            show_table(hide_dealer_first=True, bet_coins=current_bet_coins)
            if calc_score(player_hand) > 21:
                print(f"{RED}You busted!{RESET}")
                break

        show_table(hide_dealer_first=False, bet_coins=current_bet_coins)

        if calc_score(player_hand) <= 21:
            while calc_score(dealer_hand) < dealer_target:
                print("Dealer's turn")
                time.sleep(0.75)
                draw_random_card(dealer_hand)
                show_table(hide_dealer_first=False, bet_coins=current_bet_coins)

        ps = calc_score(player_hand)
        ds = calc_score(dealer_hand)

        if ps > 21:
            print(f"{RED}{BOLD}You busted!{RESET}")
            last_bet = None
        elif ds > 21 or ps > ds:
            print(f"{BOLD}{GREEN}You win!{RESET}")
            player_coins += bet_amount * 2
            last_bet = None
        elif ps == ds:
            print(f"{BOLD}{YELLOW}Push!{RESET}")
            player_coins += bet_amount  # return coins immediately
            was_push = True  # flag to reuse bet next round
        else:
            print(f"{BOLD}{RED}Dealer wins{RESET}")
            last_bet = None

        scorekeeper.pcoins = player_coins  # Save coins back to the module
        print(f"{BOLD}Coins left: {player_coins}{RESET}")
        input(f"\n{BOLD}Press enter to play again: {RESET}")
        time.sleep(0.1)

# Start the game
