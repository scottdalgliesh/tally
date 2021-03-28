from flask_login import UserMixin

from .. import db, login_manager


@login_manager.user_loader
def load_user(username):
    return User.query.get(username)


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

    def get_id(self):
        return self.username
