import streamlit as st
import hashlib
import io
import matplotlib as plt
import matplotlib
from plots import get_stock_data
from simulation import simulate_trading, optimize_choice, test_market

st.set_page_config(layout="wide",
                   page_title='Stock Analysis')


@st.cache_resource(hash_funcs={matplotlib.figure.Figure: hash})
def simulate(choice, symbol, days_away, period, order):
    # Your simulation code here
    df = get_stock_data(symbol, days_away=days_away)
    plot, stats = simulate_trading(choice, period, df['close'], 100_000_000, order, verbose=False, plot=True)

    return plot, stats


if (('symbol' and 'days_away') not in st.session_state) or not st.session_state['symbol']:
    st.write('Please head on over to Analysis and pick a symbol (or days away)')
else:
    col1, col2 = st.columns(2)
    with col1:
        st.title('Strategy Simulation')
        st.write('Simulating buy and selling', st.session_state['symbol'], 'within the last', st.session_state['days_away'], 'days')
        col1s, col2s = st.columns(2)
        with col1s:
            choice = st.selectbox('Pick a Strategy', options=["Random", "Momentum", 'Mean Reversion', 'ARIMA'], label_visibility='collapsed', placeholder='Pick a Strategy', index=None)
            st.session_state['choice'] = choice
            period = st.slider('Pick a lookback period', min_value=1, max_value=30) if (choice == 'Momentum' or choice == 'Mean Reversion') else None
            params = st.text_input('Pick ARIMA parameters (p,d,q)', placeholder="p,d,q").split(',') if choice == 'ARIMA' else '0,0,0'
            order = (tuple(map(int, filter(None, params)))
                     if params != '0,0,0'
                     else None)

        with col2s:
            Simulate = st.button('Simulate')
            st.write('')
            st.write('')
            Auto = st.button('Auto') if (choice == 'Momentum' or choice == 'Mean Reversion') else None
    if Simulate:
        if choice is None:
            with col1s:
                st.error('Please pick a Strategy before running the simulation')
        else:
            plot_hash, stats = simulate(choice, st.session_state['symbol'], st.session_state['days_away'], period, order)
            st.session_state['period'] = period
            with col2:
                st.write('')
                st.write('')
                st.write('')
                st.write('')
                st.dataframe(stats, width=400)
            st.subheader(f'Simulation of {choice} strategy')
            st.pyplot(plot_hash)
    if Auto:
        df = get_stock_data(st.session_state['symbol'], days_away=st.session_state['days_away'])
        best_period = optimize_choice(choice, df['close'])
        st.session_state['period'] = best_period
        plot_hash, stats = simulate(choice, st.session_state['symbol'], st.session_state['days_away'], best_period, order)
        with col2:
            st.write('')
            st.write('')
            st.write('')
            st.write('')
            st.dataframe(stats, width=400)
        st.subheader(f'Simulation of {choice} strategy')
        st.pyplot(plot_hash)

try:
    with st.sidebar:
        st.write(st.page_link("https://www.linkedin.com/in/hmdank/", label="@dank"))
except Exception:
    pass
