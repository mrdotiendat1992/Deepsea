import streamlit as st 
import pandas as pd
from load_data import get_data,commit_query
from datetime import datetime,date,timedelta
import time
from dateutil.relativedelta import relativedelta
from helper.table import import_to_sql
from sqlalchemy import VARCHAR, NVARCHAR, INTEGER, DATE, DECIMAL
from db.base import engine_1, get_db_1
from fastapi import  HTTPException
import numpy as np
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
    div.block-container{padding-top:2rem};
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(f'<h1 class="centered-title">BÁO CÁO PPC</h1>', unsafe_allow_html=True)
#######
fty = ['NT1','NT2', 'NT3']
sel_fty = st.sidebar.multiselect("Chọn nhà máy:",options = fty,default=fty)

df_ppc = get_data("DW",f"SELECT * FROM PPC WHERE WORKDATE >= '2024-09-01' ORDER BY WORKDATE DESC,LINE")
df_ppc['Attn'] = df_ppc.apply(
    lambda x: 0.9 if str(x['Line'])[:1] == '1' and x['WorkDate'] < date(2025,11,10)
    else 0.91 if str(x['Line'])[:1] in ['2','3'] and x['WorkDate'] >= date(2025,5,1)
    else 0.93 if str(x['Line'])[:1] in ['2','3']
    else 0.95, axis=1)
df_ppc['Total_hours_P'] = df_ppc['Hours_P'] * df_ppc['Worker_P'] * df_ppc['Attn']
df_ppc['Eff'] = df_ppc['SAH_P']/df_ppc['Total_hours_P']
df_ppc['Fty'] = 'NT' + df_ppc['Line'].str[:1]
df_ppc['Unit'] = df_ppc['Line'].str[:1] + 'P0' + df_ppc['Line'].str[1:2]

# Convert WorkDate to datetime first
df_ppc['WorkDate'] = pd.to_datetime(df_ppc['WorkDate'], errors='coerce')

# Extract month and year safely
df_ppc['Month'] = df_ppc['WorkDate'].dt.month
df_ppc['Year'] = df_ppc['WorkDate'].dt.year

# If you want just the date (without time)
df_ppc['WorkDate'] = df_ppc['WorkDate'].dt.date

df_ppc = df_ppc.dropna(subset=['Qty_P','SAH_P','Hours_P','Worker_P'],how='all')
df_ppc = df_ppc[df_ppc['Worker_P'] > 0]

#Lấy SAM bên Incentive
df_SAM = get_data("INCENTIVE","""
                  SELECT STYLE AS Style_P ,TU_NGAY,DEN_NGAY , SUM(SAM) AS SAM
                    FROM SAM_SEW_2 WHERE LTRIM(RTRIM(PHAN_LOAI_CD)) = N'CĐ Chính'
                    GROUP BY STYLE ,TU_NGAY,DEN_NGAY
                    ORDER BY STYLE,TU_NGAY
                  """)
#chuyển sang định dạng datetime
df_SAM['TU_NGAY'] = pd.to_datetime(df_SAM['TU_NGAY'])
df_SAM['DEN_NGAY'] = pd.to_datetime(df_SAM['DEN_NGAY'])
#Ghép bảng df_ppc và bảng SAM
df_ppc = pd.merge(df_ppc,df_SAM,on='Style_P',how='left')
df_ppc = df_ppc[(df_ppc['WorkDate'] >= df_ppc['TU_NGAY']) & (df_ppc['WorkDate'] <= df_ppc['DEN_NGAY'])]
df_ppc = df_ppc.drop(['TU_NGAY', 'DEN_NGAY'], axis=1)
df_ppc = df_ppc.groupby(['Line', 'WorkDate', 'Style_P'], as_index=False).agg({
    'SAM': 'sum',  
    **{col: 'first' for col in df_ppc.columns if col not in ['Line', 'WorkDate', 'Style_P', 'SAM']} 
})
df_ppc = df_ppc.query("Fty in @sel_fty")

