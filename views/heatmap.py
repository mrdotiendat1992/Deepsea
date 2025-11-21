import streamlit as st 

st.logo("logo_white.png",size= 'large')
st.markdown(
    """
    <style>
    .centered-title {
    text-align: center;
    div.block-container{padding-top:1rem};
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(f'<h1 class="centered-title">HEATMAP</h1>', unsafe_allow_html=True)