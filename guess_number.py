# pyright: reportUnknownMemberType=false, reportUnknownVariableType=false, reportUnknownArgumentType=false, reportUnknownLambdaType=false
from __future__ import annotations
import json
import random
import urllib.request
from pathlib import Path
from typing import Any, cast

import streamlit as st   # type: ignore[import-not-found]


BASE_DIR = Path(__file__).parent
SCORES_FILE = BASE_DIR / "scores.json"
WORDS_FILE = BASE_DIR / "words.txt"
WORDS_URL = "https://raw.githubusercontent.com/first20hours/google-10000-english/master/google-10000-english.txt"

CATEGORIES: dict[str, list[str]] = {
    "Technology": ["python", "computer", "keyboard", "developer", "programming"],
    "Sports": ["football", "tennis", "basketball", "running", "swimming"],
    "Cities": ["london", "paris", "berlin", "madrid", "rome"],
}

DIFFICULTIES_GUESS: dict[str, dict[str, int]] = {
    "Easy": {"max_number": 100, "attempts": 10},
    "Medium": {"max_number": 100, "attempts": 7},
    "Hard": {"max_number": 100, "attempts": 5},
}

DIFFICULTIES_HANGMAN: dict[str, int] = {
    "Easy": 8,
    "Medium": 6,
    "Hard": 4,
}

HANGMAN_PICS = [
    """
      +---+
      |   |
          |
          |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
          |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
      |   |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
     /|   |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
     /|\\  |
          |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
     /|\\  |
     /    |
          |
    =========
    """,
    """
      +---+
      |   |
      O   |
     /|\\  |
     / \\  |
          |
    =========
    """,
]


