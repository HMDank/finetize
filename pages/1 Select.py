import streamlit as st
from vnstock import stock_screening_insights
from functions.plots import get_stock_data
from functions.select import fundamental_selections, technical_selections, filter_stock, compare_stocks
st.set_page_config(layout="wide",
                   page_title='Stock Filter')

@st.cache_data()
def get_market_info():
    default_params = {
        'exchangeName': 'HOSE,HNX',
    }
    df = stock_screening_insights(default_params, size=1700, drop_lang='vi')
    tickers = df['ticker'].tolist()
    industries = df['industryName.en'].unique().tolist()
    industries.sort()
    return tickers, industries


@st.cache_data(show_spinner='Loading Comparison Table')
def generate_dataframe(symbol_list):
    st.dataframe(
        compare_stocks(symbol_list),
        column_config={
            "ticker": st.column_config.TextColumn(
                "Symbol",
            ),
            "price_change": st.column_config.LineChartColumn(
                "Price Change",
                width="small",
                help="Change in price every minute in the last trading session",
                y_min=-1,
                y_max=1
            ),
            "marketCap": st.column_config.ProgressColumn(
                "Market Cap",
                width='small',
                help="The Market Cap of the symbol/industry",
                format="%f",
                min_value=0,
                max_value=calc_total_market_cap(),
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


def calc_total_market_cap():
    params = {
        'exchangeName': 'HOSE,HNX',
    }
    df = stock_screening_insights(params, size=1700, drop_lang='vi')
    total_cap = df.loc[:, ['marketCap']].sum()
    return int(total_cap.iloc[0])


symbols, industries = get_market_info()
tab1, tab2 = st.tabs(['Filter', 'Compare'])
with tab1:
    st.title('Stock Filter', anchor=False)
    st.caption('Based on `HOSE & HNX`, of symbols with a market cap of more than `1000`')
    col1a, col1b, col1c, col1d = st.columns(4)
    with col1a:
        fundamental = st.multiselect('Fundamental Metrics:',
                                     list(fundamental_selections.keys()),
                                     placeholder='Fundamental Metrics', label_visibility='collapsed',
                                     )

    with col1b:
        technical = st.multiselect('Technical Metrics:',
                                   list(technical_selections.keys()),
                                   placeholder='Technical Metrics',
                                   label_visibility='collapsed')
    with col1c:
        industry = st.selectbox('Industry:',
                                   list(industries),
                                   placeholder='Industry',
                                   label_visibility='collapsed',
                                   index=None)
    with col1d:
        filter = st.button('Filter')

    if filter:
        params = fundamental + technical
        tickers = filter_stock(params, industry)
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
        generate_dataframe(st.session_state.symbol_list)