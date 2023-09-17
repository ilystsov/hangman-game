import sys
from secrets import choice


class HangmanGame(object):
    """
    This class implements Hangman game.

    Attributes:
    word: the word to guess
    word_chars: a set of unique letters that make up a word
    guessed_chars: a set of chars, guessed by a player
    attempted_chars: a set of chars, proposed by a player
    guesses_cnt: a number of attempts
    """

    def __init__(self) -> None:
        """Initialize HangmanGame class instance."""
        self.word: str = self.choose_word()
        self.word_chars: set[str] = set(self.word)
        self.guessed_chars: set[str] = set()
        self.attempted_chars: set[str] = set()
        self.guesses_cnt: int = len(self.word)

    def choose_word(self) -> str:
        """
        Return a random word from the words base.

        >>> HangmanGame().choose_word()
        apple

        :return: str
        """
        with open('words_base.txt', 'r') as words_base:
            words: list[str] = words_base.readlines()
            return choice(words).rstrip('\n')

    def make_hidden_word(self) -> str:
        """
        Get a word representation with underlines for player.

        >>> HangmanGame().make_hidden_word()
        app_e

        :return: str
        """
        hidden_word: str = ''
        blank: str = '_'
        for char in self.word:
            if char in self.guessed_chars:
                hidden_word += char
            else:
                hidden_word += blank
        return hidden_word

    def game_end(self) -> bool:
        """
        Check if the game is over.

        :return: bool
        """
        guessed_chars_len: int = len(self.guessed_chars)
        word_chars_len: int = len(self.word_chars)
        return self.guesses_cnt == 0 or guessed_chars_len == word_chars_len

    def wrong_char(self, char: str) -> None:
        """
        Actions if the char proposed is incorrect.

        :param char: char
        """
        self.attempted_chars.add(char)
        self.guesses_cnt -= 1
        if self.guesses_cnt != 0:
            sys.stdout.write('Wrong\nYou have {number} more guesses\n'.format(number=self.guesses_cnt))

    def right_char(self, char: str) -> None:
        """
        Actions if the char proposed is correct.

        :param char: char
        """
        self.attempted_chars.add(char)
        self.guessed_chars.add(char)

    def play(self) -> None:
        """Proceed the player's input, show the player's progress. Output the result of the game."""
        sys.stdout.write('Start guessing...\n')
        while not self.game_end():
            sys.stdout.write('{word} guess a character: '.format(word=self.make_hidden_word()))
            sys.stdout.flush()
            char: str = sys.stdin.read(2).rstrip('\n').lower()
            if char in self.attempted_chars:
                sys.stdout.write("You've already tried character '{char}'. Try another one\n".format(char=char))
            else:
                if char not in self.word_chars:
                    self.wrong_char(char)
                else:
                    self.right_char(char)
        if self.guesses_cnt == 0:
            sys.stdout.write('You lose. The word is {word}\n'.format(word=self.word))
        else:
            sys.stdout.write('{word} You win\n'.format(word=self.word))


if __name__ == '__main__':
    HangmanGame().play()
