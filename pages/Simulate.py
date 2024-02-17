import streamlit as st
from plots import get_stock_data
from simulation import simulate_trading

st.set_page_config(layout="wide",
                   page_title='Stock Analysis')


def main():
    col1, col2 = st.columns(2)
    if (('symbol' and 'days_away') not in st.session_state) or not st.session_state['symbol']:
        st.write('Please head on over to Analysis and pick a symbol (or days away)')
    else:
        with col1:
            st.title('Strategy Simulation')
            st.write('Simulating buy and selling', st.session_state['symbol'], 'within the last', st.session_state['days_away'], 'days')
            col1s, col2s = st.columns(2)
            with col1s:
                choice = st.selectbox('Pick a Strategy',options=["Pick a Strategy", "Random", "Momentum"], label_visibility='collapsed', placeholder='Pick a Strategy')
                if choice == 'Momentum':
                    days = st.slider('Pick a lookback period', min_value=1, max_value=30)
            with col2s:
                clicked = st.button('Simulate')
                if choice == 'Pick a Strategy':
                    st.error('Please pick a Strategy before running the simulation')
                else:
                    plot, stats = simulate(choice, st.session_state['symbol'], st.session_state['days_away'])
        if clicked:
            st.subheader(f'Simulation of {choice} strategy')
            st.pyplot(plot)
            st.dataframe(stats)


def simulate(choice, symbol, days_away):
    try:
        df = get_stock_data(symbol, days_away=days_away)
        plot, stats = simulate_trading(choice, df['close'].pct_change().dropna(), df['close'], 100_000_000, 0.5, None, verbose=False)
        return plot, stats
    except Exception as e:
        st.error(f"Error: {e}")


if __name__ == '__main__':
    main()
