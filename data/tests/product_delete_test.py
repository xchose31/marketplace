from sqlalchemy.orm.attributes import flag_modified

from .. import db_session
from ..models.shopping_cart import Shopping_cart


def product_delete_test(product_id):
    db_sess = db_session.create_session()
    carts = db_sess.query(Shopping_cart).all()
    for cart in carts:
        for item in cart.data:
            if item['product_id'] == product_id:
                cart.data.remove(item)
                flag_modified(cart, 'data')
                db_sess.commit()
    db_sess.close()
    return True
