import pandas as pd
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor
import matplotlib.pyplot as plt

from MarketSimulator import *
from Trader import *


def run_single_simulation(simulation_id, num_steps, num_traders_to_make):
    simulator = MarketSimulator()
    trader_types = {}

    simulator.add_trader(Trader(1, "market_maker"))
    trader_types[1] = "market_maker"

    for i in range(2, num_traders_to_make):
        num = random.randint(1, 100)
        if num < 2:
            simulator.add_trader(Trader(i, "market_maker"))
            trader_types[i] = "market_maker"
        elif num < 30:
            simulator.add_trader(Trader(i, "institutional"))
            trader_types[i] = "institutional"
        else:
            simulator.add_trader(Trader(i, "retail"))
            trader_types[i] = "retail"

    simulator.run_simulation(steps=num_steps)

    simulation_result = {
        "trader_balances": {},
        "trader_profits": {},
        "retail_market_order_profits": {},
        "retail_limit_order_profits": {},
        "retail_num_market": {},
        "retail_num_limit": {}
    }
    for trader_id, trader in simulator.traders.items():
        simulation_result["trader_balances"][trader_id] = trader.balance
        simulation_result["trader_profits"][trader_id] = trader.profit

        if trader.trader_type == "retail":
            simulation_result["retail_market_order_profits"][trader_id] = trader.market_order_profit
            simulation_result["retail_limit_order_profits"][trader_id] = trader.limit_order_profit
            simulation_result["retail_num_market"][trader_id] = trader.num_market_order
            simulation_result["retail_num_limit"][trader_id] = trader.num_limit_order

    return simulation_result, trader_types


