# pylint: disable=[missing-class-docstring]
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    PasswordField,
    StringField,
    SubmitField,
    ValidationError,
)
from wtforms.validators import DataRequired, EqualTo, Length

from .models import User


class BaseUserForm(FlaskForm):
    username = StringField("username", validators=[DataRequired(), Length(1, 30)])
    password = PasswordField("Password", validators=[DataRequired()])


class UserRegisterForm(BaseUserForm):
    confirm_password = PasswordField(
        "Confirm Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username: StringField) -> None:
        """Verify username is unique."""
        # pylint: disable=[no-self-use]
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("Username is taken.")


class UserLoginForm(BaseUserForm):
    remember = BooleanField("Remember me")
    submit = SubmitField("Login")


class UserUpdateForm(BaseUserForm):
    password = None
    submit = SubmitField("Update")

    def validate_username(self, username: StringField) -> None:
        """Verify new username is not same as old username or not unique."""
        # pylint: disable=[no-self-use]
        if username.data == current_user.username:
            return
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("Username is taken.")
