import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from scipy.stats import rv_histogram
from tqdm import tqdm
from functions.plots import get_stock_data, stock_screening_insights
from vnstock import general_rating
import random
import matplotlib
from statsmodels.tools.sm_exceptions import ConvergenceWarning
import warnings
warnings.filterwarnings('ignore', category=ConvergenceWarning)

matplotlib.use('Agg')
custom_dark_colors = {
    'figure.facecolor': '#262730',
    'axes.facecolor': '#262730',     # Axes background color
    'axes.edgecolor': '#FFFFFF',     # Axes edge color
    'text.color': '#FFFFFF',         # Text color
    'xtick.color': '#FFFFFF',        # X-axis tick color
    'ytick.color': '#FFFFFF',        # Y-axis tick color
    'grid.color': '#262730',         # Grid color
    'grid.alpha': 1               # Grid transparency
}
plt.rcParams.update(custom_dark_colors)


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


def calculate_position_sizing(symbol, prices):
    returns = prices.pct_change().dropna()
    returns = returns[~returns.index.duplicated(keep='first')]
    p = (returns > 0).sum()
    p /= len(returns)

    beta = general_rating(symbol).T.loc['beta', 0]
    expected_market_return = 0.15
    bank_rate = 0.045
    CAPM_return = (bank_rate + beta*(expected_market_return - bank_rate)) * 100
    return (CAPM_return*p + (1-p))/CAPM_return


def analyze(events_list, amt, total_asset):
    trading_volume = 0  # Total dollar trading volume
    total_shares_held = 0  # Total number of shares held
    book_size = amt  # Initial book size
    pnl_values = []
    if not events_list:
        return {'Turnover': 0, 'Sharpe': np.nan, 'Margin': np.nan, 'Return': 0}

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
        pnl_ratio = np.nan
    book_size = final_book_size if final_book_size > 0 else 0
    # Calculate daily turnover
    if book_size != 0:
        daily_turnover = (trading_volume / book_size) * 100
    else:
        daily_turnover = 0
    return {'Turnover': round(daily_turnover, 2), 'Sharpe': round(pnl_ratio, 2), 'Margin': round(average_pnl/trading_volume, 2), 'Return': total_asset/100 - 1}


