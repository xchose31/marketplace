import datetime
from flask_login import UserMixin
from sqlalchemy import Column, Integer, String, ForeignKey, orm
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase


class Shop(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'shops'

    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    description = Column(String)
    logo_url = Column(String)
    created_date = Column(String, default=datetime.date.today())
    rating = Column(Integer)
    user = orm.relationship('User')