import matplotlib.pyplot as plt
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from scipy.stats import rv_histogram
from tqdm import tqdm
from plots import fetch_data
import random


def calculate_next_wealth(f, current_wealth):
    df = fetch_data(symbol, days_away=days_away)
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
    for event in events_list:
        cur_price = event[2]
        if event[0] == 'b':
            total_shares_held += event[3]  # Increment shares held when buying
            trading_volume += cur_price  # Increment trading volume when buying
        elif event[0] == 's':
            total_shares_held -= event[4]  # Decrement shares held when selling
            trading_volume += cur_price  # Increment trading volume when selling

        # Calculate book size as the total value of assets held (price * number of shares)
        final_book_size = total_shares_held * cur_price
        # Assuming the last price reflects the current price
        pnl = final_book_size - book_size
        pnl_values.append(pnl)

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

    return {'Turnover': round(daily_turnover, 2), 'Sharpe': round(pnl_ratio, 2)}


def decide(rate, choice):
    if choice == 'Random':
        return random.choice(['buy', 'sell','wait'])
    if choice == 'If Last Positive, Buy':
        if rate > 0:
            return 'buy'
        if rate < 0:
            return 'sell'
        return 'wait'


def simulate_random_buying(choice, returns, prices, amt, order, thresh, verbose=False, plot=True):
    if isinstance(order, float):
        thresh = None

    events_list = []
    buy_price = None
    init_amt = amt
    total_shares_held = 0
    buying_price = []
    last_rate = 0

    for date, r in tqdm(returns.items(), total=len(returns)):
    # Randomly decide whether to buy or sell
        action = decide(last_rate, choice)
        if action == 'wait':
            if verbose:
                print(f'Waited with {total_shares_held} shares')

        if action == 'sell' and total_shares_held > 0:
            buy_price = sum(buying_price) / len(buying_price) if len(buying_price) > 0 else buy_price
            buying_price.clear()
            sell_amount = 1#$random.randint(1, total_shares_held) if total_shares_held > 1 else 1
            sell_price = prices.loc[date]
            ret = (sell_price - buy_price) / buy_price
            amt *= (1 + ret)
            events_list.append(('s', date, sell_price, ret, sell_amount))
            total_shares_held -= sell_amount

            if verbose:
                print(f'Sold {sell_amount} stocks at %s' % sell_price)
                print(f'Actual Return: %s, {total_shares_held} shares left' % (round(ret * 100, 4)))
                print('=======================================')

        elif action == 'buy':
            buy_amount = 1
            buy_price = prices.loc[date]
            buying_price.append(buy_price)
            events_list.append(('b', date, buy_price, buy_amount))
            total_shares_held += buy_amount
            if verbose:
                print(f'Bought {buy_amount} stocks at %s' % buy_price)
        last_rate = r

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

        tot_return = round(100*(amt / init_amt - 1), 2)
        tot_return = str(tot_return) + '%'
        ax.set_title("Price Data\nThresh=%s\nTotal Amt: $%s\nTotal Return: %s\nShares Left: %s"%(thresh, round(amt,2), tot_return, total_shares_held), fontsize=20)
        ax.set_ylim(prices.min() * 0.95, prices.max() * 1.05)

        return fig, stats

    return None

    # go through dates
    # for date, r in tqdm(returns.iloc[14:].items(), total=len(returns.iloc[14:])):
    #     # if you're currently holding the stock, sell it
    #     action = random.choice(['buy', 'sell'])
    #     if action == 'sell' and curr_holding:
    #         sell_price = prices.loc[date]
    #         curr_holding = False
    #         ret = (sell_price - buy_price) / buy_price
    #         amt *= (1+ret)
    #         events_list.append(('s', date, sell_price, ret))

    #         if verbose:
    #             print('Sold at $%s'%sell_price)
    #             print('Actual Return: %s'%(round(ret, 4)))
    #             print('=======================================')
    #         continue

    #     # get data til just before current date
    #     curr_data = returns[:date]

    #     if isinstance(order, tuple):
    #         try:
    #             # fit model
    #             model = ARIMA(curr_data, order=order).fit(maxiter=200)

    #             # get forecast
    #             pred = model.forecast()[0][0]

    #         except Exception:
    #             pred = thresh - 1

    #     # if you predict a high enough return and not holding, buy stock
    #     elif action == 'buy':
    #         if (not curr_holding) and \
    #            ((isinstance(order, float) and np.random.random() < order)
    #            or (isinstance(order, tuple) and pred > thresh)):

    #             curr_holding = True
    #             buy_price = prices.loc[date]
    #             events_list.append(('b', date, buy_price))
    #             if verbose:
    #                 print('Bought at $%s' % buy_price)