class Trader:
    def __init__(self, trader_id, trader_type, balance=100000, holdings=0):
        self.trader_id = trader_id
        self.trader_type = trader_type
        self.balance = balance
        self.holdings = holdings
        self.profit = 0
        self.num_trades = 0
        self.profitable_trades = 0
        self.profitability_rate = 0
        self.num_market_order = 0
        self.num_limit_order = 0
        self.market_order_profit = 0
        self.limit_order_profit = 0

    def execute_trade(self, balance_change, holdings_change, order_style):
        self.balance += balance_change
        self.holdings += holdings_change
        self.profit += balance_change
        self.num_trades += 1

        # Track profit based on order type
        if order_style == "market":
            self.market_order_profit += balance_change
            self.num_market_order += 1
        elif order_style == "limit":
            self.limit_order_profit += balance_change
            self.num_limit_order += 1

        if balance_change > 0:
            self.profitable_trades += 1
        if self.profitable_trades > 1:
            self.profitability_rate = self.profitable_trades / self.num_trades
