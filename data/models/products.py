import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, orm
from sqlalchemy_serializer import SerializerMixin

from data.db_session import SqlAlchemyBase


class Product(SerializerMixin, SqlAlchemyBase):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, autoincrement=True)
    shop_id = Column(Integer, ForeignKey('shops.id'))
    category = Column(String)
    name = Column(String)
    description = Column(String)
    price = Column(Integer)
    logo_url = Column(String)
    stock_quantity = Column(Integer)
    created_at = Column(String, default=datetime.date.today())
    shop = orm.relationship('Shop')
