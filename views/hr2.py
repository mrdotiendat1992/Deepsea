import streamlit as st 
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go 
from datetime import date,datetime,timedelta
from load_data import get_data

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
nha_may = st.sidebar.selectbox("Chọn nhà máy",options=['NT1','NT2'])
st.markdown(f'<h1 class="centered-title">BÁO CÁO NHÂN SỰ ({nha_may})</h1>', unsafe_allow_html=True)

df_danglamviec = get_data(DB='HR',query=f"Select * from Danh_sach_CBCNV where trang_thai_lam_viec = N'Đang làm việc' and Factory = '{nha_may}'")
df_nghithaisan = get_data(DB='HR',query=f"Select * from Danh_sach_CBCNV where trang_thai_lam_viec = N'Nghỉ thai sản' and Factory = '{nha_may}'")
df_dilam = get_data(DB='HR',query=f"Select * from Cham_cong_sang where Factory = '{nha_may}' and Gio_vao is not null")

#các tính toán cần thiết
tong_hc = df_danglamviec['MST'].count()
nghi_ts = df_nghithaisan['MST'].count()

hom_nay = f"{datetime.today(): %d/%m/%Y}"
st.subheader(f"Thông tin nhân sự ngày {hom_nay}")
cols = st.columns(4)
with cols[0]:
    st.info('Tổng số cán bộ công nhân viên hiện tại',icon= "👩‍⚕️" )
    col1,col2 = st.columns(2)
    with col1:      
        st.metric(label="Đang làm việc",value= f'{tong_hc:,.0f}')
    with col2: 
        st.metric(label="Nghỉ thai sản",value= f'{nghi_ts:,.0f}')
with cols[1]:
    cn_may = df_danglamviec[df_danglamviec['Headcount_category'] == "K"]['MST'].count()
    hc_ratio = (tong_hc-cn_may)/cn_may
    st.info('Công nhân may công nghiệp',icon= "👷" )
    col1,col2 = st.columns(2)
    with col1:      
        st.metric(label="Công nhân may",value= f'{cn_may:,.0f}')
    with col2: 
        st.metric(label="Headcount ratio",value= f'{hc_ratio:,.2f}')
with cols[2]:
    cn_tnc00 = df_danglamviec[df_danglamviec['Line'].str.contains('TNC00', case=False, na=False)]['MST'].count()
    cn_tnc01 = df_danglamviec[df_danglamviec['Line'].str.contains('TNC01', case=False, na=False)]['MST'].count()
    st.info('Công nhân may đang đào tạo',icon= "👶" )
    col1,col2 = st.columns(2)
    with col1:      
        st.metric(label="Thử việc may",value= f'{cn_tnc00:,.0f}')
    with col2: 
        st.metric(label="Có tay nghề",value= f'{cn_tnc01:,.0f}')
with cols[3]:
    cn_dilam = df_dilam['Gio_vao'].count()
    cn_may_dilam = df_dilam[(df_dilam['Chuc_vu'] == "Công nhân may công nghiệp") & (~df_dilam['Chuyen_to'].str.contains('TNC01'))]['Gio_vao'].count()
    st.info('Công nhân đi làm hôm nay',icon= "🏃" )
    col1,col2 = st.columns(2)
    with col1:      
        st.metric(label=f"Toàn nhà máy ({cn_dilam/tong_hc:,.0%})",value= f'{cn_dilam:,.0f}')
    with col2: 
        st.metric(label=f"Công nhân may ({cn_may_dilam/cn_may:,.0%})",value= f'{cn_may_dilam:,.0f}')

today = date.today() 
df_danglamviec['Ngay_sinh'] = pd.to_datetime(df_danglamviec['Ngay_sinh'],format='%Y-%m-%d')
df_danglamviec['Tuổi']= df_danglamviec['Ngay_sinh'].apply(lambda x: today.year - x.year)
df_danglamviec['Gioi_tinh'] = df_danglamviec['Gioi_tinh'].apply(lambda x: 'Nữ' if x == 'nữ' or x == '' else x)
df_danglamviec['Ngay_vao'] = pd.to_datetime(df_danglamviec['Ngay_vao'],format='%Y-%m-%d')
df_danglamviec['Số ngày'] = (pd.Timestamp(date.today()) - df_danglamviec['Ngay_vao']).dt.days
df_danglamviec['Số tháng'] = (pd.Timestamp(date.today()) - df_danglamviec['Ngay_vao']).dt.days//30
df_danglamviec['Thâm niên'] = df_danglamviec['Số ngày'].apply(lambda x: "Trên 1 năm" if x > 365 else "6-12 tháng" if x > 182 else "3-6 tháng" if x > 91 else "Dưới 3 tháng")
df_danglamviec['count'] = 1
categories=['K','O','I','S']

