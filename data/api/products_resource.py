from flask_restful import Resource, abort
from flask import jsonify

from data import db_session
from data.models.products import Product


def abort_if_product_not_found(product_id):
    session = db_session.create_session()
    product = session.query(Product).get(product_id)
    if not product:
        abort(404, message=f"Product {product_id} not found")


class ProductsResource(Resource):
    def get(self, product_id):
        abort_if_product_not_found(product_id)
        db_sess = db_session.create_session()
        product = db_sess.query(Product).get(product_id)
        return jsonify({'product': product.to_dict(
            only=('name', 'description', 'price', 'stock_quantity',))})


class ProductsListResource(Resource):
    def get(self):
        db_sess = db_session.create_session()
        products = db_sess.query(Product).all()
        return jsonify(
            {'products': [item.to_dict(only=('name', 'description', 'price', 'stock_quantity')) for item in products]})
