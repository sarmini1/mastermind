import requests


class Mastermind():
    "The Mastermind game."

    def __init__(self):
        """What needs to happen when a game instance is made."""

        self.answer = self.fetch_random_nums()
        # self.score = 0
        self.has_won = False
        self.game_over = False
        self.guessed_nums_history = []
        self.feedback = []
        self.remaining_guesses = 10

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

        response = requests.get(
            "https://www.random.org/integers/",
            params={
                "num": count,
                "min": 1,
                "max": 8,
                "col": 1,
                "base": 10,
                "format": "plain",
                "rnd": "new",
            }
        )

        parsed_response = response.text.splitlines()
        parsed_nums = [int(str) for str in parsed_response]

        return parsed_nums

    def handle_guess(self, guessed_nums):
        """
        Takes in a set of guessed numbers, scores them, and updates the game
        instance accordingly:

        Always:

            - Stores their guess in the guessed_nums_history property
            - Stores their feedback in the property by the same name
            - Decrements remaining_guesses by 1

        If this was their last remaining guess:
            - Sets game_over to True

        If their guess is 100% correct:
            - Updates the has_won property to True
            - Sets game_over to True

        """

        score = self.score_guess(guessed_nums)
        self.guessed_nums_history.append(guessed_nums)

        feedback = self._generate_feedback(score)
        self.feedback.append(feedback)

        self.remaining_guesses -= 1

        if self.remaining_guesses == 0:
            self.game_over = True

        if score["won"]:
            self.game_over = True
            self.has_won = True

    def _generate_feedback(self, score):
        """Returns a user_friendly string of information about their guess."""

        correct_nums = score["correct_nums"]
        correct_locations = score["correct_locations"]

        if correct_nums == 0 and correct_locations == 0:
            return "All incorrect."

        if correct_nums == 4 and correct_locations == 4:
            return "You win!"

        return f"{correct_nums} correct number and {correct_locations} correct locations"

    def score_guess(self, guessed_nums):
        """
        Takes in a set of guessed numbers in a list, compares them to
        the hidden numbers, and returns the correct number and correct location
        counts in a dictionary.

        For example, if the hidden numbers were [1,5,7,8]:

        Input:
        guessed_nums = [1,2,3,4]

        Output:
        {
            correct_nums: 1,
            correct_locations: 1,
        }
        """

        # iterate through guessed_nums [1,2,3,4]
        # at each point, check to see if the value at the current index is
        # equal to the value at the index in the answer list

        # if so, increment both correct_nums and correct_locations counters by 1

        # else, check if the current guessed number exists in the list at all
        # if so, increment correct_nums counter

        # TODO: consider making this an instance property
        # Using a set will allow us to have a more efficient lookup if we need
        # to search through the entire list of numbers.
        answer_as_set = set(self.answer)

        correct_nums = 0
        correct_locations = 0
        won = False
        curr_index = 0

        for num in guessed_nums:
            if self.answer[curr_index] == num:
                correct_nums += 1
                correct_locations += 1
            elif num in answer_as_set:
                correct_nums += 1
            curr_index += 1

        return {
            "won": won,
            "correct_nums": correct_nums,
            "correct_locations": correct_locations
        }
