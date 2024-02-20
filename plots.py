import matplotlib.pyplot as plt
import streamlit as st
import numpy as np
import os
from vnstock import stock_historical_data, stock_screening_insights, fr_trade_heatmap
import pandas as pd
from statsmodels.graphics.tsaplots import acf, pacf
from statsmodels.tsa.arima.model import ARIMA
from datetime import timedelta, datetime
import seaborn as sns
import matplotlib
from matplotlib import font_manager as fm
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# from apikey import apikey
# from langchain.llms import OpenAI
# from langchain_experimental.agents import create_pandas_dataframe_agent
# from dotenv import load_dotenv, find_dotenv


matplotlib.use('Agg')
prop = fm.FontProperties(fname='POPPINS-REGULAR.OTF')
plt.rcParams['font.family'] = prop.get_name()
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

market_df = fr_trade_heatmap(symbol='VNINDEX', report_type='FrBuyVal').T


def get_stock_data(symbol: str, days_away: int):
    try:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=days_away)

        # Format dates as strings
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')

        df = stock_historical_data(symbol, start_date_str, end_date_str,
                                   "1D", type='stock', source='TCBS') if len(symbol) == 3 else stock_historical_data(symbol, start_date_str, end_date_str,
                                   "1D", type='index', source='TCBS').drop_duplicates()


        # Check if df is None or empty
        if df is None or df.empty:
            print("Error fetching stock historical data.")
            return ''
        df.set_index('time', inplace=True)
        df.index = pd.to_datetime(df.index)
        return df.drop_duplicates()

    except Exception as e:
        print(f"Get Stock Data Error: {e}")
        return None


def generate(df, data_selection):
    st.line_chart(df, y =[user_question_variable])
    summary_statistics = pandas_agent.run(f"Give me a summary of the statistics of {user_question_variable}")
    st.write(summary_statistics)
    normality = pandas_agent.run(f"Check for normality or specific distribution shapes of {user_question_variable}")
    st.write(normality)
    outliers = pandas_agent.run(f"Assess the presence of outliers of {user_question_variable}")
    st.write(outliers)
    trends = pandas_agent.run(f"Analyse trends, seasonality, and cyclic patterns of {user_question_variable}")
    st.write(trends)
    missing_values = pandas_agent.run(f"Determine the extent of missing values of {user_question_variable}")
    st.write(missing_values)


