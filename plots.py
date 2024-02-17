import matplotlib.pyplot as plt

import numpy as np
from vnstock import stock_historical_data, stock_screening_insights
import pandas as pd
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA
from datetime import timedelta, datetime
import seaborn as sns
import matplotlib
matplotlib.use('Agg')
plt.rcParams['font.family'] = "Poppins"

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


def get_stock_data(symbol: str, days_away: int):
    try:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=days_away)

        # Format dates as strings
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        df = stock_historical_data(symbol, start_date_str, end_date_str,
                                   "1D", type='stock', source='TCBS')

        # Check if df is None or empty
        if df is None or df.empty:
            print("Error fetching stock historical data.")
            return ''
        df.set_index('time', inplace=True)
        df.index = pd.to_datetime(df.index)
        return df

    except Exception as e:
        print(f"Error: {e}")
        return None


def generate_data_plot(df):
    prices = df['close']
    returns = prices.pct_change().dropna()

    # Create a figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 5), sharex=True)

    # Plot prices on the first subplot
    color = 'tab:red'
    ax1.set_ylabel('Prices', color=color)
    ax1.plot(prices.index, prices, label='Prices', color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    # Plot returns on the second subplot
    color = 'tab:blue'
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Returns', color=color)
    ax2.plot(returns.index, returns, label='Price Returns', color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    # Add horizontal grey lines for better navigation
    ax2.set_xlabel('Date', color='white')

    x_ticks = ax1.get_xticks()

    # Add vertical lines for each x-axis tick
    for tick in x_ticks:
        ax1.axvline(tick, color='grey', linestyle='--', linewidth=0.8, alpha=0.3)

    x_ticks2 = ax2.get_xticks()

    # Add vertical lines for each x-axis tick
    for tick in x_ticks2:
        ax2.axvline(tick, color='grey', linestyle='--', linewidth=0.8, alpha=0.3)

    y_ticks = ax1.get_yticks()

    # Add vertical lines for each x-axis tick
    for tick in y_ticks:
        ax1.axhline(tick, color='grey', linestyle='--', linewidth=0.8, alpha=0.3)

    y_ticks2 = ax2.get_yticks()

    # Add vertical lines for each x-axis tick
    for tick in y_ticks2:
        ax2.axhline(tick, color='grey', linestyle='--', linewidth=0.8, alpha=0.3)

    return fig


def generate_histogram_plot(df):
    prices = df['close']
    returns = prices.pct_change().dropna()

    # Convert infinity values to NaN
    returns.replace([np.inf, -np.inf], np.nan, inplace=True)

    # Create a figure with a single subplot
    fig, ax = plt.subplots(figsize=(2.75, 4))

    # Plot histogram with a smooth line
    sns.histplot(returns, bins=20, color='blue',
                 alpha=0.7, ax=ax)
    sns.kdeplot(returns, color="red", alpha=0.6)

    ax.set_xlabel('Returns', color='white')
    ax.set_ylabel('Frequency', color='white')
    ax.set_title('Histogram of Returns')

    return fig


def generate_acf_pacf_plots(df):
    prices = df['close']
    returns = prices.pct_change().dropna()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 5))

    plot_acf(returns, lags=min(int(len(df)*0.2), 20), ax=ax1)
    ax1.set_title('Autocorrelation Function (ACF)')

    plot_pacf(returns, lags=min(int(len(df)*0.2), 20), ax=ax2)
    ax2.set_title('Partial Autocorrelation Function (PACF)')

    return fig


def generate_scatter_plot(df):
    # Extract prices and returns
    prices = df['close']
    returns = prices.pct_change().dropna()

    # Extract market returns
    market_returns = df['market_returns'].pct_change().dropna()

    # Create scatter plot
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.scatter(market_returns, returns, alpha=0.5)
    ax.set_title('Scatter Plot of Returns vs Market Returns')
    ax.set_xlabel('Market Returns')
    ax.set_ylabel('Returns')
    ax.grid(True)

    return fig


def generate_metrics(symbol, metric_list):
    params = {
            "exchangeName": "HOSE,HNX",
            }
    df = stock_screening_insights(params, size=1700)
    df = df[df['ticker'] == symbol][metric_list]
    return df.iloc[0].to_dict()
