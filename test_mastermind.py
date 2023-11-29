from app import app
import os
from unittest import TestCase
from unittest.mock import patch

import mastermind

os.environ['DATABASE_URL'] = "postgresql:///mastermind_test"


app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False

mastermind.db.create_all()


class MastermindModelTestCase(TestCase):
    """Test Mastermind class."""

    @patch.object(mastermind.requests, "get")
    def setUp(self, mock_fetch):
        """What to do before every test runs."""

        mastermind.Guess.query.delete()
        mastermind.MastermindGame.query.delete()

        # Mock requests.get() return value to predict our random numbers and
        # avoid calling the real API
        mock_fetch.return_value.text = "1\n1\n2\n4\n"

        # Generate a test game instance
        test_game = mastermind.MastermindGame.generate_new_game()

        mastermind.db.session.commit()
        self.test_game = test_game

    def test_repr(self):
        """Test that the __repr__ method displays the string expected."""

        self.assertEqual(
            self.test_game.__repr__(),
            f"<MastermindGame #{self.test_game.id}, answer: [1, 1, 2, 4]>"
        )

    @patch.object(mastermind.requests, "get")
    def test_make_new_game(self, mock_fetch):
        """Test that the Mastermind factory method makes a new game successfully. """

        mock_fetch.return_value.text = "1\n2\n3\n4\n"

        # Check that only one instance exists in the db before creating another
        self.assertEqual(mastermind.MastermindGame.query.count(), 1)

        mastermind.MastermindGame.generate_new_game()

        mastermind.db.session.commit()
        self.assertEqual(mastermind.MastermindGame.query.count(), 2)

    def test_score_partially_wrong_guess(self):
        """Test that a game instance can score a guess successfully."""

        score = self.test_game.score_guess([1, 7, 6, 4])
        self.assertEqual(
            score,
            {
                "won": False,
                "correct_nums": 2,
                "correct_locations": 2,
            }
        )

    def test_score_entirely_wrong_guess(self):
        """Test that a game instance can score a guess successfully."""

        score = self.test_game.score_guess([0, 0, 0, 0,])
        self.assertEqual(
            score,
            {
                "won": False,
                "correct_nums": 0,
                "correct_locations": 0,
            }
        )

    def test_score_correct_guess(self):
        """Test that a game instance can score a guess successfully."""

        score = self.test_game.score_guess([1, 1, 2, 4])
        self.assertEqual(
            score,
            {
                "won": True,
                "correct_nums": 4,
                "correct_locations": 4,
            }
        )

    def test_partially_correct_guess_feedback(self):
        """Test that a game instance can handle a guess successfully."""

        self.test_game.handle_guess([1, 1, 1, 1])
        mastermind.db.session.commit()

        self.assertEqual(len(self.test_game.guess_history), 1)
        self.assertEqual(
            self.test_game.feedback,
            ["2 correct number(s) and 2 correct location(s)."]
        )

    def test_incorrect_guess_feedback(self):
        """Test that a game instance can handle a guess successfully."""

        self.test_game.handle_guess([0, 0, 0, 0])
        mastermind.db.session.commit()

        self.assertEqual(len(self.test_game.guess_history), 1)
        self.assertEqual(
            self.test_game.feedback,
            ["All incorrect."]
        )

    def test_validate_num(self):
        """Test that a game instance can validate an individual number."""

        # Test that an ValueError is raised for an invalid input
        self.assertRaises(ValueError, self.test_game.validate_num, 8)

        # Test that True is received for a valid input
        self.assertTrue(self.test_game.validate_num(7))


class GuessModelTestCase(TestCase):
    """Test Guess class."""

    @patch.object(mastermind.requests, "get")
    def setUp(self, mock_fetch):
        """What to do before every test runs."""

        mastermind.Guess.query.delete()
        mastermind.MastermindGame.query.delete()

        # Mock requests.get() return value to predict our random numbers and
        # avoid calling the real API
        mock_fetch.return_value.text = "1\n1\n2\n4\n"

        # Generate a test game instance
        test_game = mastermind.MastermindGame.generate_new_game()

        mastermind.db.session.commit()

        test_guess = mastermind.Guess(
            game_id=test_game.id,
            numbers_guessed=[0, 0, 0, 0],
            correct_num_count=0,
            correct_location_count=0
        )
        mastermind.db.session.add(test_guess)
        mastermind.db.session.commit()

        self.test_game = test_game
        self.test_guess = test_guess

    def test_repr(self):
        """Test that the __repr__ method displays the string expected."""

        guess = self.test_game.guess_history[0]

        self.assertEqual(
            guess.__repr__(),
            f"<Guess #{self.test_guess.id} for game {self.test_game.id}, [0, 0, 0, 0]>"
        )

    def test_make_new_guess(self):
        """Test that the Mastermind factory method makes a new game successfully. """

        # Check that only one instance exists in the db before creating another
        self.assertEqual(mastermind.Guess.query.count(), 1)

        mastermind.Guess.generate_new_guess(
            game_id=self.test_game.id,
            numbers_guessed=[1, 2, 3, 4],
            correct_num_count=2,
            correct_location_count=2
        )

        mastermind.db.session.commit()
        self.assertEqual(mastermind.Guess.query.count(), 2)
