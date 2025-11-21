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

df = get_data('INCENTIVE',"SELECT * FROM TI_LE_LOI WHERE NGAY < CAST(GETDATE() AS DATE) AND NGAY >= '2024-09-01'")
df['XUONG'] = df['CHUYEN'].str[:1] +'P0' + df['CHUYEN'].str[1:2]
df['NHA_MAY'] = 'NT' + df['CHUYEN'].str[:1]
df['CODE'] = df['CHUYEN'].str[2:-2]
df['NHOM'] = df['CODE'].apply(lambda x: 'Cắt' if x == 'C' else 'May' if x == 'S' else 'QC May' if x == 'QC1'
                              else 'Là' if x == 'I' else 'QC Là' if x == 'QC2' else 'Hoàn thiện' if x == 'F' else '')
df.pop('CODE')
#di chuyển cột
move_col = df.pop('NHA_MAY')
df.insert(0,'NHA_MAY',move_col)
move_col = df.pop('XUONG')
df.insert(1,'XUONG',move_col)

#chuyển cột WorkDate về dạng date
df['NGAY'] = pd.to_datetime(df['NGAY'], format='%Y-%m-%d')
df['NGAY'] = df['NGAY'].dt.date

###########################
fty = ['NT1','NT2', 'NT3']
sel_fty = st.sidebar.selectbox("Chọn nhà máy:",options = fty,index=fty.index(st.session_state.factory))
unit = df[df['NHA_MAY'] == sel_fty]['XUONG'].unique()
unit_sorted = sorted(unit, reverse= False)
sel_unit = st.sidebar.multiselect("Chọn xưởng:", options= unit, default= unit_sorted)

min_date = df['NGAY'].min()
today = date.today() if date.today().day >1 else date.today() - timedelta(days=1)
first_day_of_month =  today.replace(day=1)
start_date = st.sidebar.date_input(label="Từ ngày:",value= first_day_of_month)

max_date = df['NGAY'].max()
end_date = st.sidebar.date_input(label="Đến ngày:", value= max_date)

st.markdown(f'<h1 class="centered-title">BÁO CÁO TỈ LỆ LỖI {sel_fty}</h1>', unsafe_allow_html=True)
df = df[
(df['XUONG'].isin(sel_unit)) & 
(df['NGAY'] >= start_date) & 
(df['NGAY'] <= end_date)]

OQL_cat = df[df['NHOM']=='Cắt']['TI_LE_LOI'].mean()
OQL_may = df[df['NHOM']=='May']['TI_LE_LOI'].mean()
OQL_qc1 = df[df['NHOM']=='QC May']['TI_LE_LOI'].mean()
OQL_la = df[df['NHOM']=='Là']['TI_LE_LOI'].mean()
OQL_qc2 = df[df['NHOM']=='QC Là']['TI_LE_LOI'].mean()
OQL_hoanthien = df[df['NHOM']=='Hoàn thiện']['TI_LE_LOI'].mean()

cols = st.columns(6, gap= 'large')
with cols[0]:
    st.metric(label= 'Cắt',value= f'{OQL_cat:,.1%}')
with cols[1]:
    st.metric(label= 'May',value= f'{OQL_may:,.1%}')
with cols[2]:
    st.metric(label= 'QC May',value= f'{OQL_qc1:,.1%}')
with cols[3]:
    st.metric(label= 'Là',value= f'{OQL_la:,.1%}')
with cols[4]:
    st.metric(label= 'QC Là',value= f'{OQL_qc2:,.1%}')
with cols[5]:
    st.metric(label= 'Hoàn thiện',value= f'{OQL_hoanthien:,.1%}')

  
st.markdown("---")
df_nhom_ngay = df.groupby(by=['NHOM','NGAY']).agg({'TI_LE_LOI' : 'mean'}).reset_index()

