import streamlit as st
from functions.plots import generate_data_plot, generate_acf_plots, generate_histogram_plot, get_stock_data, generate_metrics, generate_scatter_plot, show_full_name
from functions.simulation import calculate_position_sizing
import pandas as pd
import traceback
st.set_page_config(layout="wide",
                   page_title='Stock Analysis')


@st.cache_data(show_spinner="Retrieving stocks's data")
def retrieve_data(symbol, days_away):
    try:
        df = get_stock_data(symbol, days_away=days_away).dropna()
        returns = df['close'].pct_change()
    except Exception:
        st.error('Invalid Stock Symbol')
        return
    return df, returns


@st.cache_data(show_spinner='Generating Plots')
def graph_price_plot(df, data_selection='Price'):
    fig = generate_data_plot(df, data_selection)
    return fig


@st.cache_data(show_spinner='Generating Plots')
def graph_col1_plots(symbol, days_away):
    df, returns = retrieve_data(symbol, days_away)
    plot_histogram = generate_histogram_plot(df)
    plot_acf = generate_acf_plots(returns, plot_pacf=False)
    plot_pacf = generate_acf_plots(returns, plot_pacf=True)
    # plot_acf_pacf = generate_acf_pacf_plots(df)
    summary_data = {'Statistic': ['Mean', 'Median', 'Min', 'Max'],
                    'Return': [returns.mean(), returns.median(), returns.min(), returns.max()]}
    summary_df = pd.DataFrame(summary_data)
    plot_scatter = generate_scatter_plot(df, days_away)
    return plot_histogram, plot_acf, plot_pacf, summary_df, plot_scatter


@st.cache_data(show_spinner='Loading Financial Metrics')
def calculate_financial_metrics(symbol):
    # metric_list = ['priceToEarning', 'priceToBook', 'roe', 'roa', 'earningPerShare', 'bookValuePerShare', 'interestMargin', 'badDebtPercentage']
    metrics = generate_metrics(symbol)
    return metrics

@st.cache_data(show_spinner="Loading AI's Response (Might take up to 5 Minutes)")
def show_name(symbol):
    name = show_full_name(symbol)
    return name


def main():
    st.title('Stock Analysis', anchor=False)
    col, col0 = st.columns(2)
    with col:
        subcol1, subcol2, subcol3 = st.columns(3)
        with subcol1:
            if 'symbol' not in st.session_state:
                st.session_state['symbol'] = ''

            symbol = st.text_input('Enter Stock Symbol:')
            if 'days_away' not in st.session_state:
                st.session_state['days_away'] = 365
            days_away = st.number_input('Enter Days Away:', min_value=1, value=st.session_state['days_away'])

    if symbol:
        st.session_state['symbol'] = symbol
        st.session_state['days_away'] = days_away
        df, returns = retrieve_data(symbol, days_away)
        col1, col2 = st.columns(2)
        try:
            with col1:
                data_selection = st.radio('Pick a plot:', [ 'Candlestick', 'Price', 'Returns'], horizontal=True)
                st.subheader('Price Plots')
            plot_data = graph_price_plot(df, data_selection)
            st.plotly_chart(plot_data, use_container_width=True)
            col1a, col2a = st.columns(2)
            with col1a:
                plot_histogram, plot_acf, plot_pacf, summary_df, plot_scatter = graph_col1_plots(symbol, days_away)
                acf, pacf = st.columns(2)
                with acf:
                    st.subheader('ACF')
                    st.plotly_chart(plot_acf, use_container_width=True)
                with pacf:
                    st.subheader('PACF')
                    st.plotly_chart(plot_pacf, use_container_width=True)
                st.subheader("Summary Statistics:")
                st.dataframe(summary_df, hide_index=True, use_container_width=True)
                metrics = calculate_financial_metrics(symbol)
                st.subheader(f'Financial Statistics')
                st.dataframe(metrics, use_container_width=True, height=520)

            with col2a:
                st.subheader('Histogram')
                st.plotly_chart(plot_histogram, use_container_width=True)
                st.subheader('Marginal Histogram vs Market')
                st.plotly_chart(plot_scatter, use_container_width=True)

        except Exception as e:
            tb_str = traceback.format_exception(type(e), e, e.__traceback__)
            st.error(f"{tb_str}")

        position_sizing = calculate_position_sizing(st.session_state['symbol'], df['close'])
        if 'position_sizing' not in st.session_state:
                st.session_state['position_sizing'] = 1
        st.session_state['position_sizing'] = position_sizing

        if len(symbol) == 3:
            with col0:
                st.title(show_name(st.session_state['symbol']), anchor=False)
                # st.markdown('<span style="color:#75AB9D; font-size: 18px; font-weight: bold; font-family: \'Roboto Mono\', monospace;">AI Analysis</span>', unsafe_allow_html=True)
                # with st.container(height=112, border=True):
                #     st.markdown('<link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,100;0,300;0,400;0,700;0,900;1,100;1,300;1,400;1,700;1,900&family=Nunito+Sans:ital,opsz,wght@0,6..12,200..1000;1,6..12,200..1000&family=Roboto+Mono:ital,wght@0,100..700;1,100..700&family=Source+Sans+3:ital,wght@0,200..900;1,200..900&display=swap" rel="stylesheet">', unsafe_allow_html=True)
                #     st.markdown(f'<span style="color:#75AB9D; font-size: 14px; font-family: \'Roboto Mono\', monospace;">{show_ai_response(df)}</span>', unsafe_allow_html=True)


    try:
        with st.sidebar:
            st.write(st.page_link("https://www.linkedin.com/in/hmdank/", label="@dank"))
    except Exception:
        pass


if __name__ == '__main__':
    main()
