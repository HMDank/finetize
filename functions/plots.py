import streamlit as st
import numpy as np
import os
import scipy.stats as stats
from vnstock import stock_historical_data, stock_screening_insights, fr_trade_heatmap, financial_ratio, company_profile
import pandas as pd
from statsmodels.graphics.tsaplots import acf, pacf
from datetime import timedelta, datetime
import plotly.express as px
import plotly.graph_objects as go
from langchain_experimental.agents import create_pandas_dataframe_agent
from dotenv import load_dotenv, find_dotenv
from langchain_community.llms.openai import OpenAI

market_df = fr_trade_heatmap(symbol='VNINDEX', report_type='FrBuyVal').T


def get_stock_data(symbol: str, days_away: int):
    end_date = datetime.today()
    start_date = end_date - timedelta(days=days_away)

    # Format dates as strings
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    df = stock_historical_data(symbol, start_date_str, end_date_str,
                                "1D", type='stock', source='TCBS') if len(symbol) == 3 else stock_historical_data(symbol, start_date_str, end_date_str,
                                "1D", type='index', source='TCBS')


    # Check if df is None or empty
    if df is None or df.empty:
        print("Error fetching stock historical data.")
        return ''
    df.set_index('time', inplace=True)
    df.index = pd.to_datetime(df.index)
    return df.dropna()


def generate_data_plot(df, data_selection):
    prices = df['close'].dropna()
    returns = prices.pct_change().dropna()
    if data_selection == 'Candlestick':
        fig = go.Figure(data=[go.Candlestick(x=df.index.values,
                              open=df['open'],
                              high=df['high'],
                              low=df['low'],
                              close=df['close'])],)
        fig.update_layout(
            plot_bgcolor='#262730',
            xaxis_rangeslider_visible=False,
            height=500,
            margin=dict(t=20, b=20, l=20, r=20),
            paper_bgcolor='#262730'
            )
        fig.update_xaxes(showline=True,
                         linewidth=1,
                         linecolor='white',
                         mirror=True)

        fig.update_yaxes(showline=True,
                         linewidth=1,
                         linecolor='white',
                         mirror=True)
        return fig
    data = prices if data_selection == 'Price' else returns
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data.index.values,
        y=data.values,
        showlegend=False,
        mode='lines+markers',
    ))
    fig.update_layout(
        xaxis_rangeslider_visible=False,
        plot_bgcolor='#262730',
        paper_bgcolor='#262730',
        height=500,
        margin=dict(t=20, b=20, l=20, r=20),
        )
    fig.update_xaxes(showline=True,
                     linewidth=1,
                     linecolor='white',
                     mirror=True)

    fig.update_yaxes(showline=True,
                     linewidth=1,
                     linecolor='white',
                     mirror=True)

    return fig


def generate_histogram_plot(df):
    prices = df['close'].dropna()
    returns = prices.pct_change().dropna()

    kde = stats.gaussian_kde(returns)
    x_vals = np.linspace(returns.min(), returns.max(), 1000)
    kde_vals = kde.evaluate(x_vals)

    histogram = go.Histogram(x=returns, histnorm='probability density', name='Returns', showlegend=False, marker=dict(color='#1F77B4', line=dict(color='white', width=1)))
    kde_line = go.Scatter(x=x_vals, y=kde_vals, mode='lines', name='KDE', line=dict(color = 'white'), showlegend=False)
    fig = go.Figure(data=[histogram, kde_line])

    fig.update_layout(
        xaxis_title='Returns',
        yaxis_title='Probability Density',
        plot_bgcolor='#262730',
        paper_bgcolor='#262730',
        margin=dict(t=10, b=10, l=10, r=10),
        height=680,
    )
    fig.update_xaxes(showline=True,
                     linewidth=1,
                     linecolor='white',
                     mirror=True)

    fig.update_yaxes(showline=True,
                     linewidth=1,
                     linecolor='white',
                     mirror=True)

    return fig


def generate_acf_plots(series, plot_pacf=False):
    corr_array = pacf(series.dropna(), alpha=0.05) if plot_pacf else acf(series.dropna(), alpha=0.05)
    lower_y = corr_array[1][:,0] - corr_array[0]
    upper_y = corr_array[1][:,1] - corr_array[0]

    fig = go.Figure()
    [fig.add_scatter(x=(x,x), y=(0,corr_array[0][x]), mode='lines', line_color='#3f3f3f')
        for x in range(len(corr_array[0]))]
    fig.add_scatter(x=np.arange(len(corr_array[0])), y=corr_array[0], mode= 'markers', marker_color='#1F77B4',
                    marker_size=12)
    fig.add_scatter(x=np.arange(len(corr_array[0])), y=upper_y, mode='lines', line_color='rgba(255,255,255,0)')
    fig.add_scatter(x=np.arange(len(corr_array[0])), y=lower_y, mode='lines', fillcolor='rgba(32, 146, 230,0.2)',
                    fill='tonexty', line_color='rgba(255,255,255,0)')
    fig.update_traces(showlegend=False)
    fig.update_xaxes(range=[-1, 20], showline=True,
                     linewidth=1,
                     linecolor='white',
                     mirror=True)
    fig.update_yaxes(range=[-0.5, 0.5], showline=True,
                     linewidth=1,
                     linecolor='white',
                     mirror=True)
    fig.update_yaxes(zerolinecolor='#FFFFFF')
    fig.update_layout(height=350, width=700, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor='#262730', paper_bgcolor='#262730')
    return fig


def generate_scatter_plot(df, days_away):
    # Extract prices and returns
    prices = df['close'].dropna()
    returns = prices.pct_change().dropna()
    market_prices = get_stock_data('VNINDEX', days_away)
    market_prices = market_prices['close'].dropna()
    market_returns = market_prices.pct_change().dropna()

# Plot the scatter plot with marginal histograms
    fig = px.scatter(x=returns, y=market_returns,
                     marginal_x="histogram", marginal_y="histogram",
                     trendline="ols", trendline_color_override='white',
                     labels={'y': 'Market Returns', 'x': 'Portfolio Returns'},
                     color_discrete_sequence=['#1F77B4'])
    fig.update_layout(
        plot_bgcolor='#262730',
        paper_bgcolor='#262730'
        )
    fig.update_xaxes(showline=True,
                     linewidth=1,
                     linecolor='white',
                     mirror=True)

    fig.update_yaxes(showline=True,
                     linewidth=1,
                     linecolor='white',
                     mirror=True)

    return fig


def generate_metrics(symbol):
    try:
        df = financial_ratio(symbol, 'yearly')
        return df.drop('ticker').to_dict()
    except Exception:
        st.error("Can't generate financial statistics")


def generate_ai_analysis(df, key):
    llm2 = OpenAI(temperature=0, openai_api_key=key)
    pandas_agent = create_pandas_dataframe_agent(llm2, df, verbose=True)
    trends = pandas_agent.run(f"This is a data of the price of a stock symbol. Tell me the direction of the 'close' column over time and a pattern if it exists")
    return trends


def show_full_name(symbol):
    profile = company_profile(symbol).T.iloc[1][0]
    return profile