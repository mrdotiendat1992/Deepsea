import streamlit as st 
import pandas as pd
from load_data import get_data
import plotly.express as px 

st.logo("logo_white.png",size= 'large')
st.markdown(
    """
    <style>
    .centered-title {
        text-align: center;
        margin-top: 200 px;
        color: 'rgb(255,255,255)';
        font-size : 48px;
    }
    div.block-container{padding-top:1.5rem};
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(f'<h1 class="centered-title">BÁO CÁO HIỆU SUẤT CÔNG NHÂN TNC</h1>', unsafe_allow_html=True)

nha_may = st.sidebar.selectbox("Chọn nhà máy",options=['NT1','NT2'])
df_tnc = get_data("INCENTIVE",f"SELECT * FROM HIEU_SUAT_CN_TNC01 WHERE CHUYEN <> '' AND SO_NGAY <=90 AND NHA_MAY = '{nha_may}' ORDER BY NGAY desc")
df_tnc['Năm'] = df_tnc['NGAY'].str[:4]
df_tnc['Tháng'] = df_tnc['NGAY'].str[5:7]
df_tnc['Ngày'] = df_tnc['NGAY'].str[-2:]

ds_nam = df_tnc['Năm'].sort_values(ascending=False).unique()
nam = st.sidebar.selectbox("Chọn năm",options=ds_nam)
ds_thang = df_tnc.query("Năm == @nam")['Tháng'].sort_values(ascending=False).unique()
thang = st.sidebar.selectbox("Chọn tháng",options=ds_thang)

df_tnc_filtered = df_tnc.query("Năm == @nam and Tháng == @thang")
df_tnc_filtered['Hiệu suất'] = df_tnc_filtered['EFF'].apply(lambda x: f"{x:,.0%}")
df_tnc_filtered['Ngày thứ'] = 'Ngày thứ ' + (df_tnc_filtered['SO_NGAY']+1).astype(str)

fig = px.scatter(
    data_frame= df_tnc_filtered.sort_values('SO_NGAY',ascending=True),
    x= 'Ngày thứ',
    y= 'EFF',
    color='CHUYEN',
    hover_data={
        'Hiệu suất' : True,
        'MST' : True,
        'HO_TEN' : True,
        'CHUYEN' : True,
        'EFF' : False,
        'SAH' : True,
        'SO_GIO' : True
    } 
)
fig.update_layout(
    title = "Hiệu suất công nhân TNC theo số ngày vào công ty",
)
fig.update_yaxes(
    tickformat = ",.0%"
)
fig.update_traces(
    marker = dict(size = 14)
)
st.plotly_chart(fig,use_container_width=True)

with st.expander("Dữ liệu chi tiết"):
    st.dataframe(df_tnc_filtered)