if __name__ == "__main__": # Add this block
    # Initialize the list to store simulation results
    all_results = []
    all_trader_types = {}

    # Number of simulations
    num_simulations = 100000
    num_steps = 10000

    # num_simulations = 100
    # num_steps = 100

    # Run multiple simulations in parallel
    with ProcessPoolExecutor() as executor:
        futures = []
        for sim_num in range(num_simulations):
            num_traders_to_make = random.randint(4, 100)
            future = executor.submit(run_single_simulation, sim_num, num_steps, num_traders_to_make)
            futures.append(future)

        # Collect results as they become available
        for future in tqdm(futures, desc="Collecting Results"):
            simulation_result, trader_types = future.result()
            all_results.append(simulation_result)
            all_trader_types[len(all_results) - 1] = trader_types #Store trader types in a dict.

    # Initialize accumulators for each trader type
    total_balance_market_maker = []
    total_profit_market_maker = []
    total_balance_institutional = []
    total_profit_institutional = []
    total_balance_retail = []
    total_profit_retail = []
    # Order Type
    total_market_order_profit_retail = []
    total_limit_order_profit_retail = []

    # Iterate through all simulation results to accumulate the balances and profits
    for index, result in enumerate(all_results):
        trader_balances = result["trader_balances"]
        trader_profits = result["trader_profits"]
        retail_market_order_profits = result["retail_market_order_profits"]
        retail_limit_order_profits = result["retail_limit_order_profits"]

        trader_types = all_trader_types[index]

        # Trader Stats
        for trader_id, balance in trader_balances.items():
            trader_type = trader_types.get(trader_id)
            if trader_type == "institutional":
                total_balance_institutional.append(balance)
                total_profit_institutional.append(trader_profits[trader_id])
            elif trader_type == "retail":
                total_balance_retail.append(balance)
                total_profit_retail.append(trader_profits[trader_id])
                total_market_order_profit_retail.append(retail_market_order_profits.get(trader_id, 0))
                total_limit_order_profit_retail.append(retail_limit_order_profits.get(trader_id, 0))
            elif trader_type == "market_maker":
                total_balance_market_maker.append(balance)
                total_profit_market_maker.append(trader_profits[trader_id])

    # Calculate the averages for each trader type
    num_market_makers = len(total_balance_market_maker)
    num_institutional = len(total_balance_institutional)
    num_retail = len(total_balance_retail)

    avg_balance_market_maker = sum(total_balance_market_maker) / num_market_makers if num_market_makers > 0 else 0
    avg_profit_market_maker = sum(total_profit_market_maker) / num_market_makers if num_market_makers > 0 else 0

    avg_balance_institutional = sum(total_balance_institutional) / num_institutional if num_institutional > 0 else 0
    avg_profit_institutional = sum(total_profit_institutional) / num_institutional if num_institutional > 0 else 0

    avg_balance_retail = sum(total_balance_retail) / num_retail if num_retail > 0 else 0
    avg_profit_retail = sum(total_profit_retail) / num_retail if num_retail > 0 else 0

    # Order Tap
    avg_market_order_profit_retail = sum(total_market_order_profit_retail) / len(total_market_order_profit_retail) if total_market_order_profit_retail else 0
    avg_limit_order_profit_retail = sum(total_limit_order_profit_retail) / len(total_limit_order_profit_retail) if total_limit_order_profit_retail else 0


    pd.set_option('display.float_format', '{:,.2f}'.format)
    # Print results for each trader type
    print("Market Maker Statistics:")
    print(f"\tNumber of Market Makers: {num_market_makers}")
    print(f"\tAverage Market Maker Balance: ${avg_balance_market_maker:.2f}")
    print(f"\tAverage Market Maker Profit: ${avg_profit_market_maker:.2f}")
    print(f"\tSummary Statistics: \n{pd.Series(total_profit_market_maker).describe()}")

    print("Institutional Trader Statistics:")
    print(f"\tNumber of Institutional Traders: {num_institutional}")
    print(f"\tAverage Trader Balance: ${avg_balance_institutional:.2f}")
    print(f"\tAverage Trader Profit: ${avg_profit_institutional:.2f}")
    print(f"\tSummary Statistics: \n{pd.Series(total_profit_institutional).describe()}")

    print("Retail Trader Statistics:")
    print(f"\tNumber of Retail Traders: {num_retail}")
    print(f"\tAverage Trader Balance: ${avg_balance_retail:.2f}")
    print(f"\tAverage Trader Profit: ${avg_profit_retail:.2f}")
    print(f"\tAverage Market Order Profit: ${avg_market_order_profit_retail:.2f}")
    print(f"\tAverage Limit Order Profit: ${avg_limit_order_profit_retail:.2f}")
    print(f"\tProfit Summary Statistics: \n{pd.Series(total_profit_retail).describe()}")
    print(f"\tMarket Order Summary Statistics: \n{pd.Series(total_market_order_profit_retail).describe()}")
    print(f"\tLimit Order Summary Statistics: \n{pd.Series(total_limit_order_profit_retail).describe()}")




    # Plots

    # Log Based
    plt.figure(figsize=(10, 6))
    plt.hist(total_profit_market_maker, bins=30, alpha=0.5, label='Market Maker', color='blue')
    plt.hist(total_profit_institutional, bins=30, alpha=0.5, label='Institutional', color='orange')
    plt.hist(total_profit_retail, bins=30, alpha=0.5, label='Retail', color='green')
    plt.title("Trader Profit Distribution (Log Scale)")
    plt.xlabel("Profit")
    plt.ylabel("Frequency (Log Scale)")
    plt.yscale("log")
    plt.legend()
    plt.ticklabel_format(style='plain', axis='x')
    plt.show()

    # No Log
    plt.figure(figsize=(10, 6))
    plt.hist(total_profit_market_maker, bins=30, alpha=0.5, label='Market Maker', color='blue')
    plt.hist(total_profit_institutional, bins=30, alpha=0.5, label='Institutional', color='orange')
    plt.hist(total_profit_retail, bins=30, alpha=0.5, label='Retail', color='green')
    plt.title("Trader Profit Distribution (Log Scale)")
    plt.xlabel("Profit")
    plt.ylabel("Frequency (Log Scale)")
    plt.legend()
    plt.ticklabel_format(style='plain', axis='x')
    plt.show()

    # Plot combined histogram of market and limit order profits for retail traders
    plt.figure(figsize=(10, 6))
    plt.hist(total_market_order_profit_retail, bins=40, alpha=0.5,label='Market Orders', color='blue')
    plt.hist(total_limit_order_profit_retail, bins=40, alpha=0.5, label='Limit Orders',color='red')
    plt.title("Distribution of Market and Limit Order Profits (Retail)")
    plt.xlabel("Profit")
    plt.ylabel("Frequency")
    plt.legend()
    plt.ticklabel_format(style='plain', axis='x')
    plt.show()