def load_scores() -> list[dict[str, Any]]:
    if not SCORES_FILE.exists():
        return []

    try:
        data = json.loads(SCORES_FILE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return cast(list[dict[str, Any]], data)
        return []
    except json.JSONDecodeError:
        return []


def save_scores(scores: list[dict[str, Any]]) -> None:
    SCORES_FILE.write_text(
        json.dumps(scores, indent=4),
        encoding="utf-8",
    )


def update_best_score(game_key: str, score: int) -> bool:
    scores = load_scores()

    player_name = st.session_state.get("player_name", "Player")

    existing_score = next(
        (
            s for s in scores
            if s["player"] == player_name and s["game"] == game_key
        ),
        None,
    )

    if existing_score is None:
        scores.append(
            {
                "player": player_name,
                "game": game_key,
                "score": score,
            }
        )
        save_scores(scores)
        return True

    if score < existing_score["score"]:
        existing_score["score"] = score
        save_scores(scores)
        return True

    return False


def get_best_score(game_key: str) -> int | None:
    scores = load_scores()

    player_name = st.session_state.get("player_name", "Player")

    for score_data in scores:
        if (
            score_data["player"] == player_name
            and score_data["game"] == game_key
        ):
            return score_data["score"]

    return None


def download_words_if_needed() -> None:
    if WORDS_FILE.exists():
        return

    try:
        urllib.request.urlretrieve(WORDS_URL, WORDS_FILE)
    except Exception:
        pass


def load_random_words() -> list[str]:
    download_words_if_needed()

    if not WORDS_FILE.exists():
        return ["python", "computer", "game", "programming", "hangman"]

    words = [
        word.strip().lower()
        for word in WORDS_FILE.read_text(encoding="utf-8").splitlines()
        if word.strip().isalpha() and 4 <= len(word.strip()) <= 10
    ]

    return words or ["python", "computer", "game", "programming", "hangman"]


def reset_guess_game(difficulty: str) -> None:
    settings = DIFFICULTIES_GUESS[difficulty]
    st.session_state.guess_number = random.randint(1, settings["max_number"])
    st.session_state.guess_attempts = 0
    st.session_state.guess_message = "New game started. Good luck!"
    st.session_state.guess_finished = False


def show_guess_game() -> None:
    st.header("🎯 Guess the Number")

    difficulty = st.selectbox("Difficulty", list(DIFFICULTIES_GUESS.keys()), key="guess_difficulty")
    settings = DIFFICULTIES_GUESS[difficulty]
    game_key = f"guess_{difficulty.lower()}"
    best_score = get_best_score(game_key)

    if "guess_number" not in st.session_state:
        reset_guess_game(difficulty)

    if st.button("New Guess Game"):
        reset_guess_game(difficulty)

    st.write(f"I chose a number between 1 and {settings['max_number']}.")
    st.write(f"Maximum attempts: {settings['attempts']}")

    if best_score is None:
        st.info("No best score yet.")
    else:
        st.success(f"🏆 Best score: {best_score} attempts")

    guess = st.number_input("Your guess", min_value=1, max_value=settings["max_number"], step=1)

    if st.button("Submit Guess") and not st.session_state.guess_finished:
        st.session_state.guess_attempts += 1
        number_to_guess = st.session_state.guess_number

        if guess < number_to_guess:
            difference = abs(guess - number_to_guess)
            if difference <= 5:
                st.session_state.guess_message = "Too low ⬇️ — 🔥 Very close!"
            elif difference <= 15:
                st.session_state.guess_message = "Too low ⬇️ — 🌡️ Getting warm."
            else:
                st.session_state.guess_message = "Too low ⬇️ — ❄️ Cold."
        elif guess > number_to_guess:
            difference = abs(guess - number_to_guess)
            if difference <= 5:
                st.session_state.guess_message = "Too high ⬆️ — 🔥 Very close!"
            elif difference <= 15:
                st.session_state.guess_message = "Too high ⬆️ — 🌡️ Getting warm."
            else:
                st.session_state.guess_message = "Too high ⬆️ — ❄️ Cold."
        else:
            st.session_state.guess_finished = True
            new_record = update_best_score(game_key, st.session_state.guess_attempts)
            if new_record:
                st.session_state.guess_message = f"🎉 Correct in {st.session_state.guess_attempts} attempts — new best score!"
            else:
                st.session_state.guess_message = f"🎉 Correct in {st.session_state.guess_attempts} attempts!"

        if st.session_state.guess_attempts >= settings["attempts"] and not st.session_state.guess_finished:
            st.session_state.guess_finished = True
            st.session_state.guess_message = f"💀 Game over! The number was {number_to_guess}."

    attempts_left = settings["attempts"] - st.session_state.guess_attempts
    st.write(f"Attempts left: {max(attempts_left, 0)}")
    st.write(st.session_state.guess_message)


def reset_hangman_game(category: str, difficulty: str) -> None:
    if category == "Random 10,000 words":
        words = load_random_words()
    else:
        words = CATEGORIES[category]

    st.session_state.hangman_word = random.choice(words)
    st.session_state.hangman_guessed_letters = set()
    st.session_state.hangman_attempts_left = DIFFICULTIES_HANGMAN[difficulty]
    st.session_state.hangman_max_attempts = DIFFICULTIES_HANGMAN[difficulty]
    st.session_state.hangman_message = "New Hangman game started."
    st.session_state.hangman_finished = False


def get_hangman_picture(attempts_left: int, max_attempts: int) -> str:
    wrong_guesses = max_attempts - attempts_left
    picture_index = int(wrong_guesses * (len(HANGMAN_PICS) - 1) / max_attempts)
    return HANGMAN_PICS[picture_index]


def show_hangman_game() -> None:
    st.header("🔤 Hangman")

    categories = ["Technology", "Sports", "Cities", "Random 10,000 words"]
    category = st.selectbox("Category", categories, key="hangman_category")
    difficulty = st.selectbox("Difficulty", list(DIFFICULTIES_HANGMAN.keys()), key="hangman_difficulty")
    game_key = f"hangman_{difficulty.lower()}"
    best_score = get_best_score(game_key)

    if "hangman_word" not in st.session_state:
        reset_hangman_game(category, difficulty)

    if st.button("New Hangman Game"):
        reset_hangman_game(category, difficulty)

    word_to_guess = str(st.session_state.hangman_word)
    guessed_letters = cast(set[str], st.session_state.hangman_guessed_letters)
    attempts_left = int(st.session_state.hangman_attempts_left)
    max_attempts = int(st.session_state.hangman_max_attempts)

    st.write(f"Hint: the word has {len(word_to_guess)} letters.")

    if best_score is None:
        st.info("No best score yet.")
    else:
        st.success(f"🏆 Best score: {best_score} wrong guesses")

    st.code(get_hangman_picture(attempts_left, max_attempts))

    display_word = " ".join(letter if letter in guessed_letters else "_" for letter in word_to_guess)
    st.subheader(display_word)
    st.write(f"Attempts left: {attempts_left}")
    st.write(f"Tried letters: {' '.join(sorted(guessed_letters)) or 'none'}")

    guess = st.text_input("Guess a letter", max_chars=1).lower().strip()

    if st.button("Submit Letter") and not st.session_state.hangman_finished:
        if len(guess) != 1 or not guess.isalpha():
            st.session_state.hangman_message = "Please enter a single letter."
        elif guess in guessed_letters:
            st.session_state.hangman_message = "You already tried that letter."
        else:
            guessed_letters.add(guess)

            if guess in word_to_guess:
                st.session_state.hangman_message = "Good guess! ✅"
            else:
                st.session_state.hangman_attempts_left -= 1
                st.session_state.hangman_message = "Wrong guess ❌"

            if all(letter in guessed_letters for letter in word_to_guess):
                wrong_guesses = max_attempts - st.session_state.hangman_attempts_left
                new_record = update_best_score(game_key, wrong_guesses)
                st.session_state.hangman_finished = True
                if new_record:
                    st.session_state.hangman_message = f"🎉 You won! The word was '{word_to_guess}'. New best score!"
                else:
                    st.session_state.hangman_message = f"🎉 You won! The word was '{word_to_guess}'."

            if st.session_state.hangman_attempts_left <= 0 and not st.session_state.hangman_finished:
                st.session_state.hangman_finished = True
                st.session_state.hangman_message = f"💀 You lost! The word was '{word_to_guess}'."

        st.rerun()

    st.write(st.session_state.hangman_message)

CARDS = {
    "AS": 11,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "10": 10,
    "J": 10,
    "Q": 10,
    "K": 10,
}


def draw_card() -> str:
    return random.choice(list(CARDS.keys()))


def calculate_score(cards: list[str]) -> int:
    score = sum(CARDS[card] for card in cards)

    aces = cards.count("AS")

    while score > 21 and aces > 0:
        score -= 10
        aces -= 1

    return score


def reset_blackjack_game() -> None:
    st.session_state.player_cards = [draw_card(), draw_card()]
    st.session_state.dealer_cards = [draw_card(), draw_card()]
    st.session_state.blackjack_finished = False
    st.session_state.blackjack_message = ""

def show_blackjack_game() -> None:
    st.header("🎴 Blackjack")

    if "player_cards" not in st.session_state:
        reset_blackjack_game()

    if st.button("New Blackjack Game"):
        reset_blackjack_game()

    player_cards = st.session_state.player_cards
    dealer_cards = st.session_state.dealer_cards

    player_score = calculate_score(player_cards)
    dealer_score = calculate_score(dealer_cards)

    st.subheader("Your Cards")
    st.write(player_cards)
    st.write(f"Score: {player_score}")

    st.subheader("Dealer")

    if st.session_state.blackjack_finished:
        st.write(dealer_cards)
        st.write(f"Score: {dealer_score}")
    else:
        st.write([dealer_cards[0], "❓"])

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Hit") and not st.session_state.blackjack_finished:
            player_cards.append(draw_card())
            player_score = calculate_score(player_cards)

            if player_score > 21:
                st.session_state.blackjack_finished = True
                st.session_state.blackjack_message = "💀 Bust! You lose."

            st.rerun()

    with col2:
        if st.button("Stand") and not st.session_state.blackjack_finished:
            while calculate_score(dealer_cards) < 17:
                dealer_cards.append(draw_card())

            dealer_score = calculate_score(dealer_cards)

            st.session_state.blackjack_finished = True

            if dealer_score > 21:
                st.session_state.blackjack_message = "🎉 Dealer busts! You win."
            elif dealer_score > player_score:
                st.session_state.blackjack_message = "😢 Dealer wins."
            elif dealer_score < player_score:
                st.session_state.blackjack_message = "🎉 You win!"
            else:
                st.session_state.blackjack_message = "🤝 Draw."

            st.rerun()

    st.write(st.session_state.blackjack_message)

def show_scores() -> None:
    st.header("🏆 Leaderboard")
    scores = load_scores()

    if not scores:
        st.info("No scores saved yet.")
        return

    score_names = {
        "guess_easy": "Guess the Number — Easy",
        "guess_medium": "Guess the Number — Medium",
        "guess_hard": "Guess the Number — Hard",
        "hangman_easy": "Hangman — Easy",
        "hangman_medium": "Hangman — Medium",
        "hangman_hard": "Hangman — Hard",
    }

    sorted_scores = sorted(scores, key=lambda score_data: score_data["score"])

    for position, score_data in enumerate(sorted_scores, start=1):
        label = score_names.get(score_data["game"], score_data["game"])

        if score_data["game"].startswith("guess"):
            unit = "attempts"
        elif score_data["game"].startswith("hangman"):
            unit = "wrong guesses"
        else:
            unit = "points"

        st.write(
            f"**{position}. {score_data['player']}** — {label}: "
            f"{score_data['score']} {unit}"
        )

    if st.button("Reset all scores"):
        save_scores([])
        st.success("Scores reset.")
        st.rerun()


def main() -> None:
    st.set_page_config(page_title="Python Games", page_icon="🎮")
    st.title("🎮 Python Games")
    player_name = st.sidebar.text_input("Player name", value="Player")

    st.session_state.player_name = player_name

    page = st.sidebar.radio(
        "Choose a game",
        [
            "Guess the Number",
            "Hangman",
            "Blackjack",
            "Scores",
        ],
    )
    if page == "Guess the Number":
        show_guess_game()
    elif page == "Hangman":
        show_hangman_game()
    elif page == "Blackjack":
        show_blackjack_game()
    elif page == "Scores":
        show_scores()


if __name__ == "__main__":
    main()