class Order:
    def __init__(self, order_id, trader_id, order_type, price, quantity, timestamp, order_style):
        self.order_id = order_id
        self.trader_id = trader_id
        self.order_type = order_type
        self.price = price
        self.quantity = quantity
        self.timestamp = timestamp
        self.order_style = order_style

    def __lt__(self, other):
        if self.order_type == "buy" and self.order_style == "limit":
            return (self.price, self.timestamp) > (other.price, other.timestamp)
        elif self.order_type == "sell" and self.order_style == "limit":
            return (self.price, self.timestamp) < (other.price, other.timestamp)
        else:
            return self.timestamp < other.timestamp
