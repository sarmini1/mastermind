from app import app, CURR_GAME_KEY
import os
from unittest import TestCase
from unittest.mock import patch

import mastermind
# from mastermind import db, MastermindGame, Guess

os.environ['DATABASE_URL'] = "postgresql:///mastermind_test"

app.config['TESTING'] = True

mastermind.db.create_all()


class MastermindAppTestCase(TestCase):
    """Test Flask Mastermind app."""

    @patch.object(mastermind.requests, "get")
    def setUp(self, mock_fetch):
        """What to do before every test runs."""

        mastermind.Guess.query.delete()
        mastermind.MastermindGame.query.delete()

        # Mock requests.get() return value to predict our random numbers and
        # avoid calling the real API
        mock_fetch.return_value.text = "1\n2\n3\n4\n"

        # Generate a test game instance
        test_game = mastermind.MastermindGame.generate_new_game()

        mastermind.db.session.commit()
        self.test_game_id = test_game.id

    def test_homepage(self):
        """Make sure the introductory HTML is displayed. """

        with app.test_client() as client:
            response = client.get('/')
            html = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(
                "<h2>Start a new game of Mastermind below!</h2>",
                html
            )

    def test_start_new_game(self):
        """
        Test that we can start a new game and get redirected to play
        successfully.
        """

        with app.test_client() as client:
            response = client.post(
                '/new-game',
                data={
                    "difficulty": "4"
                },
                follow_redirects=True
            )
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn("New game started!", html)
            self.assertIn("You have 10 guesses left.", html)

    def test_make_valid_guess(self):
        """
        Test that we can submit a valid guess for a new game instance and
        have its feedback appear on the page.
        """

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session[CURR_GAME_KEY] = self.test_game_id

            response = client.post(
                '/submit-guess',
                data={
                    "num-0": "4",
                    "num-1": "4",
                    "num-2": "4",
                    "num-3": "4",
                },
                follow_redirects=True
            )
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn("You have 9 guesses left.", html)
            self.assertIn(
                "1 correct number(s) and 1 correct location(s)", html)

    def test_make_invalid_guess(self):
        """
        Test that we can submit an invalid guess for a new game instance and see
        that it wasn't counted and we were alerted appropriately.
        """

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session[CURR_GAME_KEY] = self.test_game_id

            response = client.post(
                '/submit-guess',
                data={
                    "num-0": "not",
                    "num-1": "good",
                    "num-2": "data",
                    "num-3": "nope",
                },
                follow_redirects=True
            )
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn("You have 10 guesses left.", html)
            self.assertIn(
                "Your guess is invalid; you must only input integers here.",
                html
            )

    def test_make_correct_guess(self):
        """
        Test that we can submit the correct guess and get redirected to the
        win page.
        """

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session[CURR_GAME_KEY] = self.test_game_id

            response = client.post(
                '/submit-guess',
                data={
                    "num-0": "1",
                    "num-1": "2",
                    "num-2": "3",
                    "num-3": "4",
                },
                follow_redirects=True
            )
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn("You won with 9 guesses remaining!", html)

    def test_lose(self):
        """
        Test that we can submit the correct amount of wrong guesses to get to the
        loss page.
        """

        with app.test_client() as client:
            with client.session_transaction() as change_session:
                change_session[CURR_GAME_KEY] = self.test_game_id

            # Make 9 wrong guesses
            for i in range(10):
                client.post(
                    '/submit-guess',
                    data={
                        "num-0": "1",
                        "num-1": "1",
                        "num-2": "1",
                        "num-3": "1",
                    },
                    follow_redirects=True
                )

            # Make one last wrong guess to get to the loss page
            response = client.post(
                '/submit-guess',
                data={
                    "num-0": "1",
                    "num-1": "1",
                    "num-2": "1",
                    "num-3": "1",
                },
                follow_redirects=True
            )
            html = response.get_data(as_text=True)

            self.assertEqual(response.status_code, 200)
            self.assertIn("The hidden combination was: [1, 2, 3, 4]", html)
