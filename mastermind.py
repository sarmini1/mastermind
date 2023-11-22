import requests


class Mastermind():
    "The Mastermind game."

    def __init__(self):
        """What needs to happen when a game instance is made."""

        self.answer = self.fetch_random_nums()
        self.score = 0
        # self.difficulty = difficulty # TODO: add this once basic game is made

    @classmethod
    def create_new_game(cls):
        """Generates a new game instance."""

        return Mastermind()

    def fetch_random_nums(self, count=4):
        """
        Makes an API request to fetch a specified count of random numbers.
        If no count is provided, the default will be 4.

        Returns fetched numbers in a list, like: [3,6,7,2]

        """

    def handle_guess(self, guessed_nums):
        """
        Takes in a set of guessed numbers in a list, compares them to
        the hidden numbers, and updates sco

        """

