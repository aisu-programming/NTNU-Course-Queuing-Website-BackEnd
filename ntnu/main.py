''' Libraries '''
from database.model import OrderObject



''' Functions '''
def get_all_orders():
    orders = OrderObject.query.all()
    print("\n\nTest\n\n")
    print(orders)
    return orders