def simulate_trading(choice, period, symbol, days_away, amt, order, position_sizing, verbose=False, plot=True):
    def decide(rate, choice, period, order):
        if choice == 'Random':
            return random.choice(['buy', 'sell', 'wait'])
        if choice == 'Momentum':
            if len(rate) < period:
                return 'wait'
            if sum(rate[-period:]) / period > 0:
                return 'buy'
            return 'sell'
        if choice == 'Mean Reversion':
            if len(rate) < period + 1:
                return 'wait'
            avg_rate = np.mean(rate[-(period+1):-1])
            if avg_rate > rate[-1]:
                return 'buy'
            return 'sell'
        if choice == 'ARIMA':
            if len(rate) > 30:
                model = ARIMA(rate, order=order).fit()
                prediction = model.forecast(steps=1)
                if prediction > 0.002:
                    return 'buy'
                if prediction < -0.002:
                    return 'sell'
            return 'wait'
    prices = get_stock_data(symbol, days_away)['close']
    returns = prices.pct_change().dropna()
    returns = returns[~returns.index.duplicated(keep='first')]

    events_list = []
    buy_price = None
    init_amt = amt
    total_shares_held = 0
    buying_price = []
    rate = []
    last_buy = 0
    last_sell = 0
    for date, r in tqdm(returns.items(), total=len(returns)):
        action = decide(rate, choice, period, order)
        if last_buy > 0:
            last_buy -= 1
            action = 'wait'
        if last_sell > 0:
            last_sell -= 1
            action = 'wait'
        current_price = prices.loc[date]
        if isinstance(current_price, pd.Series):
            current_price = prices.loc[date].iloc[0]
        rate.append(r)
        if action == 'wait':
            if verbose:
                print(f'Waited with {total_shares_held} shares')

        if action == 'sell' and total_shares_held > 0:
            buy_price = sum(buying_price) / len(buying_price) if len(buying_price) > 0 else buy_price
            buying_price.clear()
            sell_amount = total_shares_held  # $random.randint(1, total_shares_held) if total_shares_held > 1 else 1
            sell_price = current_price
            amt += sell_price*sell_amount*0.9965
            ret = (sell_price - buy_price) / buy_price
            events_list.append(('s', date, sell_price, ret, sell_amount, amt))
            total_shares_held -= sell_amount
            last_sell = 2

            if verbose:
                print(f'Sold {sell_amount} stocks at %s. Current asset: {amt}' % sell_price)
                print(f'Actual Return: %s, {total_shares_held} shares left' % (round(ret * 100, 4)))
                print('=======================================')

        elif action == 'buy' and amt*position_sizing > current_price:
            buy_price = current_price
            buy_amount = int(amt*position_sizing/buy_price)
            amt -= buy_price*buy_amount
            buying_price.append(buy_price)
            events_list.append(('b', date, buy_price, buy_amount))
            total_shares_held += buy_amount
            last_buy = 2
            if verbose:
                print(f'Bought {buy_amount} stocks at {buy_price}, {amt} remaining')

    if verbose:
        print('Total Amount: $%s' % round(amt, 2))

    total_return = round(100*((amt + total_shares_held*prices.iloc[-1]) / init_amt - 1), 2)
    total_return = str(total_return) + '%'
    total_asset = round((amt + total_shares_held*prices.iloc[-1])/1000000, 2)
    stats = analyze(events_list, amt, total_asset)
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
        buy_amounts = [event[3] for event in events_list]
        date_proportion_dict = {}
        for event in events_list:
            date = event[1]
            buy_amount = event[3]
            proportion = buy_amount / (max(buy_amounts)*1)
            date_proportion_dict[date] = proportion

        for idx, event in enumerate(events_list):
            if event[0] == 'b':
                if idx == 0:
                    buy_index = idx
                    ax.axvline(event[1], color='k', linestyle='--', alpha=0.4)
                    continue
                if events_list[idx - 1][0] == 's':
                    buy_index = idx
                    ax.axvline(event[1], color='k', linestyle='--', alpha=0.4)
                else:
                    proportion = date_proportion_dict[event[1]]
                    ax.axvline(event[1], color='white', linestyle='-', alpha=0.15, ymin=0, ymax=proportion)

            if event[0] == 's':
                color = 'green' if event[3] > 0 else ('yellow' if event[3] == 0 else 'red')
                ax.fill_betweenx(range(int(prices.min()*.5), int(prices.max()*1.5)),
                                 event[1], events_list[buy_index][1],
                                 color=color, alpha=0.2)
                ax.axvline(event[1], color='k', linestyle='--', alpha=0.4)
        ax.set_title("%s(%s)\nTotal Asset: %sM, Total Return: %s\nShares Left: %s" %(choice, period if period is not None else order, total_asset, total_return, total_shares_held), fontsize=20)
        ax.set_ylim(prices.min() * 0.95, prices.max() * 1.05)

        return fig, stats

    return stats


def optimize_choice(choice, symbol, days_away, position_sizing):
    all_returns = {}
    for period in range(1, 31, 1):
        stats = simulate_trading(choice, period, symbol, days_away, 100_000_000, 0, position_sizing, verbose=False, plot=False)
        all_returns[period] = stats['Return']
    best_period = max(all_returns, key=all_returns.get)
    return best_period


def test_market(choice, period, days_away):
    results = {}
    params = {
                "exchangeName": "HOSE,HNX",
                'marketCap': (1000, 99999999999),
                }
    tickers = stock_screening_insights(params, size=1700)['ticker']
    for ticker in tickers:
        try:
            stats = simulate_trading(choice, period, ticker, days_away, 100_000_000, 0, 1, verbose=False, plot=False)
            results[ticker] = stats['Return']
        except Exception:
            results[ticker] = None
    return results


def split_results(results):
    wins = {}
    losses = {}

    for key, value in results.items():
        if not value:
            continue
        if value > 0:
            wins[key] = value
        else:
            losses[key] = value

    return wins, losses


def simulate_buy_hold(symbol, days_away):
    prices = get_stock_data(symbol, days_away)['close']
    return prices.iloc[-1] / prices.iloc[0] - 1
