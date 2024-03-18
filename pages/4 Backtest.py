import streamlit as st
from functions.simulation import test_market, split_results

st.set_page_config(layout="wide",
                   page_title='Against Market')


@st.cache_data(show_spinner='Running against `HOSE` (~5 Minutes)')
def display_results():
    results = test_market(st.session_state['choice'], st.session_state['period'], st.session_state['days_away'])
    wins, losses = split_results(results)
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f'Won against {len(wins)} symbols')
        st.dataframe(wins, use_container_width=True)
    with col2:
        st.subheader(f'Lost against {len(losses)} symbols')
        st.dataframe(losses, use_container_width=True)


if (('symbol' and 'days_away' and 'choice' and 'period') not in st.session_state) or (st.session_state['choice'] is None):
    st.write('Please head on over to `Simulate` and simulate a strategy')
else:
    st.title('Test Against Market')
    st.write('Using', st.session_state['choice'], 'at', st.session_state['period'])
    if st.button('Run'):
        st.subheader('Here are the results:', anchor=False)
        display_results()

try:
    with st.sidebar:
        st.write(st.page_link("https://www.linkedin.com/in/hmdank/", label="@dank"))
except Exception:
    pass
