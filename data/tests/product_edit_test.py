from sqlalchemy.orm.attributes import flag_modified

from .. import db_session
from ..models.shops import Shop
from ..models.shopping_cart import Shopping_cart



def product_edit_test(product):
    db_sess = db_session.create_session()
    carts = db_sess.query(Shopping_cart).all()
    for cart in carts:
        for item in cart.data:
            if item['product_id'] == product.id:
                item['price'] = product.price
                flag_modified(cart, 'data')
                db_sess.commit()
    return True