color_map = {
    'K': 'light blue', 
    'O': 'blue',
    'I': 'orange',
    'S': 'red'
}
# st.dataframe(df_danglamviec)
cols = st.columns(3)
with cols[0]:
    fig = px.histogram(
        df_danglamviec,
        x='Tuổi',
        text_auto=True,
        color='Headcount_category',
        category_orders={'Headcount_category': categories},
        color_discrete_map=color_map
    )
    fig.update_layout(
        title = "Phân bổ công nhân theo độ tuổi và Headcout category",
        legend_title_text = "",
        yaxis_title = "Số người"
    )
    st.plotly_chart(fig,use_container_width=True)
with cols[1]:
    fig = px.sunburst(
        df_danglamviec,
        path= ['Headcount_category','Thâm niên'],
        values='count',
        color= 'Headcount_category',
        color_discrete_map=color_map
    )
    fig.update_layout(
        title = "Phân bổ theo Heacount category và thâm niên",
    ) 
    st.plotly_chart(fig,use_container_width=True)
with cols[2]:
    df_danglamviec_dropna = df_danglamviec.dropna(subset=['Tinh_TP', 'Quan_huyen'])
    # df_danglamviec_dropna['Tinh_TP'] = df_danglamviec_dropna['Tinh_TP'].replace({'Tỉnh Nghệ An' : 'Nghệ An',' Nghệ An' : 'Nghệ An'})
    df_danglamviec_dropna['Tinh_TP'] = df_danglamviec_dropna['Tinh_TP'].str.replace(r'Tỉnh|tỉnh','',regex=True)
    df_danglamviec_dropna['Quan_huyen'] = df_danglamviec_dropna['Quan_huyen'].str.replace(r'Huyện|huyện','',regex=True)
    df_danglamviec_dropna['Tinh_TP'] = df_danglamviec_dropna['Tinh_TP'].str.strip()
    df_danglamviec_dropna['Quan_huyen'] = df_danglamviec_dropna['Quan_huyen'].str.strip()
    fig = px.treemap(
        df_danglamviec_dropna,
        path= ['Tinh_TP','Quan_huyen','Phuong_xa'],
        values ='count'             
    )
    fig.update_layout(
        title = "Phân bổ theo địa lý",
    ) 
    st.plotly_chart(fig,use_container_width=True)
st.markdown("---")
st.subheader("Xu hướng biến động nhân sự")
df_RP_HR = get_data(DB='HR',query=f"Select * from RP_HR_TONG_HOP_15_PHUT where NHA_MAY = '{nha_may}' AND NGAY > = '2024-09-01'")
df_total_hc = df_RP_HR.groupby(by='NGAY').agg({'HC' : 'sum'}).reset_index()
df_total_hc['Chi_so'] = 'Tổng HC'
df_total_sew = df_RP_HR[df_RP_HR['HC_CATEGORY'] == 'K'].groupby(by='NGAY').agg({'HC' : 'sum'}).reset_index()
df_total_sew['Chi_so'] = 'Tổng CN May'

df_total_hc_sew = pd.concat([df_total_hc, df_total_sew], ignore_index=True)
df_total_hc_sew = df_total_hc_sew[df_total_hc_sew['HC'] > 0]
df_total_hc_sew['HC_formated'] = df_total_hc_sew['HC'].apply(lambda x: f"{x:,.0f}")
# sidebar chọn khoảng ngày
df_total_hc_sew['NGAY'] = pd.to_datetime(df_total_hc_sew['NGAY'], format='%Y-%m-%d')
df_total_hc_sew['NGAY'] = df_total_hc_sew['NGAY'].dt.date
min_date = df_total_hc_sew['NGAY'].min()
today = date.today() if date.today().day > 1 else date.today() - timedelta(days=1)
first_day_of_month =  today.replace(day=1)
start_date = st.sidebar.date_input(label="Từ ngày:",value= first_day_of_month)

