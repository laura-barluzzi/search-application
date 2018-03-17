from secrets import token_hex

from elasticsearch_dsl import DocType
from elasticsearch_dsl import Text
from flask_mongoengine import MongoEngine
from flask_security import RoleMixin
from flask_security import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
mongo = MongoEngine()


class RolesUsers(db.Model):
    __tablename__ = 'roles_users'

    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column('user_id', db.Integer(), db.ForeignKey('user.id'))
    role_id = db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))


class Role(db.Model, RoleMixin):
    __tablename__ = 'role'

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    user_name = db.Column(db.String(255), unique=True)
    access_token = db.Column(db.String(255), unique=True, index=True,
                             default=lambda: token_hex(127))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    roles = db.relationship('Role', secondary='roles_users',
                            backref=db.backref('users', lazy='dynamic'))


class Document(mongo.Document):
    content = mongo.StringField(required=True)


# from https://goo.gl/v9VnRp
class DocumentIndex(DocType):
    id = Text()
    content = Text()

    class Meta:
        index = 'documents'