unit = df_ppc[df_ppc['Fty'].isin(sel_fty)]['Unit'].unique()
unit_sorted = sorted(unit, reverse= False)
sel_unit = st.sidebar.multiselect("Chọn xưởng:", options= unit, default= unit_sorted)

df_ppc=df_ppc[df_ppc['Unit'].isin(sel_unit)]

min_date = df_ppc['WorkDate'].min()
today = date.today() if date.today().day >1 else date.today() - timedelta(days=1)
first_day_of_month =  today.replace(day=1)
last_day_of_month = first_day_of_month + relativedelta(months=1) - timedelta(days=1)
start_date = st.sidebar.date_input(label="Từ ngày:",value= first_day_of_month,min_value=min_date)

max_date = df_ppc['WorkDate'].max()
value = last_day_of_month if last_day_of_month <= max_date else max_date
end_date = st.sidebar.date_input(label="Đến ngày:", value= value,max_value=max_date)

df_ppc =  df_ppc.query("WorkDate >= @start_date and WorkDate <= @end_date")
###############
# # Tải xuống file PPC mẫu
# with open("excel/File mẫu PPC.xlsx", "rb") as file:
#     st.sidebar.download_button(
#         label="Tải xuống File mẫu PPC",
#         data=file,
#         file_name="File mẫu PPC.xlsx",
#         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
#     )
# #Upload file kế hoạch mới
# file_to_upload = st.sidebar.file_uploader("Cập nhật mục tiêu",type=["xlsx"])
# up_file = st.sidebar.button("Tải lên file kế hoạch mới")

# if up_file:
#     if file_to_upload:
#         df = pd.read_excel(file_to_upload)
#         df = df.rename(columns={df.columns[0] : "Line"})
#         df['Chỉ số'] = df['Date'].apply(lambda x : 'Style_P' if x == 'Style' else 'Qty_P' if x == 'S.lượng' else 'SAH_P' if x == 'SAH'
#                                         else 'Hours_P' if x == 'AVG Hours' else 'Worker_P' if x == 'Total Worker' else None)
#         df = df.drop(columns= {df.columns[1],df.columns[2]})
        
#         df = df.dropna(subset=['Chỉ số'])
#         df['Line'] = df['Line'].fillna(method='ffill')
     
#         df = pd.melt(df,id_vars=['Chỉ số','Line'])
#         df.rename(columns={'variable' : 'WorkDate'},inplace=True)
#         df['WorkDate'] = pd.to_datetime(df['WorkDate'])
#         df['WorkDate'] = df['WorkDate'].dt.date
#         df = df.pivot(index=['Line','WorkDate'],columns='Chỉ số',values='value').reset_index()
#         df = df.dropna(subset=['Hours_P','Qty_P','SAH_P','Worker_P'],how= 'all')
#         new_order = ["WorkDate", "Line", "Style_P", "Qty_P","SAH_P","Hours_P","Worker_P"]  # Thứ tự mong muốn
#         df = df[new_order]
        
#         dtype = {
#             "WorkDate": DATE,
#             "Line": NVARCHAR(100),
#             "Style_P": NVARCHAR(100),
#             "Qty_P": INTEGER,
#             "SAH_P": DECIMAL(10,2),   
#             "Hours_P": DECIMAL(3,1),  
#             "Worker_P": INTEGER
#         }
#         try:
#             import_to_sql(df=df,table_name="PPC",dtype=dtype,engine=engine_1)
#             st.success("Cập nhật dữ liệu mới thành công!")
#             time.sleep(5)
#             st.rerun()
            
#         except Exception as e:
#             print(e)
#             HTTPException(status_code=500, detail="Internal server error")
#     else:
#         st.sidebar.warning("Vui lòng chọn file trước khi tải lên")
###############
Total_SAH = df_ppc['SAH_P'].sum()
Total_Qty = df_ppc['Qty_P'].sum()
Total_Hours = df_ppc['Total_hours_P'].sum()
Eff = Total_SAH/Total_Hours
Hours = df_ppc['Hours_P'].mean()
Workers = df_ppc['Worker_P'].sum()
WD = df_ppc['WorkDate'].nunique()
SAH_CN = Total_SAH/Workers
Attn = df_ppc['Attn'].mean()

