import streamlit as st
import pandas as pd
import pyodbc
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
from datetime import datetime
from datetime import date,timedelta
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from load_data import get_data
import time
import numpy as np

st.markdown(
    """
    <style>
    .centered-title {
        text-align: center;
        margin-top: 0 px;
        color: 'rgb(255,255,255)';
        font-size : 48px;
    }
    div.block-container{padding-top:1.5rem};
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(f'<h1 class="centered-title">HIỆU SUẤT THEO STYLE</h1>', unsafe_allow_html=True)

df1 = get_data('DW','SELECT WorkDate, LINE, STYLE_A, SAM FROM ETS_5 WHERE WORKDATE < CAST(GETDATE() AS DATE)')
min_date = df1['WorkDate'].min()
max_date = df1['WorkDate'].max()

fty = ['NT1','NT2', 'NT3']
sel_fty = st.sidebar.multiselect("Chọn nhà máy:",options = fty,default=fty)

today = date.today() if date.today().day >1 else date.today() - timedelta(days=1)
first_day_of_month =  today.replace(day=1)
start_date = st.sidebar.date_input(label="Từ ngày:",value= first_day_of_month)
end_date = st.sidebar.date_input(label="Đến ngày:", value= max_date)

df2 = get_data('DW','SELECT Style_P, WorkDate, LINE FROM PPC')
df2['WorkDate'] = pd.to_datetime(df2['WorkDate'], format='%Y-%m-%d')
df2['WorkDate'] = df2['WorkDate'].dt.date

valid_fac = [group[-1] for group in sel_fty] 
styles = [style for style in df2[
    (df2['LINE'].str[0].isin(valid_fac)) & 
    (df2['WorkDate'] >= start_date) & 
    (df2['WorkDate'] <= end_date)
]['Style_P'].unique() if pd.notna(style) and style != ""]

sel_style = st.sidebar.multiselect("Chọn Style:",options=styles,default=styles)

valid_fac_str = ", ".join(valid_fac)
style_conditions = " OR ".join([f"STYLE LIKE '%{style}%'" for style in sel_style])
df3 = get_data("INCENTIVE",f"SELECT NGAY, MST, HO_TEN, CHUYEN, SCP, STYLE, TGLV, EFF FROM thuong_cn_may_hang_ngay_chi_tiet WHERE LEFT(CHUYEN, 1) IN ({valid_fac_str}) AND NGAY BETWEEN '{start_date}' AND '{end_date}' AND ({style_conditions}) ORDER BY NGAY")

df3['Efficiency'] = df3['EFF'].map(lambda x: f"{x*100:.2f}%")
df3 = df3.drop(columns=['EFF'])

df_merged = pd.merge(df3, df1, 
                    left_on=['CHUYEN', 'STYLE', 'NGAY'],
                    right_on=['LINE', 'STYLE_A', 'WorkDate'],  
                    how='inner')

df_merged.drop(columns=['LINE', 'STYLE_A', 'WorkDate'], inplace=True)
move_col = df_merged.pop('SAM')
df_merged.insert(6,'SAM',move_col)

st.dataframe(df3,hide_index=True, use_container_width=True)
