import streamlit as st 
import pandas as pd
from load_data import get_data
from datetime import datetime,date,timedelta
import plotly.express as px
import numpy as np
import streamlit.components.v1 as components

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
st.markdown(f'<h1 class="centered-title">BÁO CÁO DẬP THẺ ETS HÀNG GIỜ</h1>', unsafe_allow_html=True)

fty = ['NT1','NT2', 'NT3']
sel_fty = st.sidebar.selectbox("Chọn nhà máy:",options = fty,index=fty.index(st.session_state.factory))

df_hourly = get_data("DW",f"SELECT * FROM ETS_DAP_THE_HANG_GIO WHERE 'NT' + LEFT(LINE,1) = '{sel_fty}' ORDER BY Time_Stamp")
df_daily = df_hourly.copy()
df_hourly['Time'] = df_hourly['Time_Stamp'].apply(lambda x: f"{x:%H:%M}") 
df_hourly['WorkDate'] = pd.to_datetime(df_hourly['WorkDate'])
df_hourly['Time'].replace(to_replace='12:30',value='13:30',inplace=True)

min_date = df_hourly['WorkDate'].min()
today = date.today() if date.today().day >1 else date.today() - timedelta(days=1)
first_day_of_month =  today.replace(day=1)
start_date = st.sidebar.date_input(label="Từ ngày:",value= first_day_of_month)

max_date = df_hourly['WorkDate'].max()
end_date = st.sidebar.date_input(label="Đến ngày:", value= max_date)

st.subheader("Báo cáo hàng giờ hôm nay")
st.markdown("[Link báo cáo NT1](http://10.0.0.252:82)")
st.markdown("[Link báo cáo NT2](http://172.16.60.98:82)")

st.markdown("---")
st.subheader("Bảng theo dõi dập thẻ ETS hàng giờ")
date_sel = st.date_input("Chọn ngày:",value=max_date,min_value=min_date,max_value=max_date)
date_sel = pd.to_datetime(date_sel)
df_hourly = df_hourly[df_hourly['WorkDate'] == date_sel]

df_hourly_groupby = df_hourly.groupby(by=['WorkDate','Line','Time']).agg({'Qty':'sum','SAH':'sum','Style' : 'max'}).reset_index()
# df_hourly_groupby
df_hourly_pivot = df_hourly_groupby.pivot(index='Line',columns='Time',values='SAH')
# df_hourly_pivot
df_hourly_pivot_style = df_hourly_groupby.pivot(index='Line',columns='Time',values='Style')
df_hourly_pivot_qty = df_hourly_groupby.pivot(index='Line',columns='Time',values='Qty')
# df_hourly_groupby
# df_hourly_pivot
# df_hourly_pivot_style
# df_hourly_pivot_qty
customdata = np.dstack([df_hourly_pivot_style.values, df_hourly_pivot_qty.values])
#config chung cho các biểu đồ plotly
config = {
    'displayModeBar': True,  # Hiển thị/thêm thanh công cụ
    'modeBarButtonsToRemove': ['zoom', 'select', 'lasso2d', 'resetScale', 'toImage'],  # Ẩn nút
    'displaylogo': False,  # Ẩn logo Plotly
    'modeBarButtonsToAdd': []  # Đảm bảo không thêm bất kỳ nút nào khác
}
fig = px.imshow(
    df_hourly_pivot,
    color_continuous_scale="RdYlGn",
    text_auto=".0f"
)
num_row = df_hourly_pivot.shape[0]
row_hight = 50
fig.update_layout(
    title = "SAH",
    xaxis_title = "Mốc thời gian",
    yaxis_title = "Chuyền",
    height = num_row * row_hight
)
fig.update_traces(
    customdata=customdata,
    textfont=dict(size=14),
    hovertemplate=(
        "Style: %{customdata[0]}<br>"
        "Qty: %{customdata[1]:.0f}"
    )
)
fig.update_layout(dragmode="pan")

st.plotly_chart(fig,use_container_width=True,key='heatmap1',config=config)

with st.expander("Dữ liệu chi tiết"):
    df_hourly
    
st.markdown("---")
df_daily['WorkDate'] = pd.to_datetime(df_daily['WorkDate'])
df_daily = df_daily.query("WorkDate >= @start_date and WorkDate <= @end_date")
df_daily['Time_Stamp']=df_daily['Time_Stamp'].apply(lambda x: f"{x:%H:%M}")
df_daily['Time_Stamp'].replace(to_replace="12:30",value="13:30",inplace=True)
df_daily_line_wd = df_daily.groupby(by=['WorkDate','Line','Time_Stamp']).agg({'Qty':'sum'}).reset_index()
# df_daily_line_wd
df_daily_groupby = df_daily_line_wd.groupby(by=['WorkDate','Line']).agg({'Qty':'count'}).reset_index()
# df_daily_groupby
df_daily_pivot = df_daily_groupby.pivot(index='Line',columns='WorkDate',values='Qty')
fig = px.imshow(
    df_daily_pivot,
    color_continuous_scale= "RdYlGn",
    text_auto=True
)
num_row = df_daily_pivot.shape[0]
row_hight = 50
fig.update_layout(
    title = "Số lần dập thẻ theo ngày",
    xaxis_title = "Ngày",
    yaxis_title = "Chuyền",
    height = num_row * row_hight
)
fig.update_xaxes(
    dtick = 'D1',
    tickformat = '%d/%m',
    tickfont = dict(size = 12)
)
fig.update_yaxes(
    tickfont = dict(size = 14),
    dtick = 'D1'
)
fig.update_layout(dragmode="pan")

st.plotly_chart(fig,use_container_width=True,key='heatmap2',config=config)
with st.expander("Dữ liệu chi tiết"):
    df_daily_pivot
st.markdown("---")
df_total = df_daily_groupby.groupby(by='Line').agg({'Qty':'sum'}).reset_index()
so_ngay = df_daily_groupby['WorkDate'].nunique()
df_total['Số ngày'] = so_ngay
df_total['Số lần/ngày'] = df_total['Qty']/df_total['Số ngày']
df_total['Số lần/ngày_formated'] = df_total['Số lần/ngày'].apply(lambda x: f"{x:,.1f}")
df_total=df_total.rename(columns={'Qty' : 'Tổng số lần dập thẻ'})

fig=px.bar(
    data_frame=df_total.sort_values('Line',ascending=False),
    y= 'Line',
    x='Số lần/ngày',
    text='Số lần/ngày_formated',
    hover_data= {
        'Tổng số lần dập thẻ' : True,
        'Số ngày' : True,
        'Số lần/ngày' : False,
        'Line' : False,
        'Số lần/ngày_formated' : False
    }
)
row_num = df_total.shape[0]
fig.update_layout(
    xaxis_title = "Chuyền",
    yaxis_title = "Số lần dập thẻ trung bình",
    title = "Số lần dập thẻ trung bình theo chuyền",
    height = row_num * 50
)
fig.update_traces(
    textposition = 'outside'
)
fig.update_layout(dragmode="pan")

st.plotly_chart(fig,use_container_width=True,config=config)
with st.expander("Dữ liệu chi tiết"):
    df_total