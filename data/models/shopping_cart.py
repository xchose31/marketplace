import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, orm, JSON
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase


class Shopping_cart(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'shopping_carts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    data = Column(MutableList.as_mutable(JSON), default=[])
