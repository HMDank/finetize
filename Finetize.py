import streamlit as st

st.set_page_config(layout="wide",
                   page_title='Finetize')


st.title("Finetize", anchor=False)
st.subheader('Simulate a Trading Strategy, only with 2 steps!', anchor=False)
st.markdown('''
1. Navigate through the sidebar and select a symbol (and period away from today) in `Analysis` to see the symbol's analysis.
2. Head to `Simulation` to simulate a trading strategy on that same exact stock data!
''')
st.write('')
st.caption("(Please feel free to contact me via the link on the sidebar!)")
st.subheader('Have fun Trading!', anchor=False)

try:
    with st.sidebar:
        st.write(st.page_link("https://www.linkedin.com/in/hmdank/", label="@dank"))
except Exception:
    pass
