import streamlit as st
from vnstock import stock_screening_insights
from functions.plots import get_stock_data
from functions.select import fundamental_selections, technical_selections, filter_stock, compare_stocks
st.set_page_config(layout="wide",
                   page_title='Stock Filter')


def calc_total_market_cap():
    params = {
        'exchangeName': 'HOSE,HNX',
    }
    df = stock_screening_insights(params, size=1700, drop_lang='vi')
    total_cap = df.loc[:, ['marketCap']].sum()
    return int(total_cap[0])


def add_symbol(symbol):
    try:
        df = get_stock_data(symbol, days_away=5)
        st.session_state.symbol_list.append(symbol)
    except Exception:
        st.error('Invalid Symbol')


tab1, tab2 = st.tabs(['Filter', 'Compare'])
with tab1:
    st.title('Stock Filter')
    st.caption('Based on `HOSE & HNX`, of symbols with a market cap of more than `1000`')
    col1a, col1b, col1c = st.columns(3)
    with col1a:
        fundamental = st.multiselect('Fundamental Metrics:',
                                     list(fundamental_selections.keys()))

    with col1b:
        technical = st.multiselect('Technical Metrics:',
                                   list(technical_selections.keys()))
    with col1c:
        filter = st.button('Filter')

    if filter:
        params = fundamental + technical
        tickers = filter_stock(params)
        st.dataframe(tickers, hide_index=True)
with tab2:
    if "symbol_list" not in st.session_state:
        st.session_state.symbol_list = []

    st.title('Stock Comparison')
    st.caption('Compare stock symbols against each others and the entire industry')
    col1a, col1b, col1c = st.columns(3)

    with col1a:
        col1aa, col1ab = st.columns(2)
        with col1aa:
            symbol = st.text_input('Enter Stock Symbol:')
    if symbol and symbol not in st.session_state.symbol_list and len(symbol) == 3:
        add_symbol(symbol.upper())
    with col1c:
        st.subheader('Symbols queue:')
        if st.session_state.symbol_list:
            result_string = ', '.join(st.session_state.symbol_list)
            st.caption(result_string)
    if st.button('Compare'):
        st.dataframe(
            compare_stocks(st.session_state.symbol_list),
            column_config={
                "marketCap": st.column_config.ProgressColumn(
                    "Market Cap",
                    help="The Market Cap of the symbol/industry",
                    format="%f",
                    min_value=0,
                    max_value=calc_total_market_cap(),
                ),
            },
            hide_index=True,
            use_container_width=True,
            )
