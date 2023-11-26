from unittest import TestCase

from app import app, games

# Make Flask errors be real errors, not HTML pages with error info
app.config['TESTING'] = True


class MastermindAppTestCase(TestCase):
    """Test Flask Mastermind app."""

    def setUp(self):
        """What to do before every test runs."""

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
