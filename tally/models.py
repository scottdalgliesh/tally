from datetime import date as date_obj

from flask_login import UserMixin
from sqlalchemy import event

from . import db, login_manager


def _fk_pragma_on_connect(dbapi_con, con_record):  # pylint: disable=unused-argument
    """Enable foreign key enforcement for SQLite3"""
    dbapi_con.execute('pragma foreign_keys=ON')


event.listen(db.engine, 'connect', _fk_pragma_on_connect)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    username = db.Column(db.String(30), primary_key=True)
    password = db.Column(db.String(60), nullable=False)
    categories = db.relationship('Category', back_populates='user',
                                 cascade='all, delete-orphan')
    bills = db.relationship('Bill', back_populates='user',
                            cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User(username="{self.username}")>'


class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)
    username = db.Column(
        db.String(30),
        db.ForeignKey('users.username', onupdate='CASCADE', ondelete='CASCADE')
    )
    hidden = db.Column(db.Boolean, default=False)
    user = db.relationship('User', back_populates='categories')
    bills = db.relationship('Bill', back_populates='category',
                            cascade='all, delete-orphan')
    __table_args__ = (
        db.UniqueConstraint('username', 'name', name='user-category-uc'),
    )

    def __repr__(self):
        return f'<Category(name="{self.name}", username="{self.username}")>'


class Bill(db.Model):
    __tablename__ = 'bills'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    descr = db.Column(db.String, nullable=False)
    value = db.Column(db.Float, nullable=False)
    username = db.Column(
        db.String(30),
        db.ForeignKey('users.username', onupdate='CASCADE', ondelete='CASCADE')
    )
    category_id = db.Column(
        db.Integer,
        db.ForeignKey('categories.id', onupdate='CASCADE', ondelete='CASCADE')
    )
    user = db.relationship('User', back_populates='bills')
    category = db.relationship('Category', back_populates='bills')

    def __repr__(self):
        return (
            f'<Bill(date="{self.date}", descr="{self.descr}", '
            f'value="{self.value}", username="{self.username}", '
            f'category_id={self.category_id})>')

    @classmethod
    def from_name(cls, date: date_obj, descr: str, value: float,
                  username: str, category_name: str):
        """Create new Bill by category_name, rather than category_id"""
        category = db.session.query(Category).filter_by(    # pylint:disable=no-member
            username=username, name=category_name).one()
        return cls(date=date, descr=descr, value=value,
                   username=username, category_id=category.id)