def generate_data_plot(df, data_selection):
    prices = df['close'].dropna()
    returns = prices.pct_change().dropna()
    if data_selection == 'Candle':
        fig = go.Figure(data=[go.Candlestick(x=df.index.values,
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'])])
        fig.update_layout(
            plot_bgcolor='#262730',
            # paper_bgcolor='#262730'
            )
        return fig
    data = prices if data_selection == 'Price' else returns
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index.values,
        y=data.values,
        showlegend=False
    ))
    fig.update_layout(
        plot_bgcolor='#262730',
        # paper_bgcolor='#262730'
        )

    return fig

    # Create a figure with two subplots
    # fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 5), sharex=True)

    # # Plot prices on the first subplot
    # color = 'white'
    # ax1.set_ylabel('Prices', color=color)
    # ax1.plot(prices.index, prices, label='Prices', color=color)
    # ax1.tick_params(axis='y', labelcolor=color)

    # # Plot returns on the second subplot
    # color = 'tab:blue'
    # ax2.set_xlabel('Date')
    # ax2.set_ylabel('Returns', color=color)
    # ax2.plot(returns.index, returns, label='Price Returns', color=color)
    # ax2.tick_params(axis='y', labelcolor=color)
    # # Add horizontal grey lines for better navigation
    # ax2.set_xlabel('Date', color='white')

    # x_ticks = ax1.get_xticks()

    # # Add vertical lines for each x-axis tick
    # for tick in x_ticks:
    #     ax1.axvline(tick, color='grey', linestyle='--', linewidth=0.8, alpha=0.3)

    # x_ticks2 = ax2.get_xticks()

    # # Add vertical lines for each x-axis tick
    # for tick in x_ticks2:
    #     ax2.axvline(tick, color='grey', linestyle='--', linewidth=0.8, alpha=0.3)

    # y_ticks = ax1.get_yticks()

    # # Add vertical lines for each x-axis tick
    # for tick in y_ticks:
    #     ax1.axhline(tick, color='grey', linestyle='--', linewidth=0.8, alpha=0.3)

    # y_ticks2 = ax2.get_yticks()

    # # Add vertical lines for each x-axis tick
    # for tick in y_ticks2:
    #     ax2.axhline(tick, color='grey', linestyle='--', linewidth=0.8, alpha=0.3)

    # return fig


def generate_histogram_plot(df):
    prices = df['close']
    returns = prices.pct_change().dropna()

    # Convert infinity values to NaN
    returns.replace([np.inf, -np.inf], np.nan, inplace=True)

    # Create a figure with a single subplot
    fig, ax = plt.subplots(figsize=(2.75, 4))

    # Plot histogram with a smooth line
    sns.histplot(returns, bins=20, color='#1F77B4',
                 alpha=0.7, ax=ax)
    sns.kdeplot(returns, color="white", alpha=0.7)

    ax.set_xlabel('Returns', color='white')
    ax.set_ylabel('Frequency', color='white')
    ax.set_title('Histogram of Returns')

    return fig


def generate_acf_pacf_plots(df):
    prices = df['close']
    returns = prices.pct_change().dropna()

    def create_corr_plot(series, plot_pacf=False, ratio=(4, 5)):
        corr_array = pacf(series.dropna(), alpha=0.05) if plot_pacf else acf(series.dropna(), alpha=0.05)
        lower_y = corr_array[1][:,0] - corr_array[0]
        upper_y = corr_array[1][:,1] - corr_array[0]

        fig = go.Figure()
        [fig.add_scatter(x=(x,x), y=(0,corr_array[0][x]), mode='lines', line_color='#3f3f3f')
         for x in range(len(corr_array[0]))]
        fig.add_scatter(x=np.arange(len(corr_array[0])), y=corr_array[0], mode= 'markers', marker_color='#1f77b4',
                        marker_size=12)
        fig.add_scatter(x=np.arange(len(corr_array[0])), y=upper_y, mode='lines', line_color='rgba(255,255,255,0)')
        fig.add_scatter(x=np.arange(len(corr_array[0])), y=lower_y, mode='lines', fillcolor='rgba(32, 146, 230,0.3)',
                        fill='tonexty', line_color='rgba(255,255,255,0)')
        fig.update_traces(showlegend=False)
        fig.update_xaxes(range=[-1, 20])
        fig.update_yaxes(range=[-0.5, 0.5])
        fig.update_yaxes(zerolinecolor='#000000')

        title = 'Partial Autocorrelation (PACF)' if plot_pacf else 'Autocorrelation (ACF)'
        fig.update_layout(height=ratio[0]*100, width=ratio[1]*100, margin=dict(l=30, r=30, t=30, b=30))
        return fig

    acf_fig = create_corr_plot(returns)
    pacf_fig = create_corr_plot(returns, plot_pacf=True)

    # Create a subplot with two rows and one column
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True)

    # Add ACF plot to the first row
    for trace in acf_fig.data:
        fig.add_trace(trace, row=1, col=1)
    fig.update_xaxes(title_text="Lags")

    # Add PACF plot to the second row
    for trace in pacf_fig.data:
        fig.add_trace(trace, row=1, col=2)
    fig.update_xaxes(title_text="Lags")

    # Update layout
    fig.update_layout(acf_fig.layout)
    fig.update_layout(
        plot_bgcolor='#262730',
        #  paper_bgcolor='#262730'
        )

    return fig


    # fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 5))

    # plot_acf(returns, lags=min(int(len(df)*0.2), 20), ax=ax1)
    # ax1.set_title('Autocorrelation Function (ACF)')

    # plot_pacf(returns, lags=min(int(len(df)*0.2), 20), ax=ax2)
    # ax2.set_title('Partial Autocorrelation Function (PACF)')

    # return fig


def generate_scatter_plot(df, days_away):
    # Extract prices and returns
    prices = df['close']
    returns = prices.pct_change().dropna()
    market_prices = get_stock_data('VNINDEX', days_away).drop_duplicates()
    market_prices = market_prices['close']
    market_returns = market_prices.pct_change().dropna()

# Plot the scatter plot with marginal histograms
    fig = px.scatter(x=returns, y=market_returns,
                     marginal_x="histogram", marginal_y="histogram",
                     trendline="ols", trendline_color_override='white',
                     labels={'y': 'Market Returns', 'x': 'Portfolio Returns'},
                     color_discrete_sequence=['#1F77B4'])
    fig.update_layout(
        plot_bgcolor='#262730',
        #  paper_bgcolor='#262730'
        )

    return fig


def generate_metrics(symbol, metric_list):
    try:
        params = {
                "exchangeName": "HOSE,HNX",
                }
        df = stock_screening_insights(params, size=1700)
        df = df[df['ticker'] == symbol.upper()][metric_list]
        return df.iloc[0].to_dict()
    except Exception:
        st.error("Can't generate financial metrics")


# def generate_ai_analysis(df):
#     os.environ['OPENAI_API_KEY'] = apikey
#     load_dotenv(find_dotenv())
#     llm = OpenAI(temperature=0)
#     pandas_agent = create_pandas_dataframe_agent(llm, df, verbose=True)
