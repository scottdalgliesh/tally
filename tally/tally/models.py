from __future__ import annotations

from datetime import date as date_obj
from typing import Optional

from sqlalchemy.sql import elements

from ..auth.models import User
from ..extensions import db


class Category(db.Model):
    """Database schema for categories."""

    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE")
    )
    hidden = db.Column(db.Boolean, default=False)
    user = db.relationship("User", back_populates="categories")
    bills = db.relationship("Bill", back_populates="category", cascade="all, delete-orphan")
    __table_args__ = (db.UniqueConstraint("user_id", "name", name="user-category-uc"),)

    def __repr__(self) -> str:
        return f'<Category(name="{self.name}", user_id={self.user_id})>'

    @classmethod
    def from_name(cls, name: str, username: str, hidden: bool = False) -> Category:
        """Create new Category by username, rather than user_id"""
        user = User.query.filter_by(username=username).one()
        return cls(name=name, user_id=user.id, hidden=hidden)


class Bill(db.Model):
    """Database schema for bills (individual purchase records)."""

    __tablename__ = "bills"
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    descr = db.Column(db.String, nullable=False)
    value = db.Column(db.Float, nullable=False)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE")
    )
    category_id = db.Column(
        db.Integer, db.ForeignKey("categories.id", onupdate="CASCADE", ondelete="CASCADE")
    )
    user = db.relationship("User", back_populates="bills")
    category = db.relationship("Category", back_populates="bills")

    def __repr__(self) -> str:
        return (
            f'<Bill(date="{self.date}", descr="{self.descr}", '
            f'value="{self.value}", user_id={self.user_id}, '
            f"category_id={self.category_id})>"
        )

    @classmethod
    def from_name(
        cls, date: date_obj, descr: str, value: float, username: str, category_name: str
    ) -> Bill:
        """Create new Bill by category_name, rather than category_id"""
        user = User.query.filter_by(username=username).one()
        category = Category.query.filter_by(user_id=user.id, name=category_name).one()
        return cls(date=date, descr=descr, value=value, user_id=user.id, category_id=category.id)

    @staticmethod
    def generate_filters(
        user_id: int,
        start_date: Optional[date_obj] = None,
        end_date: Optional[date_obj] = None,
        description: Optional[str] = None,
        categories: Optional[list[int]] = None,
        exclude_hidden: bool = True,
        min_value: Optional[int] = None,
        max_value: Optional[int] = None,
    ) -> list[elements.BinaryExpression]:
        """Build filtered search query.

        Note: The query to which the filters are applied must include a join to
        Table "Category" in order to use "exclude_hidden". This will automatically
        exclude uncategorized transactions.
        """
        # pylint: disable=[singleton-comparison, no-member, protected-access]
        filters = []
        filters.append(Bill.user_id == user_id)
        if start_date:
            filters.append(Bill.date >= start_date)
        if end_date:
            filters.append(Bill.date <= end_date)
        if description:
            filters.append(Bill.descr.contains(description))
        if categories:
            filters.append(Bill.category_id.in_(categories))
        if exclude_hidden:
            filters.append(Category.hidden == False)
        if min_value:
            filters.append(Bill.value >= min_value)
        if max_value:
            filters.append(Bill.value <= max_value)
        return filters