df_nhom_ngay['TI_LE_LOI_formated']= df_nhom_ngay['TI_LE_LOI'].apply(lambda x: f"{x:,.1%}")
df_nhom_ngay = df_nhom_ngay.sort_values('NGAY')
# df_nhom_ngay
category_order = {
    'NHOM': ['Cắt', 'May', 'QC May', 'Là', 'QC Là', 'Hoàn thiện']
}
#config chung cho các biểu đồ plotly
config = {
    'displayModeBar': True,  # Hiển thị/thêm thanh công cụ
    'modeBarButtonsToRemove': ['zoom', 'select', 'lasso2d', 'resetScale', 'toImage'],  # Ẩn nút
    'displaylogo': False,  # Ẩn logo Plotly
    'modeBarButtonsToAdd': []  # Đảm bảo không thêm bất kỳ nút nào khác
}
fig = px.line(df_nhom_ngay,
                x= df_nhom_ngay['NGAY'],
                y= df_nhom_ngay['TI_LE_LOI'],
                color=df_nhom_ngay['NHOM'],
                category_orders=category_order,
                color_discrete_map={
                    'Cắt' : 'blue',
                    'May' : 'lightblue',
                    'QC May' : 'orange',
                    'Là' : 'green',
                    'QC Là' : 'red',
                    'Hoàn thiện' : 'purple'
                },
                text= df_nhom_ngay['TI_LE_LOI_formated']
                )
fig.update_xaxes(
    dtick = 'D1',
    tickangle = 45,
    tickformat = "%d/%m"
)
fig.update_yaxes(
    tickformat = ",.0%"
)
fig.update_layout(
    xaxis_title = 'Ngày',
    yaxis_title = 'Tỉ lệ lỗi',
    title = "Tỉ lệ lỗi theo ngày",
    legend_title_text = 'Nhóm'
)
fig.update_traces(
    textposition = 'top center',
    textfont = dict(size = 14)
)
fig.update_layout(dragmode="pan")

st.plotly_chart(fig,use_container_width=True,config=config)

st.markdown("---")
## Heatmap CẮT
df_cat = df[df['NHOM']=='Cắt']
df_cat_pivot = pd.pivot_table(data=df_cat,index='CHUYEN',columns='NGAY',values='TI_LE_LOI')
# df_cat_pivot
fig = px.imshow(
    df_cat_pivot,
    color_continuous_scale=px.colors.diverging.RdYlGn[::-1], 
    text_auto= True)
fig.update_xaxes(
    dtick = 'D1',
    tickformat = '%d/%m',
    tickfont = dict(size = 12)
)
fig.update_yaxes(
    tickfont = dict(size = 14),
    dtick = 'D1'
)
num_row = df_cat_pivot.shape[0]
row_hight = 35

fig.update_layout(
    title = "Biểu đồ nhiệt - Nhóm Cắt",
    xaxis_title = "Ngày",
    yaxis_title = "Chuyền",
    # height = num_row * row_hight
)
fig.update_traces(
    texttemplate='%{z:.1%}',
    textfont=dict(size=14),
    zmin=0,
    zmax=1,
)
fig.update_layout(dragmode="pan")

st.plotly_chart(fig,use_container_width=True,key='heatmap0',config=config)
## Heatmap MAY
df_may = df[df['NHOM']=='May']
df_may_pivot = pd.pivot_table(data=df_may,index='CHUYEN',columns='NGAY',values='TI_LE_LOI')
fig = px.imshow(
    df_may_pivot,
    color_continuous_scale=px.colors.diverging.RdYlGn[::-1], 
    text_auto= True)
fig.update_xaxes(
    dtick = 'D1',
    tickformat = '%d/%m',
    tickfont = dict(size = 12)
)
fig.update_yaxes(
    tickfont = dict(size = 14),
    dtick = 'D1'
)
num_row = df_may_pivot.shape[0]
row_hight = 35

fig.update_layout(
    title = "Biểu đồ nhiệt - Nhóm May",
    xaxis_title = "Ngày",
    yaxis_title = "Chuyền",
    height = num_row * row_hight
)
fig.update_traces(
    texttemplate='%{z:.1%}',
    textfont=dict(size=14),
    zmin=0,
    zmax=1,
)
fig.update_layout(dragmode="pan")

st.plotly_chart(fig,use_container_width=True,key='heatmap1',config=config)
## Heatmap QC MAY
df_qcmay = df[df['NHOM']=='QC May']
df_qcmay_pivot = pd.pivot_table(data=df_qcmay,index='CHUYEN',columns='NGAY',values='TI_LE_LOI')
fig = px.imshow(
    df_qcmay_pivot,
    color_continuous_scale=px.colors.diverging.RdYlGn[::-1], 
    text_auto= True)