st.subheader(f"Mục tiêu nhà máy {", ".join(sel_fty)}")
cols = st.columns(4)
with cols[0]:
    st.metric("Tổng SAH",value=f"{Total_SAH:,.0f}")
    st.metric("Tổng sản lượng",value=f"{Total_Qty:,.0f}")
with cols[1]:
    st.metric("Tổng TGLV",value=f"{Total_Hours:,.0f}")
    st.metric("TGLV trung bình (giờ)",value=f"{Hours:,.1f}")
with cols[2]:
    st.metric("Hiệu suất",value=f"{Eff:,.0%}")
    st.metric("SAH/CN/Ngày",value=f"{SAH_CN:,.1f}")
with cols[3]:
    st.metric("Tổng CN May",value=f"{Workers/WD:,.0f}")
    st.metric("Tỉ lệ đi làm",value=f"{Attn:,.0%}")
with st.expander("Dữ liệu chi tiết"):
    df_ppc
    df_ppc.shape
st.markdown("---")
################

df_ppc['Short_Style'] = df_ppc['Style_P'].str[-4:]
df_SAH_pivot = df_ppc.pivot(index='Line',columns='WorkDate',values='SAH_P')
df_Style_pivot = df_ppc.pivot(index='Line',columns='WorkDate',values='Style_P')
df_Short_Style_pivot = df_ppc.pivot(index='Line',columns='WorkDate',values='Short_Style')
df_Hours_pivot = df_ppc.pivot(index='Line',columns='WorkDate',values='Hours_P')
df_Workers_pivot = df_ppc.pivot(index='Line',columns='WorkDate',values='Worker_P')
df_SAM_pivot = df_ppc.pivot(index='Line',columns='WorkDate',values='SAM')
df_Eff_pivot = df_ppc.pivot(index='Line',columns='WorkDate',values='Eff')

#Ghép các bảng pivot vào thành bảng chiều dùng làm customdata
customdata = np.dstack([df_SAH_pivot.values, df_Style_pivot.values,df_Short_Style_pivot.values,
                        df_Hours_pivot.values,df_Workers_pivot.values,df_SAM_pivot.values,df_Eff_pivot.values])
