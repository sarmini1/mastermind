from flask_wtf import FlaskForm


class CSRFForm(FlaskForm):
    """Blank form for CSRF protection only."""
