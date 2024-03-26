import streamlit as st
from vnstock import stock_screening_insights
from functions.plots import get_stock_data
from functions.select import fundamental_selections, technical_selections, filter_stock, compare_stocks
st.set_page_config(layout="wide",
                   page_title='Stock Filter')


@st.cache_data()
def get_df():
    default_params = {
        'exchangeName': 'HOSE,HNX',
        'marketCap': (100, 99999999999),
    }
    df = stock_screening_insights(default_params, size=1700, drop_lang='vi')
    return df


@st.cache_data()
def get_market_info(df):
    total_cap = df.loc[:, ['marketCap']].sum()
    total_market_cap = int(total_cap.iloc[0])
    tickers = df['ticker'].tolist()
    industries = df['industryName.en'].unique().tolist()
    industries.sort()
    return tickers, industries, total_market_cap


@st.cache_data(show_spinner='Loading Comparison Table')
def generate_dataframe(df, symbol_list, total_market_cap):
    st.dataframe(
        compare_stocks(df, symbol_list),
        column_config={
            "ticker": st.column_config.TextColumn(
                "Symbol",
            ),
            "price_change": st.column_config.LineChartColumn(
                "Price Change",
                width="small",
                help="Change in price every minute in the last 6 Months",
                y_min=-1,
                y_max=1
            ),
            "marketCap": st.column_config.ProgressColumn(
                "Market Cap",
                width='small',
                help="The Market Cap of the symbol/industry",
                format="%f",
                min_value=0,
                max_value=total_market_cap,
            ),
            "pe": st.column_config.NumberColumn(
                "P/E",
                help="Price/Earnings",
                format="%.2f",
            ),
            "pb": st.column_config.NumberColumn(
                "P/B",
                help="Price/Book",
                format="%.2f",
            ),
            "roe": st.column_config.NumberColumn(
                "ROE",
                help="Return on Equity",
                format="%.2f",
            ),
            "revenueGrowth1Year": st.column_config.NumberColumn(
                "Revenue Growth",
                help="1 Year Revenue Growth in %",
                format="%.2f",
            ),

        },
        hide_index=True,
        use_container_width=True,
        column_order=('ticker', "price_change", "marketCap", "pe", "pb", "roe", "revenueGrowth1Year")
        )


df = get_df()
symbols, industries, total_market_cap = get_market_info(df)
tab1, tab2 = st.tabs(['Filter', 'Compare'])
with tab1:
    st.title('Stock Filter', anchor=False)
    st.caption('Based on `HOSE & HNX`, of symbols with a market cap of more than `1000`')
    col1, col2 = st.columns(2)
    with col1:
        with st.popover('Select Metrics', use_container_width=True):
            st.subheader('Fundamentals:')
            fundamental_values = ['pe', 'pb', 'roe']
            params = {}
            # Generate inputs in the same line
            cols = st.columns(len(fundamental_values))
            for col, col_container in zip(fundamental_values, cols):
                params[col] = col_container.number_input(f"{col.upper()} >" if col=='roe' else f"{col.upper()} <", value=None, min_value=0)

            st.subheader('Technical:')
            col1a, col1b, col1c = st.columns(3)
            with col1a:
                params['rsi14'] = st.number_input("RSI14 <", value=None, min_value=0.01)
            with col1b:
                st.write('')
                st.write('')
                params['macd'] = st.checkbox('MACD < 0 and Increasing')

    with col2:
        col2a, col2b = st.columns(2)
        with col2a:
            industry = st.selectbox('Industry:',
                                    list(industries),
                                    placeholder='Industry',
                                    label_visibility='collapsed',
                                    index=None)
        with col2b:
            filter = st.button('Filter')

    if filter:
        tickers = filter_stock(df, params, industry)
        st.dataframe(tickers, hide_index=True)
with tab2:
    if "symbol_list" not in st.session_state:
        st.session_state.symbol_list = []

    st.title('Stock Comparison', anchor=False)
    st.caption('Compare stock symbols against each others and the entire industry')

    col1aa, col1ab, col1ac = st.columns(3)
    with col1aa:
        selection = st.multiselect('Select symbols:',
                                   symbols,
                                   st.session_state.symbol_list,
                                   placeholder='Select symbols',
                                   label_visibility='collapsed')

    if st.button('Compare'):
        st.session_state.symbol_list = selection
        generate_dataframe(df, st.session_state.symbol_list, total_market_cap)