max_date = df_total_hc_sew['NGAY'].max()
end_date = st.sidebar.date_input(label="Đến ngày:", value= max_date)
df_total_hc_sew_filtered = df_total_hc_sew.query('NGAY >= @start_date and NGAY <= @end_date')
fig = px.line(
    df_total_hc_sew_filtered,
    x= 'NGAY',
    y='HC',
    color='Chi_so',
    text = 'HC_formated'
)
fig.update_layout(
    title = 'Tổng số CBCNV và tổng số công nhân may theo ngày',
    xaxis_title = 'Ngày',
    yaxis_title = 'Số người',
    legend_title_text = "",
)
fig.update_xaxes(
    dtick = 'D1',
    tickformat = '%d/%m'
)
max_hc = df_total_hc['HC'].max() * 1.1
fig.update_yaxes(
    range = [0,max_hc]
)
fig.update_traces(
    textposition = 'top center',
    textfont = dict(size = 14)
)
st.plotly_chart(fig,use_container_width=True)
# ####
st.markdown("---")
st.subheader("Tuyển mới và nghỉ việc")
#tuyển mới
df_tuyen_moi = df_RP_HR.groupby(by='NGAY').agg({'TUYEN_MOI' : 'sum'}).reset_index()
df_tuyen_moi['Chi_so'] = 'Tổng tuyển mới'
df_tuyen_moi_sew = df_RP_HR[(df_RP_HR['HC_CATEGORY'] == 'I') & (df_RP_HR['CHUYEN'].str.contains('TNC',case=True))].groupby(by='NGAY').agg({'TUYEN_MOI' : 'sum'}).reset_index()
df_tuyen_moi_sew['Chi_so'] = 'Tổng CN May tuyển mới'

df_tuyen_moi_concat = pd.concat([df_tuyen_moi, df_tuyen_moi_sew], ignore_index=True)
df_tuyen_moi_concat['NGAY'] = pd.to_datetime(df_tuyen_moi_concat['NGAY'])
df_tuyen_moi_concat_filtered = df_tuyen_moi_concat.query('NGAY >= @start_date and NGAY <= @end_date')
# st.write(df_tuyen_moi_concat)
#vẽ biểu đồ tuyển dụng
fig = px.line(
    df_tuyen_moi_concat_filtered,
    x= 'NGAY',
    y='TUYEN_MOI',
    color='Chi_so',
    text = 'TUYEN_MOI'
)
fig.update_layout(
    title = 'Tuyển mới theo ngày',
    xaxis_title = 'Ngày',
    yaxis_title = 'Số người',
    legend_title_text = "",
)
fig.update_xaxes(
    dtick = 'D1',
    tickformat = '%d/%m'
)
max_tuyen_moi = df_tuyen_moi_concat_filtered['TUYEN_MOI'].max() * 1.1
fig.update_yaxes(
    range = [0,50]
)
fig.update_traces(
    textposition = 'top center',
    textfont = dict(size = 14)
)
st.plotly_chart(fig,use_container_width=True,key='tuyen_moi')
###
#nghỉ việc
df_nghi_viec = df_RP_HR.groupby(by='NGAY').agg({'NGHI_VIEC' : 'sum'}).reset_index()
df_nghi_viec['Chi_so'] = 'Tổng nghỉ việc'
df_nghi_viec_sew = df_RP_HR[(df_RP_HR['HC_CATEGORY'] == 'K')|((df_RP_HR['HC_CATEGORY'] == 'I') & (df_RP_HR['CHUYEN'].str.contains('TNC',case=True)))].groupby(by='NGAY').agg({'NGHI_VIEC' : 'sum'}).reset_index()
df_nghi_viec_sew['Chi_so'] = 'Tổng CN May nghỉ việc'

df_nghi_viec_concat = pd.concat([df_nghi_viec, df_nghi_viec_sew], ignore_index=True)
df_nghi_viec_concat['NGAY'] = pd.to_datetime(df_nghi_viec_concat['NGAY'])
df_nghi_viec_concat_filtered = df_nghi_viec_concat.query('NGAY >= @start_date and NGAY <= @end_date')
# st.write(df_nghi_viec_concat)
#vẽ biểu đồ tuyển dụng
fig = px.line(
    df_nghi_viec_concat_filtered,
    x= 'NGAY',
    y='NGHI_VIEC',
    color='Chi_so',
    text = 'NGHI_VIEC'
)
fig.update_layout(
    title = 'Nghỉ việc theo ngày',
    xaxis_title = 'Ngày',
    yaxis_title = 'Số người',
    legend_title_text = "",
)
fig.update_xaxes(
    dtick = 'D1',
    tickformat = '%d/%m'
)
max_nghi_viec = df_nghi_viec_concat_filtered['NGHI_VIEC'].max() * 1.1
fig.update_yaxes(
    range = [0,50]
)
fig.update_traces(
    textposition = 'top center',
    textfont = dict(size = 14)
)
st.plotly_chart(fig,use_container_width=True,key='nghi_viec')

