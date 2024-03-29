from __future__ import annotations

from typing import Optional

from flask_login import UserMixin

from ..extensions import db, login_manager


@login_manager.user_loader
def load_user(username: str) -> Optional[User]:
    """Helper function required by Flask-login to facilitate user session."""
    return User.query.get(username)  # type:ignore


class User(db.Model, UserMixin):
    """User database schema."""

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False)
    categories = db.relationship("Category", back_populates="user", cascade="all, delete-orphan")
    bills = db.relationship("Bill", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f'<User(username="{self.username}")>'

    def get_category_options(self) -> list[tuple[int, str]]:
        """Get user's category options for bills."""
        # pylint: disable=not-an-iterable
        # -1 used for un-categorized items since None is not compatible with SelectField
        choices = [(category.id, category.name) for category in self.categories]
        choices.insert(0, (-1, ""))
        return choices
