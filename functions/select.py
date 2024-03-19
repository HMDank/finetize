import streamlit as st
import numpy as np
import os
import scipy.stats as stats
from vnstock import stock_historical_data, stock_screening_insights, fr_trade_heatmap, financial_ratio
import pandas as pd

fundamental_selections = {
    'PE < 20': {'pe': (0, 20)},
    'PB > 1': {'pb': (1, 30)},
    'ROE > 25': {'roe':(25, 100)}
}

technical_selections = {
    'RSI14 < 30': {'rsi14': (0, 30)},
}


def filter_stock(params_list):
    default_params = {
        'exchangeName': 'HOSE,HNX',
        'marketCap': (1000, 99999999999),
    }
    extra_params = {}
    for selection in params_list:
        for item in fundamental_selections.items():
            if selection == item[0]:
                extra_params.update(fundamental_selections.get(selection))
        for item in technical_selections.items():
            if selection == item[0]:
                extra_params.update(technical_selections.get(selection))
    final_params = {}
    final_params.update(default_params)
    final_params.update(extra_params)
    df = stock_screening_insights(final_params, size=1700, drop_lang='vi')
    if df.empty:
        return df
    sorted_df = df.sort_values(by=['industryName.en', 'marketCap'], ascending=[True, False])
    top_stock_market_cap = sorted_df.groupby('industryName.en')['marketCap'].first().reset_index()
    top_stock_market_cap = top_stock_market_cap.rename(columns={'marketCap': 'topStockMarketCap'})
    top_stock_market_cap = top_stock_market_cap.sort_values(by='topStockMarketCap', ascending=False)
    result_df = pd.DataFrame(columns=df.columns)
    for industry in top_stock_market_cap['industryName.en']:
        industry_symbols = sorted_df[sorted_df['industryName.en'] == industry]
        result_df = pd.concat([result_df, industry_symbols], ignore_index=True)

    def highlight_industry_row(row):
        return ['background-color: #1a1c24' if row.name % 2 == 0 else '' for _ in row]
    new_df = result_df.drop(columns=['companyName'])
    formatted_df = new_df.style.apply(highlight_industry_row, axis=1)
    numeric_columns = new_df.select_dtypes(include=['float64', 'int64']).columns
    formatted_df = formatted_df.format({col: '{:.1f}' for col in numeric_columns})

    return formatted_df


def reorder_stocks(df):
    sorted_df = df.sort_values(by=['industryName.en', 'marketCap'], ascending=[True, False])
    top_stock_market_cap = sorted_df.groupby('industryName.en')['marketCap'].first().reset_index()
    top_stock_market_cap = top_stock_market_cap.rename(columns={'marketCap': 'topStockMarketCap'})
    top_stock_market_cap = top_stock_market_cap.sort_values(by='topStockMarketCap', ascending=False)
    result_df = pd.DataFrame(columns=df.columns)
    for industry in top_stock_market_cap['industryName.en']:
        industry_symbols = sorted_df[sorted_df['industryName.en'] == industry]
        result_df = pd.concat([result_df, industry_symbols], ignore_index=True)
    return result_df


def calculate_market():
    params = {
        'exchangeName': 'HOSE,HNX',
    }
    df = stock_screening_insights(params, size=1700, drop_lang='vi')
    sorted_df = df.sort_values(by=['industryName.en', 'marketCap'], ascending=[True, False])
    top_stock_market_cap = sorted_df.groupby('industryName.en')['marketCap'].first().reset_index()
    top_stock_market_cap = top_stock_market_cap.rename(columns={'marketCap': 'topStockMarketCap'})
    top_stock_market_cap = top_stock_market_cap.sort_values(by='topStockMarketCap', ascending=False)
    result_df = pd.DataFrame(columns=df.columns)
    for industry in top_stock_market_cap['industryName.en']:
        industry_symbols = sorted_df[sorted_df['industryName.en'] == industry]
        result_df = pd.concat([result_df, industry_symbols.dropna(axis=1, how='all')], ignore_index=True)
    total_market_cap_by_industry = result_df.groupby('industryName.en')['marketCap'].sum()
    result_df['industryMarketCapWeight'] = result_df.groupby('industryName.en')['marketCap'].transform(lambda x: x / x.sum())
    result_df['weightedPE'] = result_df['pe'] * result_df['industryMarketCapWeight']
    result_df['weightedPB'] = result_df['pb'] * result_df['industryMarketCapWeight']
    result_df['weightedROE'] = result_df['roe'] * result_df['industryMarketCapWeight']
    total_weighted_PE = result_df.groupby('industryName.en')['weightedPE'].sum()
    total_weighted_PB = result_df.groupby('industryName.en')['weightedPB'].sum()
    total_weighted_ROE = result_df.groupby('industryName.en')['weightedROE'].sum()

    industry_ratios_df = pd.DataFrame({
        'Industry_PE_ratio': total_weighted_PE,
        'Industry_PB_ratio': total_weighted_PB,
        'Industry_ROE_ratio': total_weighted_ROE,
        'Industry_Market_Cap': total_market_cap_by_industry
    })
    return industry_ratios_df


def compare_stocks(symbol_list):
    params = {
        'exchangeName': 'HOSE,HNX',
    }
    df = stock_screening_insights(params, size=1700, drop_lang='vi')
    df = df[df['ticker'].isin(symbol_list)].loc[:, ['ticker', 'marketCap', 'pe', 'pb', 'roe', 'industryName.en', 'revenueGrowth1Year', ]]
    df = reorder_stocks(df)
    market_df = calculate_market()
    new_rows = []
    current_industry = None
    for index, row in df.iterrows():
        if row['industryName.en'] != current_industry:
            # If industry changes, get the corresponding PE and PB values from market_df
            current_industry = row['industryName.en']
            industry_stats = market_df.loc[current_industry]
            new_row = {
                'ticker': current_industry,
                'marketCap': industry_stats['Industry_Market_Cap'],
                'pe': industry_stats['Industry_PE_ratio'],
                'pb': industry_stats['Industry_PB_ratio'],
                'roe': industry_stats['Industry_ROE_ratio'],
            }
            new_rows.append(new_row)

        # Append the original row (converted to a dictionary)
        new_rows.append(row.to_dict())

# Create a new DataFrame with the updated rows
    new_df = pd.DataFrame(new_rows, columns=df.columns).drop(columns=['industryName.en'])

    def highlight_industry_row(row):
        if len(row['ticker']) > 3:
            return ['background-color: #262730'] * len(row)
        else:
            return [''] * len(row)

    # Apply the function to the DataFrame
    styled_df = new_df.style.apply(highlight_industry_row, axis=1)
    final_df = styled_df.format({
        'marketCap': '{:.2f}',
        'pe': '{:.2f}',
        'pb': '{:.2f}',
        'roe': '{:.2f}',
        'revenueGrowth1Year': '{:.2f}'
    })
    return final_df
