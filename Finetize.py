import streamlit as st

st.set_page_config(layout="wide",
                   page_title='Finetize')


st.title("Finetize", anchor=False)
st.subheader('Simulate a Trading Strategy, in 3 steps!', anchor=False)
st.markdown('''
1. No idea where to begin? Just navigate to `Select` on the sidebar to pick your starting symbol.
2. Select a symbol (and period away from today) in `Analyze` to see the symbol's analysis.
3. Head to `Simulate` to simulate a trading strategy on that same exact stock data!
4. Test the Strategy in `Backtest` and see how it holds against the market!
''')
st.write('')
st.caption("(Please feel free to contact me via the link on the sidebar!)")
st.subheader('Have fun Trading!', anchor=False)


try:
    with st.sidebar:
        st.write(st.page_link("https://www.linkedin.com/in/hmdank/", label="@dank"))
except Exception:
    pass
