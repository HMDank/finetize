import streamlit as st
import hashlib
import io
import matplotlib as plt
import matplotlib
from plots import get_stock_data
from simulation import simulate_trading, optimize_choice, simulate_buy_hold

st.set_page_config(layout="wide",
                   page_title='Stock Analysis')


def draw_data(column, stats, choice, plot):
    with column:
        st.write('')
        st.write('')
        st.write('')
        st.write('')
        st.dataframe(stats, width=400)
    st.subheader(f'Simulation of `{choice}` strategy')
    st.pyplot(plot)
    cola, colb, colc = st.columns(3)
    with cola:
        baseline0 = simulate_buy_hold(st.session_state['symbol'], st.session_state['days_away'])
        st.metric(label='Buy and Hold', value=f'{baseline0*100:.2f}%',
                  delta=f'{(stats["Return"] - baseline0)*100:.2f}%', help='Buy at the very start and sell at the very end')
    with colc:
        with st.expander('Assumptions:'):
            st.write('Taxes account for `0.1%`')
            st.write('Transaction fees account for `0.25%`')
            st.write('Money will return after `1` day when selling')
            st.write('Expected market return: `15%`')
            st.write('Risk-free rate: `4.5%`')
            st.write(f'Position sizing: `{st.session_state["position_sizing"]:.2f}%`')



if (('symbol' and 'days_away') not in st.session_state) or not st.session_state['symbol']:
    st.write('Please head on over to Analysis and pick a symbol (or days away)')
else:
    col1, col2 = st.columns(2)
    with col1:
        st.title('Strategy Simulation')
        st.write(f"Simulating buy and selling `{st.session_state['symbol']}` within the last `{st.session_state['days_away']}` days")
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
            Auto = st.button('Auto', help='Auto generate the best period for returns') if (choice == 'Momentum' or choice == 'Mean Reversion') else None
    if Simulate:
        if choice is None:
            with col1s:
                st.error('Please pick a Strategy before running the simulation')
        else:
            plot, stats = simulate_trading(choice, period, st.session_state['symbol'], st.session_state['days_away'], 100_000_000, order, st.session_state['position_sizing'], verbose=False, plot=True)
            st.session_state['period'] = period
            draw_data(col2, stats, choice, plot)
    if Auto:
        df = get_stock_data(st.session_state['symbol'], days_away=st.session_state['days_away'])
        best_period = optimize_choice(choice, st.session_state['symbol'], st.session_state['days_away'], st.session_state['position_sizing'])
        st.session_state['period'] = best_period
        plot, stats = simulate_trading(choice, period, st.session_state['symbol'], st.session_state['days_away'], 100_000_000, order, st.session_state['position_sizing'], verbose=False, plot=True)
        draw_data(col2, stats, choice, plot)

try:
    with st.sidebar:
        st.write(st.page_link("https://www.linkedin.com/in/hmdank/", label="@dank"))
except Exception:
    pass
