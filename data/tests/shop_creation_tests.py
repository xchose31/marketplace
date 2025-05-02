from .. import db_session
from ..models.shops import Shop



def shop_creation_test(form):
    db_sess = db_session.create_session()
    shop = db_sess.query(Shop).filter(Shop.name == form.name.data).first()
    if shop:
        db_sess.close()
        return False
    return True