#config chung cho các biểu đồ plotly
config = {
    'displayModeBar': True,  # Hiển thị/thêm thanh công cụ
    'modeBarButtonsToRemove': ['zoom', 'select', 'lasso2d', 'resetScale', 'toImage'],  # Ẩn nút
    'displaylogo': False,  # Ẩn logo Plotly
    'modeBarButtonsToAdd': []  # Đảm bảo không thêm bất kỳ nút nào khác
}
#Vẽ biểu đồ nhiệt theo SAH
fig = px.imshow(
    df_SAH_pivot,
    color_continuous_scale= "RdYlGn",
    # color_continuous_midpoint=0.5,
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
num_row = df_SAH_pivot.shape[0]
row_hight = 35
min_height = 300
fig.update_layout(
    title = "SAH",
    xaxis_title = "Ngày",
    yaxis_title = "Chuyền",
    height = max(num_row * row_hight, min_height)
)
fig.update_traces(
    customdata=customdata,
    texttemplate='%{z:.0f}',
    textfont=dict(size=14),
    zmin=0,
    zmax=1,
    hovertemplate=(
        "Style: %{customdata[1]}<br>"
        "SAM: %{customdata[5]:.4f}<br>"
        "Eff: %{customdata[6]:.0%}<br>"
        "Hours: %{customdata[3]:.1f}<br>"
        "Worker: %{customdata[4]:.0f}<br>"
        # "<img src='%{customdata[2]}' style='width:100px;height:100px;'>"
    )
)
fig.update_layout(dragmode="pan")

st.plotly_chart(fig,use_container_width=True,key='heatmap4',config=config)

#Vẽ biểu đồ nhiệt theo Eff
fig = px.imshow(
    df_Eff_pivot,
    color_continuous_scale= "RdYlGn",
    # color_continuous_midpoint=0.5,
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
num_row = df_SAH_pivot.shape[0]
row_hight = 35
fig.update_layout(
    title = "Hiệu suất",
    xaxis_title = "Ngày",
    yaxis_title = "Chuyền",
    height = max(num_row * row_hight, min_height)
)
fig.update_traces(
    customdata=customdata,
    texttemplate='%{z:.0%}',
    textfont=dict(size=14),
    zmin=0,
    zmax=1,
    hovertemplate=(
        "Style: %{customdata[1]}<br>"
        "SAM: %{customdata[5]:.4f}<br>"
        "SAH: %{customdata[0]:.0f}<br>"
        "Hours: %{customdata[3]:.1f}<br>"
        "Worker: %{customdata[4]:.0f}<br>"
        # "<img src='%{customdata[2]}' style='width:100px;height:100px;'>"
    )
)
fig.update_layout(dragmode="pan")

st.plotly_chart(fig,use_container_width=True,key='heatmap0',config=config)

#Vẽ biểu đồ nhiệt theo short style
fig = px.imshow(
    df_Eff_pivot,
    color_continuous_scale= "RdYlGn",
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
num_row = df_Eff_pivot.shape[0]
row_hight = 35
fig.update_layout(
    title = "Style",
    xaxis_title = "Ngày",
    yaxis_title = "Chuyền",
    height = max(num_row * row_hight, min_height)
)
fig.update_traces(
    customdata = customdata,
    textfont=dict(size=14),
    zmin=0,
    zmax=1,
    hovertemplate=(
        "Style: %{customdata[1]}<br>"
        "SAM: %{customdata[5]:.4f}<br>"
        "Eff: %{customdata[6]:.0%}<br>"
        "Hours: %{customdata[3]:.1f}<br>"
        "Worker: %{customdata[4]:.0f}<br>"
    ),
    text=df_Short_Style_pivot.values, 
    texttemplate="%{text}"
)
fig.update_layout(dragmode="pan")

st.plotly_chart(fig,use_container_width=True,key='heatmap1',config=config)

#Vẽ biểu đồ nhiệt theo số giờ làm việc
fig = px.imshow(
    df_Hours_pivot,
    color_continuous_scale= "RdYlGn",
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
num_row = df_Eff_pivot.shape[0]
row_hight = 35
fig.update_layout(
    title = "Số giờ làm việc",
    xaxis_title = "Ngày",
    yaxis_title = "Chuyền",
    height = max(num_row * row_hight, min_height)
)
fig.update_traces(
    customdata = customdata,
    textfont=dict(size=14),
    zmin=0,
    zmax=1,
    hovertemplate=(
        "Style: %{customdata[1]}<br>"
        "SAM: %{customdata[5]:.4f}<br>"
        "Eff: %{customdata[6]:.0%}<br>"
        "Hours: %{customdata[3]:.1f}<br>"
        "Worker: %{customdata[4]:.0f}<br>"
    ),
    text=df_Hours_pivot.values, 
    texttemplate="%{text}"
)
fig.update_layout(dragmode="pan")

st.plotly_chart(fig,use_container_width=True,key='heatmap2',config=config)

#Vẽ biểu đồ nhiệt theo Worker
fig = px.imshow(
    df_Workers_pivot,
    color_continuous_scale= "RdYlGn",
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
num_row = df_Eff_pivot.shape[0]
row_hight = 35
fig.update_layout(
    title = "Số công nhân may",
    xaxis_title = "Ngày",
    yaxis_title = "Chuyền",
    height = max(num_row * row_hight, min_height)
)
fig.update_traces(
    customdata = customdata,
    textfont=dict(size=14),
    zmin=0,
    zmax=1,
    hovertemplate=(
        "Style: %{customdata[1]}<br>"
        "SAM: %{customdata[5]:.4f}<br>"
        "Eff: %{customdata[6]:.0%}<br>"
        "Hours: %{customdata[3]:.1f}<br>"
        "Worker: %{customdata[4]:.0f}<br>"
    ),
    text=df_Workers_pivot.values, 
    texttemplate="%{text}"
)
fig.update_layout(dragmode="pan")

st.plotly_chart(fig,use_container_width=True,key='heatmap3',config=config)

