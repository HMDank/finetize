import matplotlib.pyplot as plt
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from scipy.stats import rv_histogram
from tqdm import tqdm
from plots import get_stock_data
import random


def calculate_next_wealth(f, current_wealth):
    df = get_stock_data(symbol, days_away=days_away)
    prices = df['close']
    returns = prices.pct_change().dropna()
    counts, bins, _ = plt.hist(returns, bins=100, color='blue', alpha=0.7)
    histogram_rv = rv_histogram((counts, bins))
    sample = histogram_rv.rvs(size=1)
    return current_wealth * ((1-f) + f * 0.9975 * (1 + max(sample, -100)) * 0.9965)


def calculate_final_return(f, iterations):
    cur_wealth = 1
    for _ in range(iterations):
        cur_wealth = calculate_next_wealth(f, cur_wealth)
    return cur_wealth


def analyze(events_list, amt, prices):
    trading_volume = 0  # Total dollar trading volume
    total_shares_held = 0  # Total number of shares held
    book_size = amt  # Initial book size
    pnl_values = []
    if not events_list:
        return {'Turnover': 0, 'Sharpe': np.nan, 'Margin': np.nan}

    for event in events_list:
        cur_price = event[2]
        if event[0] == 'b':
            total_shares_held += event[3]  # Increment shares held when buying
            trading_volume += cur_price
            amt += cur_price  # Increment trading volume when buying
        elif event[0] == 's':
            total_shares_held -= event[4]  # Decrement shares held when selling
            trading_volume += cur_price  # Increment trading volume when selling
        # Calculate book size as the total value of assets held (price * number of shares)
        final_book_size = total_shares_held * cur_price + amt
        # Assuming the last price reflects the current price
        pnl = (final_book_size - book_size)/book_size
        pnl_values.append(pnl)
        book_size = final_book_size
    average_pnl = np.mean(pnl_values)
    std_dev_pnl = np.std(pnl_values)
    if std_dev_pnl != 0:  # Avoid division by zero
        pnl_ratio = average_pnl / std_dev_pnl
    else:
        pnl_ratio = np.nan  # Handle division by zero
    book_size = final_book_size if final_book_size > 0 else 0
    # Calculate daily turnover
    if book_size != 0:  # Avoid division by zero
        daily_turnover = (trading_volume / book_size) * 100  # Calculate turnover as a percentage
    else:
        daily_turnover = 0

    return {'Turnover': round(daily_turnover, 2), 'Sharpe': round(pnl_ratio, 2), 'Margin': round(average_pnl/trading_volume, 2)}


def decide(rate, choice, period, order):
    if choice == 'Random':
        return random.choice(['buy', 'sell','wait'])
    if choice == 'Momentum':
        if len(rate) < period:
            return 'wait'
        if sum(rate[-period:]) / period > 0:
            return 'buy'
        return 'sell'
    if choice == 'ARIMA':
        if len(rate) > 30:
            model = ARIMA(rate, order=order).fit()
            prediction = model.forecast(steps=1)
            if prediction > 0.001:
                return 'buy'
            if prediction < -0.001:
                return 'sell'
        return 'wait'


def simulate_trading(choice, period, returns, prices, amt, order, verbose=False, plot=True):
    events_list = []
    buy_price = None
    init_amt = amt
    total_shares_held = 0
    buying_price = []
    rate = []

    for date, r in tqdm(returns.items(), total=len(returns)):
        rate.append(r)
        action = decide(rate, choice, period, order)
        if action == 'wait':
            if verbose:
                print(f'Waited with {total_shares_held} shares')

        if action == 'sell' and total_shares_held > 0:
            buy_price = sum(buying_price) / len(buying_price) if len(buying_price) > 0 else buy_price
            buying_price.clear()
            sell_amount = total_shares_held  # $random.randint(1, total_shares_held) if total_shares_held > 1 else 1
            sell_price = prices.loc[date]
            amt += sell_price*sell_amount
            ret = (sell_price - buy_price) / buy_price
            events_list.append(('s', date, sell_price, ret, sell_amount))
            total_shares_held -= sell_amount

            if verbose:
                print(f'Sold {sell_amount} stocks at %s. Current asset: {amt}' % sell_price)
                print(f'Actual Return: %s, {total_shares_held} shares left' % (round(ret * 100, 4)))
                print('=======================================')

        elif action == 'buy' and amt > prices.loc[date]:
            buy_price = prices.loc[date]
            buy_amount = int(amt/buy_price)
            amt -= buy_price*buy_amount
            buying_price.append(buy_price)
            events_list.append(('b', date, buy_price, buy_amount))
            total_shares_held += buy_amount
            if verbose:
                print(f'Bought {buy_amount} stocks at {buy_price}, {amt} remaining')

    if verbose:
        print('Total Amount: $%s' % round(amt, 2))
    stats = analyze(events_list, amt, prices)
    # graph
    if plot:
        fig, ax = plt.subplots(figsize=(10, 4))
        prices.plot(ax=ax)

    # Add vertical lines for each x-axis tick
        y_ticks = ax.get_yticks()

    # Add vertical lines for each x-axis tick
        for tick in y_ticks:
            ax.axhline(tick, color='black', linestyle='-', linewidth=0.8, alpha=0.2)
        buy_index = 0

        for idx, event in enumerate(events_list):
            if event[0] == 'b' and events_list[idx - 1][0] == 's':
                buy_index = idx
                ax.axvline(event[1], color='k', linestyle='--', alpha=0.4)
            if event[0] == 's':
                color = 'green' if event[3] > 0 else ('white' if event[3] == 0 else 'red')
                ax.fill_betweenx(range(int(prices.min()*.5), int(prices.max()*1.5)),
                                 event[1], events_list[buy_index][1],
                                 color=color, alpha=0.2)
                ax.axvline(event[1], color='k', linestyle='--', alpha=0.4)

        tot_return = round(100*((amt + total_shares_held*prices.iloc[-1]) / init_amt - 1), 2)
        tot_return = str(tot_return) + '%'
        ax.set_title("Total Asset: %sM, Total Return: %s\nShares Left: %s" % (round((amt + total_shares_held*prices.iloc[-1])/1000000, 2), tot_return, total_shares_held), fontsize=20)
        ax.set_ylim(prices.min() * 0.95, prices.max() * 1.05)

        return fig, stats

    return None