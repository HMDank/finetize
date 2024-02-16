import streamlit as st
from plots import fetch_data
from simulation import simulate_random_buying

st.set_page_config(layout="wide",
                   page_title='Stock Analysis')


def main():
    st.title('Strategy Simulation')
    col1, col2 = st.columns(2)
    if (('symbol' and 'days_away') not in st.session_state) or not st.session_state['symbol']:
        st.write('Please head on over to Analysis and pick a symbol (or days away)')
    else:
        with col1:
            st.write('Simulating buy and selling', st.session_state['symbol'], 'within the last', st.session_state['days_away'], 'days')
        with col2:
            choice = st.radio('Pick a Strategy:', ["Random", "If Last Positive, Buy"], horizontal=True)
        if st.button('Simulate'):
            simulate(choice, st.session_state['symbol'], st.session_state['days_away'])


def simulate(choice, symbol, days_away):
    try:
        df = fetch_data(symbol, days_away=days_away)
        plot, stats = simulate_random_buying(choice, df['close'].pct_change().dropna(), df['close'], 100, 0.5, None, verbose=False)
        st.subheader('Simulation')
        st.pyplot(plot)
        st.dataframe(stats)
    except Exception as e:
        st.error(f"Error: {e}")


if __name__ == '__main__':
    main()
