import streamlit as st
from plots import generate_data_plot, generate_acf_pacf_plots, generate_histogram_plot, fetch_data
import pandas as pd
st.set_page_config(layout="wide",
                   page_title='Stock Analysis')


def main():
    st.title('Stock Analysis')
    if 'symbol' not in st.session_state:
        st.session_state['symbol'] = ''

    symbol = st.text_input('Enter Stock Symbol:', st.session_state['symbol'])
    if 'days_away' not in st.session_state:
        st.session_state['days_away'] = 365
    days_away = st.number_input('Enter Days Away:', min_value=1, value=st.session_state['days_away'])

    if st.button('Generate Plots'):
        if symbol:
            st.session_state['symbol'] = symbol
            st.session_state['days_away'] = days_away
            graph(symbol, days_away)
        else:
            st.error('Invalid symbol')


def graph(symbol, days_away):
    try:
        df = fetch_data(symbol, days_away=days_away)
        returns = df['close'].pct_change().dropna()
        plot_data = generate_data_plot(df)
        plot_histogram = generate_histogram_plot(df)
        plot_acf_pacf = generate_acf_pacf_plots(df)
        summary_data = {'Statistic': ['Mean', 'Median'],
                        'Return': [returns.mean(), returns.median()]}
        summary_df = pd.DataFrame(summary_data)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader('Price Plots')
            st.pyplot(plot_data)
            st.subheader('ACF and PACF Plots')
            st.pyplot(plot_acf_pacf)
            st.write("Summary Statistics:")
            st.dataframe(summary_df, hide_index=True, use_container_width=True)

        with col2:
            st.subheader('Histogram Plot')
            st.pyplot(plot_histogram)





    except Exception as e:
        st.error(f"Error: {e}")


if __name__ == '__main__':
    main()
