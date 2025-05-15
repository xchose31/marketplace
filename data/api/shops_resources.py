from flask_restful import Resource, abort
from flask import jsonify

from data import db_session
from data.models.shops import Shop

def abort_if_shop_not_found(shop_id):
    session = db_session.create_session()
    shop = session.query(Shop).get(shop_id)
    if not shop:
        abort(404, message=f"Shop {shop_id} not found")



class ShopsResource(Resource):
    def get(self, shop_id):
        abort_if_shop_not_found(shop_id)
        db_sess = db_session.create_session()
        shop = db_sess.query(Shop).get(shop_id)
        return jsonify({'shop': shop.to_dict(
            only=('name', 'description', 'owner_id'))})


class ShopsListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        shops = db_sess.query(Shop).all()
        return jsonify({'shops': [item.to_dict(only=('name', 'description', 'owner_id')) for item in shops]})
