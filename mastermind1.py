from collections import Counter

import requests


class Mastermind():
    "The Mastermind game."

    def __init__(self, count):
        """Initializing various properties when a new instance is made."""

        self.count = count
        self.answer = self._fetch_random_nums(count)
        # self.score = 0
        self.has_won = False
        self.game_over = False
        self.guessed_nums_history = []
        self.feedback = []
        self.remaining_guesses = 10

    def _fetch_random_nums(self, count=4):
        """
        Makes an API request to fetch a specified count of random numbers.
        If no count is provided as a parameter, the default will be 4.

        Returns fetched numbers in a list, like: [3,6,7,2]

        """

        response = requests.get(
            "https://www.random.org/integers/",
            params={
                "num": count,
                "min": 0,
                "max": 7,
                "col": 1,
                "base": 10,
                "format": "plain",
                "rnd": "new",
            }
        )

        parsed_response = response.text.splitlines()
        parsed_nums = [int(line) for line in parsed_response]

        return parsed_nums

    def handle_guess(self, guessed_nums):
        """
        Takes in a list of guessed_nums, scores them, and updates the game
        instance accordingly as outlined below. Returns None.

        Always:

            - Stores their guess in the guessed_nums_history property
            - Stores their feedback in the property by the same name
            - Decrements remaining_guesses by 1

        If this was their last remaining guess:
            - Sets game_over to True

        If their guess is correct:
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
        """
        Receives a score, passed in as a dictionary, and returns a string
        containing information about the score. If the score indicates no
        correct numbers and locations, this method will return "All incorrect."
        Otherwise the returned string will contain information like:

        Input: {
            "correct_nums": 2,
            "correct_locations: 2
        }

        Output: "2 correct number(s) and 2 correct location(s)."

        """

        correct_nums = score["correct_nums"]
        correct_locations = score["correct_locations"]

        if correct_nums == 0 and correct_locations == 0:
            return "All incorrect."

        return f"{correct_nums} correct number(s) and {correct_locations} correct location(s)."

    def score_guess(self, guessed_nums):
        """
        Takes in a list of guessed_nums, compares them to the hidden answer numbers,
        and returns the correct number and correct location counts in a dictionary.

        For example, if the hidden answer numbers were [1,5,7,8]:

        Input:
        guessed_nums = [1,2,3,4]

        Output:
        {
            "won": False,
            "correct_nums": 1,
            "correct_locations": 1,
        }
        """

        # Succeed fast and immediately check for a win
        if guessed_nums == self.answer:
            return {
                "won": True,
                "correct_nums": self.count,
                "correct_locations": self.count
            }

        won = False
        correct_nums = 0
        correct_locations = 0

        # Using a set will allow us to have a more efficient lookup while
        # searching through the list of hidden numbers.
        answer_as_set = set(self.answer)

        frequencies_in_answer = Counter(self.answer)
        correct_counters = {
            key: {
                "correct_nums": 0,
                "correct_locations": 0
            } for key in answer_as_set
        }

        # scrap while figuring out strategy for dupes
        # {
        # 1: {correct_nums: 1, correct_locations: 1}
        # 4: {correct_nums: 2, correct_locations: 1}
        # }
        #

        # {
        # 0: {correct_nums: 0, correct_locations: 0}
        # 1: {correct_nums: 1, correct_locations: 0}
        # 3: {correct_nums: 0, correct_locations: 0}
        # 5: {correct_nums: 0, correct_locations: 0}
        # }
        # guess  [4, 4, 1, 2] 3 correct numbers and 2 correct locations
        # answer [1, 4, 1, 4]

        # {
        # 1: {correct_nums: 0, correct_locations: 0}
        # 4: {correct_nums: 2, correct_locations: 1}
        # }
        #

        # guess  [4, 4, 4, 4] 2 correct numbers and 2 correct locations
        # answer [1, 4, 1, 4]

        # guess  “2 2 1 1”, game responds “1 correct number and 0 correct location”
        # answer “0 1 3 5”

        curr_index = 0

        for num in guessed_nums:

            if self.answer[curr_index] == num:
                curr_correct_num_count = correct_counters[num]["correct_nums"]
                if curr_correct_num_count < frequencies_in_answer[num]:
                    correct_counters[num]["correct_nums"] += 1

                correct_counters[num]["correct_locations"] += 1

            elif num in answer_as_set:

                # if the number exists in the combination overall,
                # check if the current correct count is above the frequency of the number in the combo overall
                # if it is, do not increment that number's correct number count
                curr_correct_num_count = correct_counters[num]["correct_nums"]

                if curr_correct_num_count < frequencies_in_answer[num]:
                    correct_counters[num]["correct_nums"] += 1

            curr_index += 1

        for value in correct_counters.values():
            correct_nums += value["correct_nums"]
            correct_locations += value["correct_locations"]

        return {
            "won": won,
            "correct_nums": correct_nums,
            "correct_locations": correct_locations
        }