fig.update_xaxes(
    dtick = 'D1',
    tickformat = '%d/%m',
    tickfont = dict(size = 12)
)
fig.update_yaxes(
    tickfont = dict(size = 14),
    dtick = 'D1'
)
num_row = df_qcmay_pivot.shape[0]
row_hight = 35

fig.update_layout(
    title = "Biểu đồ nhiệt - Nhóm QC May",
    xaxis_title = "Ngày",
    yaxis_title = "Chuyền",
    # height = num_row * row_hight
)
fig.update_traces(
    texttemplate='%{z:.1%}',
    textfont=dict(size=14),
    zmin=0,
    zmax=1,
)
fig.update_layout(dragmode="pan")

st.plotly_chart(fig,use_container_width=True,key='heatmap2',config=config)
## Heatmap LA
df_la = df[df['NHOM']=='Là']
df_la_pivot = pd.pivot_table(data=df_la,index='CHUYEN',columns='NGAY',values='TI_LE_LOI')
fig = px.imshow(
    df_la_pivot,
    color_continuous_scale=px.colors.diverging.RdYlGn[::-1], 
    text_auto= True)
fig.update_xaxes(
    dtick = 'D1',
    tickformat = '%d/%m',
    tickfont = dict(size = 12)
)
fig.update_yaxes(
    tickfont = dict(size = 14),
    dtick = 'D1'
)
num_row = df_la_pivot.shape[0]
row_hight = 35

fig.update_layout(
    title = "Biểu đồ nhiệt - Nhóm Là",
    xaxis_title = "Ngày",
    yaxis_title = "Chuyền",
    # height = num_row * row_hight
)
fig.update_traces(
    texttemplate='%{z:.1%}',
    textfont=dict(size=14),
    zmin=0,
    zmax=1,
)
fig.update_layout(dragmode="pan")

st.plotly_chart(fig,use_container_width=True,key='heatmap3',config=config)
## Heatmap QC LA
df_qcla = df[df['NHOM']=='QC Là']
df_qcla_pivot = pd.pivot_table(data=df_qcla,index='CHUYEN',columns='NGAY',values='TI_LE_LOI')
fig = px.imshow(
    df_qcla_pivot,
    color_continuous_scale=px.colors.diverging.RdYlGn[::-1], 
    text_auto= True)
fig.update_xaxes(
    dtick = 'D1',
    tickformat = '%d/%m',
    tickfont = dict(size = 12)
)
fig.update_yaxes(
    tickfont = dict(size = 14),
    dtick = 'D1'
)
num_row = df_qcla_pivot.shape[0]
row_hight = 35

fig.update_layout(
    title = "Biểu đồ nhiệt - Nhóm QC Là",
    xaxis_title = "Ngày",
    yaxis_title = "Chuyền",
    # height = num_row * row_hight
)
fig.update_traces(
    texttemplate='%{z:.1%}',
    textfont=dict(size=14),
    zmin=0,
    zmax=1,
)
fig.update_layout(dragmode="pan")

st.plotly_chart(fig,use_container_width=True,key='heatmap4',config=config)
## Heatmap HOAN THIEN
df_hoanthien = df[df['NHOM']=='Hoàn thiện']
df_hoanthien_pivot = pd.pivot_table(data=df_hoanthien,index='CHUYEN',columns='NGAY',values='TI_LE_LOI')
fig = px.imshow(
    df_hoanthien_pivot,
    color_continuous_scale=px.colors.diverging.RdYlGn[::-1], 
    text_auto= True)
fig.update_xaxes(
    dtick = 'D1',
    tickformat = '%d/%m',
    tickfont = dict(size = 12)
)
fig.update_yaxes(
    tickfont = dict(size = 14),
    dtick = 'D1'
)
num_row = df_hoanthien_pivot.shape[0]
row_hight = 35

fig.update_layout(
    title = "Biểu đồ nhiệt - Nhóm hoàn thiện",
    xaxis_title = "Ngày",
    yaxis_title = "Chuyền",
    # height = num_row * row_hight
)
fig.update_traces(
    texttemplate='%{z:.1%}',
    textfont=dict(size=14),
    zmin=0,
    zmax=1,
)
fig.update_layout(dragmode="pan")

st.plotly_chart(fig,use_container_width=True,key='heatmap5',config=config)

