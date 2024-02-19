import streamlit as st
from plots import get_stock_data
from simulation import simulate_trading

st.set_page_config(layout="wide",
                   page_title='Stock Analysis')


def simulate(choice, symbol, days_away, period, order):
    df = get_stock_data(symbol, days_away=days_away)
    try:
        plot, stats = simulate_trading(choice, period, df['close'], 100_000_000, order, verbose=False)
        return plot, stats
    except Exception as e:
        st.error(f"Error: {e}")


if (('symbol' and 'days_away') not in st.session_state) or not st.session_state['symbol']:
    st.write('Please head on over to Analysis and pick a symbol (or days away)')
else:
    col1, col2 = st.columns(2)
    with col1:
        st.title('Strategy Simulation')
        st.write('Simulating buy and selling', st.session_state['symbol'], 'within the last', st.session_state['days_away'], 'days')
        col1s, col2s = st.columns(2)
        with col1s:
            choice = st.selectbox('Pick a Strategy',options=["Pick a Strategy", "Random", "Momentum", 'Mean Reversion', 'ARIMA'], label_visibility='collapsed', placeholder='Pick a Strategy')
            period = st.slider('Pick a lookback period', min_value=1, max_value=30) if (choice == 'Momentum' or choice == 'Mean Reversion') else None
            params = st.text_input('Pick ARIMA parameters (p,d,q)', placeholder="p,d,q").split(',') if choice == 'ARIMA' else '0,0,0'
            order = (tuple(map(int, filter(None, params)))
                    if params != '0,0,0'
                    else None)

        with col2s:
            clicked = st.button('Simulate')
    if clicked:
        if choice == 'Pick a Strategy':
            st.error('Please pick a Strategy before running the simulation')
        else:
            plot, stats = simulate(choice, st.session_state['symbol'], st.session_state['days_away'], period, order)
            with col2:
                st.write("")
                st.write("")
                st.write("")
                st.write("")
                st.write("")
                st.write("")
                st.write("")
                st.write("")
                st.dataframe(stats, use_container_width=True)
            st.subheader(f'Simulation of {choice} strategy')
            st.pyplot(plot)
