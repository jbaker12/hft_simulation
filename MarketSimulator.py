import random
from LimitOrderBook import *
from Order import *

class MarketSimulator:
    def __init__(self):
        self.lob = LimitOrderBook()
        self.traders = {}
        self.time = 0
        self.metrics = {"price_history": [], "bid_ask_spread": [], "order_flow_imbalance": [], "profitable_traders": 0.0}
        self.order_id_counter = 0

    def add_trader(self, trader):
        self.traders[trader.trader_id] = trader

    def generate_random_order(self, trader_id):
        trader = self.traders[trader_id]
        order_type = random.choice(["buy", "sell"])
        order_style = random.choice(["market", "limit"])

        # Set trade Price
        if order_style == "limit":
            best_bid = self.lob.get_best_bid() or 100
            best_ask = self.lob.get_best_ask() or 100
            if trader.trader_type == "market_maker":
                price = round(best_bid + (random.choice([-0.1, 0.1]) * random.uniform(0.5, 1.5)), 3)
            elif trader.trader_type == "retail":
                price = best_ask if order_type == "buy" else best_bid
            else:
                price = round(random.uniform(99, 101), 3)
        else:
            price = 0.0

        # Set trade Quantity
        if trader.trader_type == "institutional":
            quantity = random.randint(10, 100)
        elif trader.trader_type == "market_maker":
            quantity = random.randint(25, 500)
        else:
            quantity = random.randint(1, 25)
        self.order_id_counter += 1
        order = Order(self.order_id_counter, trader_id, order_type, price, quantity, self.time, order_style)
        self.lob.add_order(order)

    def record_metrics(self):
        best_bid = self.lob.get_best_bid()
        best_ask = self.lob.get_best_ask()
        if best_bid and best_ask:
            self.metrics["price_history"].append(round((best_bid + best_ask) / 2, 3))
            self.metrics["bid_ask_spread"].append(round(best_ask - best_bid, 3))
            buy_volume = sum(o.quantity for o in self.lob.buy_orders)
            sell_volume = sum(o.quantity for o in self.lob.sell_orders)
            self.metrics["order_flow_imbalance"].append(round((buy_volume - sell_volume) / (buy_volume + sell_volume) if buy_volume + sell_volume > 0 else 0, 3))
        profitable_count = sum(1 for trader in self.traders.values() if trader.profit > 0)
        self.metrics["profitable_traders"] = round((profitable_count / len(self.traders)) * 100, 3) if self.traders else 0.0

    def run_simulation(self, steps=100):
        self.lob.traders = self.traders
        for _ in range(steps):
            self.time += 1
            for trader_id in self.traders:
                if random.random() < 0.1:
                    self.generate_random_order(trader_id)
            self.lob.match_orders(self.traders)
            self.record_metrics()