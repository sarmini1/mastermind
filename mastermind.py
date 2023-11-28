from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ARRAY
from sqlalchemy.ext.mutable import MutableList
import requests

from datetime import datetime
from collections import Counter

db = SQLAlchemy()


class MastermindGame(db.Model):
    "The Mastermind game."

    __tablename__ = 'mastermind_games'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True,
    )

    num_count = db.Column(
        db.Integer,
        nullable=False,
        default=4,
    )

    answer = db.Column(
        MutableList.as_mutable(ARRAY(db.Integer)),
        nullable=False,
    )

    has_won = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    game_over = db.Column(
        db.Boolean,
        nullable=False,
        default=False,
    )

    guess_history = db.relationship(
        'Guess',
        order_by='Guess.occurred_at.desc()'
    )

    def __repr__(self):
        return f"<MastermindGame #{self.id}, answer: {self.answer}>"

    @classmethod
    def generate_new_game(cls, num_count=4):
        """Creates and returns a new instance of the class."""

        random_nums = cls._fetch_random_nums(num_count)
        new_game = MastermindGame(
            answer=random_nums,
            num_count=num_count
        )
        db.session.add(new_game)
        return new_game

    @classmethod
    def _fetch_random_nums(cls, num_count=4):
        """
        Makes an API request to fetch a specified num_count of random numbers.
        If no num_count is provided as a parameter, the default will be 4.

        Returns fetched numbers in an array of integers, like: [1,2,3,4]

        """

        response = requests.get(
            "https://www.random.org/integers/",
            params={
                "num": num_count,
                "min": 0,
                "max": 7,
                "col": 1,
                "base": 10,
                "format": "plain",
                "rnd": "new",
            }
        )

        parsed_response = response.text.splitlines()
        combined_nums = [int(s) for s in parsed_response]

        return combined_nums

    def handle_guess(self, numbers_guessed):
        """
        Takes in a list of numbers_guessed, scores them, and updates the game
        instance accordingly as outlined below. Returns None.

        Always:

            - Scores the incoming guess by correct nums and correct locations
            - Creates a new Guess instance and adds to db session
            - Decrements remaining_guesses by 1

        If this was their last remaining guess:
            - Sets game_over to True

        If their guess is correct:
            - Updates the has_won property to True
            - Sets game_over to True

        """

        score = self.score_guess(numbers_guessed)

        # The below factory method called db.session.add() for the new guess
        Guess.generate_new_guess(
            game_id=self.id,
            numbers_guessed=numbers_guessed,
            correct_num_count=score["correct_nums"],
            correct_location_count=score["correct_locations"]
        )

        if self.remaining_guesses == 0:
            self.game_over = True

        if score["won"]:
            self.game_over = True
            self.has_won = True

    @property
    def remaining_guesses(self):
        """
        Determines how many guesses are remaining for the current game instance.
        Returns this number as an integer.
        """
        return 10 - len(self.guess_history)

    @property
    def feedback(self):
        """
        Iterates through the current instance's history of guesses and returns
        a list of strings describing the result of each guess, like:

        ["All incorrect.", "2 correct number(s) and 1 correct location(s), ..."]

        """

        feedback = []

        for guess in self.guess_history:
            text = self._generate_feedback_text(
                guess.correct_num_count,
                guess.correct_location_count
            )
            feedback.append(text)

        return feedback

    def _generate_feedback_text(self, correct_nums, correct_locations):
        """
        Receives correct_nums and correct_locations params as integers and
        returns a string containing that information. If the score indicates
        no correct numbers and locations, this method will return "All incorrect."
        Otherwise the returned string will contain information like:

        Input: (2, 2)

        Output: "2 correct number(s) and 2 correct location(s)."

        """

        if correct_nums == 0 and correct_locations == 0:
            return "All incorrect."

        return f"{correct_nums} correct number(s) and {correct_locations} correct location(s)."

    def score_guess(self, numbers_guessed):
        """
        Takes in a list of numbers_guessed, compares them to the hidden answer numbers,
        and returns the correct number and correct location counts in a dictionary.

        For example, if the hidden answer numbers were [1,5,7,8]:

        Input:
        numbers_guessed = [1,2,3,4]

        Output:
        {
            "won": False,
            "correct_nums": 1,
            "correct_locations": 1,
        }
        """

        # Succeed fast and immediately check for a win
        if numbers_guessed == self.answer:
            return {
                "won": True,
                "correct_nums": self.num_count,
                "correct_locations": self.num_count
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

        for num in numbers_guessed:

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


class Guess(db.Model):
    "An individual guess made for a particular game."

    __tablename__ = 'guesses'

    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    game_id = db.Column(
        db.Integer,
        db.ForeignKey('mastermind_games.id', ondelete="cascade"),
        nullable=False,
    )

    numbers_guessed = db.Column(
        MutableList.as_mutable(ARRAY(db.Integer)),
        nullable=False,
    )

    correct_num_count = db.Column(
        db.Integer,
        nullable=False,
    )

    correct_location_count = db.Column(
        db.Integer,
        nullable=False,
    )

    occurred_at = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
    )

    def __repr__(self):
        return f"<Guess #{self.id} for game {self.game_id}, {self.numbers_guessed}>"

    @classmethod
    def generate_new_guess(
        cls,
        game_id,
        numbers_guessed,
        correct_num_count,
        correct_location_count,
    ):
        """
        Factory method to create, add and return a new instance of the Guess class.
        """

        new_guess = Guess(
            game_id=game_id,
            numbers_guessed=numbers_guessed,
            correct_num_count=correct_num_count,
            correct_location_count=correct_location_count,
        )
        db.session.add(new_guess)
        return new_guess


def connect_db(app):
    """Connect to database."""

    app.app_context().push()
    db.app = app
    db.init_app(app)
