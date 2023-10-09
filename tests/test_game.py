from typing import Set

import pytest
import requests

from src.hangman.game import (
    ChooseWord,
    ChooseWordFromAPI,
    GameTimer,
    HangmanGame,
    IOHandler,
    Timer,
)


class FkIOConsole(IOHandler):
    def __init__(self, return_values: list[str] = []) -> None:
        self.return_values = return_values
        self.shift: int = 0
        self.container: list[str] = []

    def read(self) -> str:
        value: str = self.return_values[self.shift]
        self.shift += 1
        return value

    def write(self, text: str) -> None:
        self.container.append(text)


class FkChooseWord(ChooseWord):
    def choose_word(self) -> str:
        return 'apple'


@pytest.fixture
def game(freezer) -> HangmanGame:
    freezer.move_to('2023-10-03 19:00:00')
    io_handler: FkIOConsole = FkIOConsole()
    choose_word_method: FkChooseWord = FkChooseWord()
    timer: Timer = GameTimer(30)
    return HangmanGame(choose_word_method, io_handler, timer)


@pytest.fixture(params=[
    30,
    60,
    120,
])
def timer(request, freezer) -> GameTimer:
    freezer.move_to('2023-10-03 19:00:00')
    return GameTimer(request.param)


@pytest.fixture
def choose_word_instance() -> ChooseWordFromAPI:
    return ChooseWordFromAPI(FkIOConsole())


def test_choose_word(requests_mock, choose_word_instance: ChooseWordFromAPI) -> None:
    requests_mock.get('https://random-word-api.herokuapp.com/word', text="['apple']")
    word: str = choose_word_instance.choose_word()
    assert word == 'apple'


def test_choose_word_errors(requests_mock, choose_word_instance: ChooseWordFromAPI) -> None:
    requests_mock.get('https://random-word-api.herokuapp.com/word', exc=requests.exceptions.Timeout)
    with pytest.raises(SystemExit):
        choose_word_instance.choose_word()
    assert choose_word_instance.io_handler.container[-1] == 'Server did not respond in 10 seconds. We are sorry :(\n'


def test_choose_word_timeout(requests_mock, choose_word_instance: ChooseWordFromAPI) -> None:
    requests_mock.get('https://random-word-api.herokuapp.com/word', exc=requests.exceptions.RequestException)
    with pytest.raises(SystemExit):
        choose_word_instance.choose_word()
    assert 'An error occurred: ' in choose_word_instance.io_handler.container[-1]
    assert '. We are sorry :(\n' in choose_word_instance.io_handler.container[-1]


@pytest.mark.parametrize('time, expected_result', [
    ('2023-10-03 19:02:01', True),
    ('2023-10-03 19:00:29', False),
])
def test_is_time_up(timer: GameTimer, freezer, time: str, expected_result: bool) -> None:
    freezer.move_to(time)
    assert timer.is_time_up() == expected_result


@pytest.mark.parametrize('word, guessed_chars, expected_hidden_word', [
    ('sanity', {'a', 'n', 't'}, '_an_t_'),
    ('acknowledgment', {'e', 'n'}, '___n___e___en_'),
    ('wit', {}, '___'),
])
def test_make_hidden_word(game: HangmanGame, word: str, guessed_chars: Set[str], expected_hidden_word: str) -> None:
    game.word = word
    game.guessed_chars = guessed_chars
    hidden_word: str = game.make_hidden_word()
    assert hidden_word == expected_hidden_word


@pytest.mark.parametrize('word, g_chars, g_cnt, expected_result', [
    ('beaver', {'a', 'e', 'v'}, 6, False),
    ('man', {'a', 'n', 'm'}, 3, True),
    ('river', {'i'}, 0, True),
])
def test_game_end(game: HangmanGame, word: str, g_chars: Set[str], g_cnt: int, expected_result: bool) -> None:
    game.word = word
    game.word_chars = set(word)
    game.guessed_chars = g_chars
    game.guesses_cnt = g_cnt
    assert game.game_end() == expected_result


def test_wrong_char(game: HangmanGame) -> None:
    prev_cnt: int = game.guesses_cnt
    game.wrong_char('_')
    assert '_' in game.attempted_chars
    assert game.guesses_cnt + 1 == prev_cnt
    assert game.io_handler.container[-1] == 'Wrong\nYou have {number} more guesses\n'.format(number=game.guesses_cnt)


def test_right_char(game: HangmanGame) -> None:
    game.right_char('_')
    assert '_' in game.attempted_chars
    assert '_' in game.guessed_chars


def test_out_of_time(game: HangmanGame):
    game.out_of_time()
    assert game.io_handler.container[-1] == '\nYou are out of time! '
    assert game.guesses_cnt == 0


def test_play_win(game: HangmanGame) -> None:
    game.io_handler.return_values = ['a', 'x', 'p', 'y', 'l', 'z', 'e']
    game.play()
    assert game.io_handler.container[-1] == 'apple You win\n'


def test_play_lose(game: HangmanGame) -> None:
    game.io_handler.return_values = ['q', 'w', 'e', 'r', 't', 'y']
    game.play()
    assert game.io_handler.container[-1] == 'You lose. The word is apple\n'


def test_play_repeated_char(game: HangmanGame) -> None:
    game.io_handler.return_values = ['a', 'a', 'p', 'l', 'e']
    game.play()
    assert "You've already tried character 'a'. Try another one\n" in game.io_handler.container


def test_play_timeout(game: HangmanGame, freezer) -> None:
    freezer.move_to('2023-10-03 19:00:31')
    game.play()
    assert game.io_handler.container[-1] == 'You lose. The word is apple\n'
    assert game.io_handler.container[-2] == '\nYou are out of time! '
