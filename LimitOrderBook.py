import heapq

class LimitOrderBook:
    def __init__(self):
        self.buy_orders = []
        self.sell_orders = []
        self.market_orders = {"buy": [], "sell": []}
        self.limit_orders = {"buy": [], "sell": []}
        self.all_orders = []

    def add_order(self, order):
        fstr = (f"Add Order: Trader: {order.trader_id}, "
                f"Order Type: {order.order_type}, "
                f"Order Style: {order.order_style}, "
                f"Order Quantity: {order.quantity}, "
                f"Order Price: {order.price}, "
                f"Timestamp: {order.timestamp}")
        # self.all_orders.append(fstr)
        if order.order_style == "market":
            self.market_orders[order.order_type].append(order)
            self.execute_market_order(order)
        else:
            self.limit_orders[order.order_type].append(order)
            if order.order_type == "buy":
                heapq.heappush(self.buy_orders, order)
            else:
                heapq.heappush(self.sell_orders, order)

    def execute_market_order(self, order):
        fstr = (f"Execute Market Order: Trader: {order.trader_id}, "
                f"Order Type: {order.order_type}, "
                f"Order Style: {order.order_style}, "
                f"Order Quantity: {order.quantity}, "
                f"Order Price: {order.price}, "
                f"Timestamp: {order.timestamp}")
        # self.all_orders.append(fstr)
        if order.order_type == "buy":
            while order.quantity > 0 and self.sell_orders:
                best_sell = self.sell_orders[0]
                executed_quantity = min(order.quantity, best_sell.quantity)
                executed_price = best_sell.price

                # Execute the trade
                self.traders[order.trader_id].execute_trade(round(-executed_price * executed_quantity, 3), executed_quantity, order.order_style)
                self.traders[best_sell.trader_id].execute_trade(round(executed_price * executed_quantity, 3), -executed_quantity, best_sell.order_style)

                order.quantity -= executed_quantity
                best_sell.quantity -= executed_quantity

                if best_sell.quantity == 0:
                    heapq.heappop(self.sell_orders)
                if order.quantity == 0:
                    break

        elif order.order_type == "sell":
            while order.quantity > 0 and self.buy_orders:
                best_buy = self.buy_orders[0]
                executed_quantity = min(order.quantity, best_buy.quantity)
                executed_price = best_buy.price

                # Execute the trade
                self.traders[order.trader_id].execute_trade(round(executed_price * executed_quantity, 3), -executed_quantity, order.order_style)
                self.traders[best_buy.trader_id].execute_trade(round(-executed_price * executed_quantity, 3), executed_quantity, best_buy.order_style)

                order.quantity -= executed_quantity
                best_buy.quantity -= executed_quantity

                if best_buy.quantity == 0:
                    heapq.heappop(self.buy_orders)
                if order.quantity == 0:
                    break

    def cancel_order(self, order):
        if order in self.buy_orders:
            self.buy_orders.remove(order)
            heapq.heapify(self.buy_orders)
        elif order in self.sell_orders:
            self.sell_orders.remove(order)
            heapq.heapify(self.sell_orders)

    def match_orders(self, traders):
        while self.buy_orders and self.sell_orders:
            best_buy = self.buy_orders[0]
            best_sell = self.sell_orders[0]

            if best_buy.order_style == "market" or best_sell.order_style == "market" or best_buy.price >= best_sell.price:
                executed_price = best_sell.price if best_buy.order_style == "limit" else best_buy.price
                executed_quantity = min(best_buy.quantity, best_sell.quantity)

                traders[best_buy.trader_id].execute_trade(round(-executed_price * executed_quantity, 3), executed_quantity, best_buy.order_style)
                traders[best_sell.trader_id].execute_trade(round(executed_price * executed_quantity, 3), -executed_quantity, best_sell.order_style)

                best_buy.quantity -= executed_quantity
                best_sell.quantity -= executed_quantity

                if best_buy.quantity == 0:
                    heapq.heappop(self.buy_orders)
                if best_sell.quantity == 0:
                    heapq.heappop(self.sell_orders)
            else:
                break

    def get_best_bid(self):
        return round(self.buy_orders[0].price, 3) if self.buy_orders else None

    def get_best_ask(self):
        return round(self.sell_orders[0].price, 3) if self.sell_orders else None
