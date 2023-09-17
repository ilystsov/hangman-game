import os
import sys
from io import StringIO

import pytest

from src.hangman.game import HangmanGame


@pytest.fixture
def game(tmp_path) -> HangmanGame:
    tmp_dir = tmp_path / 'test_data'
    tmp_dir.mkdir()
    base_path = tmp_dir / 'words_base.txt'
    with open(base_path, 'w') as words_base:
        words_base.write('headset\ntap\nmayonnaise')
    os.chdir(tmp_dir)
    return HangmanGame()


def test_choose_word(game: HangmanGame) -> None:
    word: str = game.choose_word()
    assert word.isalpha()


def test_make_hidden_word(game: HangmanGame) -> None:
    hidden_word: str = game.make_hidden_word()
    assert all(char == '_' for char in hidden_word)


def test_game_end(game: HangmanGame) -> None:
    for char in game.word:
        game.guessed_chars.add(char)
    assert game.game_end()


def test_wrong_char(game: HangmanGame) -> None:
    prev_cnt: int = game.guesses_cnt
    game.wrong_char('_')
    assert '_' in game.attempted_chars
    assert game.guesses_cnt + 1 == prev_cnt


def test_right_char(game: HangmanGame) -> None:
    game.right_char('_')
    assert '_' in game.attempted_chars
    assert '_' in game.guessed_chars


@pytest.mark.parametrize(
    'user_input, expected',
    [
        (
            lambda game: list(game.word),
            lambda game: game.guesses_cnt > 0,
        ),
        (
            lambda game: [str(number % 10) for number in range(game.guesses_cnt)],
            lambda game: game.guesses_cnt == 0,
        ),
    ],
)
def test_play(game: HangmanGame, user_input, expected) -> None:
    sys.stdin = StringIO('\n'.join(user_input(game)))
    game.play()
    assert expected(game)
    sys.stdin = sys.__stdin__
    sys.stdout = sys.__stdout__
