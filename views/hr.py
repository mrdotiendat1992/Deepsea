import streamlit as st 
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go 
from datetime import date,datetime,timedelta
from load_data import get_data,exec_query
from io import BytesIO

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
    div[data-testid="stMetricValue"] {
        font-size: 20px; /* chỉnh kích thước chữ value */
    }
    div[data-testid="stMetricLabel"] {
        font-size: 14px; /* chỉnh kích thước chữ label */
    }
    div[data-testid="stMetricDelta"] {
        font-size: 12px; /* chỉnh kích thước chữ delta */
    }
    div.block-container{padding-top:1.5rem};
    </style>
    """,
    unsafe_allow_html=True
)
fty = ['NT1','NT2']
nha_may = st.sidebar.selectbox("Chọn nhà máy",options= fty, index= fty.index(st.session_state.factory))
st.markdown(f'<h1 class="centered-title">BÁO CÁO NHÂN SỰ ({nha_may})</h1>', unsafe_allow_html=True)

df_danglamviec = get_data(DB='HR',query=f"Select * from Danh_sach_CBCNV where trang_thai_lam_viec = N'Đang làm việc' and Factory = '{nha_may}'")
df_nghithaisan = get_data(DB='HR',query=f"Select * from Danh_sach_CBCNV where trang_thai_lam_viec = N'Nghỉ thai sản' and Factory = '{nha_may}'")
df_dilam = get_data(DB='HR',query=f"Select * from Cham_cong_sang where Factory = '{nha_may}' and Gio_vao is not null")
df_TGLV = get_data('HR',f"SELECT * FROM TONG_TGLV_DEEPSEA WHERE NHA_MAY = '{nha_may}'")
df_TGLV_so_CN_chuyen = get_data('HR',f"SELECT * FROM SO_CN_TONG_TGLV_THEO_CHUYEN_DEEPSEA WHERE NHA_MAY = '{nha_may}'")
df_thoi_vu_may = get_data('HR',f"Select count(*) as thoi_vu From Thoi_vu where BoPhan = 'May' and NhaMay ='{nha_may}'")
df_thoi_vu_ngoai = get_data('HR',f"Select count(*) as thoi_vu From Thoi_vu where BoPhan <> 'May' and NhaMay ='{nha_may}'")

thoi_vu_may = df_thoi_vu_may['thoi_vu'][0]
thoi_vu_ngoai = df_thoi_vu_ngoai['thoi_vu'][0]

#các tính toán cần thiết
tong_hc = df_danglamviec['MST'].count()
nghi_ts = df_nghithaisan['MST'].count()

hom_nay = f"{datetime.today(): %d/%m/%Y}"
st.subheader(f"Thông tin nhân sự ngày {hom_nay}")
cols = st.columns(5)
with cols[0]:
    st.info('Tổng số cán bộ công nhân viên hiện tại',icon= "👩‍⚕️" )
    col1,col2 = st.columns(2)
    with col1:      
        st.metric(label="Đang làm việc",value= f'{tong_hc:,.0f}')
    with col2: 
        st.metric(label="Nghỉ thai sản",value= f'{nghi_ts:,.0f}')
with cols[1]:
    cn_may = df_danglamviec[df_danglamviec['Headcount_category'] == "K"]['MST'].count()
    hc_ratio = ((tong_hc + thoi_vu_may + thoi_vu_ngoai)-(cn_may+thoi_vu_may))/(cn_may+thoi_vu_may)
    
    cn_may_tnc = cn_may_tnc = df_danglamviec[
        (df_danglamviec['Headcount_category'].notna() & (df_danglamviec['Headcount_category'] == "K")) | 
        (df_danglamviec['Section_code'].notna() & (df_danglamviec['Section_code'].str.contains("TNC")))
    ]['MST'].count()
    
    hc_ratio2 = (tong_hc-cn_may_tnc)/cn_may_tnc
    
    st.info('Công nhân may công nghiệp',icon= "👷" )
    col1,col2,col3 = st.columns(3)
    with col1:      
        st.metric(label="Công nhân may",value= f'{cn_may:,.0f}')
    with col2: 
        st.metric(label="Headcount ratio",value= f'{hc_ratio:,.2f}')
    with col3: 
        st.metric(label="Headcount ratio",value= f'{hc_ratio2:,.2f}')
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
with cols[4]:
    st.info('Công nhân thử việc nhóm 2',icon= "👶" )
    col1,col2 = st.columns(2)
    with col1:
        st.metric(label=f"May",value= f'{thoi_vu_may:,.0f}')
    with col2:
        st.metric(label=f"Khối ngoài",value= f'{thoi_vu_ngoai:,.0f}')
  
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
config = {
    'displayModeBar': True,  # Hiển thị/thêm thanh công cụ
    'modeBarButtonsToRemove': ['zoom', 'select', 'lasso2d', 'resetScale', 'toImage'],  # Ẩn nút
    'displaylogo': False,  # Ẩn logo Plotly
    'modeBarButtonsToAdd': []  # Đảm bảo không thêm bất kỳ nút nào khác
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
    fig.update_layout(dragmode="pan")

    st.plotly_chart(fig,use_container_width=True,config= config)
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
    fig.update_layout(dragmode="pan")

    st.plotly_chart(fig,use_container_width=True,config= config)
with cols[2]:
    df_danglamviec_dropna = df_danglamviec.dropna(subset=['Tinh_TP', 'Quan_huyen'])
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
    fig.update_layout(dragmode="pan")

    st.plotly_chart(fig,use_container_width=True,config= config)

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

pivot_df = df_total_hc_sew_filtered.pivot(index='NGAY', columns='Chi_so', values='HC_formated')

summary_df = pd.DataFrame(pivot_df)

# Hàm export Excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=True)
        worksheet = writer.sheets['Sheet1']

        for i, column in enumerate(df.reset_index().columns): 
            col_width = max(df.reset_index()[column].astype(str).map(len).max(), len(str(column))) + 2
            worksheet.set_column(i, i, col_width)

    return output.getvalue()

excel_bytes = to_excel(summary_df)

now_str = datetime.now().strftime("%d%m%Y%H%M%S")
# Nút tải file
st.download_button(
    label="📥 Tải Excel",
    data=excel_bytes,
    file_name=f"bien_dong_{now_str}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

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
fig.update_layout(dragmode="pan")

st.plotly_chart(fig,use_container_width=True,config= config)
# with st.expander("Dữ liệu biến động nhân sự chi tiết"):
#     # theo xưởng
#     ds_xuong = ['1P01','1P02','1P03','1P04','1P05','2P01','2P02','2P03','2P04','2P05']
#     df_RP_HR['Xưởng'] = df_RP_HR['XUONG'].apply(lambda x: x if x in ds_xuong else "Khác")
#     df_RP_HR_pivot = df_RP_HR.pivot_table(
#         index=['Xưởng', 'HC_CATEGORY'],
#         values=['TUYEN_MOI', 'NGHI_VIEC', 'THAI_SAN_DI_LAM_LAI', 'NGHI_THAI_SAN', 'DIEU_CHUYEN_DEN', 'DIEU_CHUYEN_DI'],
#         aggfunc='sum'
#     )
#     df_RP_HR_pivot['Tuyển mới'] = df_RP_HR_pivot['TUYEN_MOI']
#     df_RP_HR_pivot['Nghỉ việc'] = df_RP_HR_pivot['NGHI_VIEC'].apply(lambda x: -x)
#     df_RP_HR_pivot['Thai sản đi làm lại'] = df_RP_HR_pivot['THAI_SAN_DI_LAM_LAI']
#     df_RP_HR_pivot['Nghỉ thai sản'] = df_RP_HR_pivot['NGHI_THAI_SAN'].apply(lambda x: -x)
#     df_RP_HR_pivot['Điều chuyển đến'] = df_RP_HR_pivot['DIEU_CHUYEN_DEN']
#     df_RP_HR_pivot['Điều chuyển đi'] = df_RP_HR_pivot['DIEU_CHUYEN_DI'].apply(lambda x: -x)
#     df_RP_HR_pivot['+/-'] = df_RP_HR_pivot['Tuyển mới'] + df_RP_HR_pivot['Nghỉ việc'] + df_RP_HR_pivot['Thai sản đi làm lại'] + \
#         df_RP_HR_pivot['Nghỉ thai sản'] + df_RP_HR_pivot['Điều chuyển đến'] + df_RP_HR_pivot['Điều chuyển đi']
#     df_RP_HR_pivot = df_RP_HR_pivot.drop(['TUYEN_MOI', 'NGHI_VIEC', 'THAI_SAN_DI_LAM_LAI', 'NGHI_THAI_SAN', 'DIEU_CHUYEN_DEN', 'DIEU_CHUYEN_DI'], axis=1)
#     ## theo toàn nhà máy
#     df_RP_HR_pivot_factory = df_RP_HR.pivot_table(
#         index=['HC_CATEGORY'],
#         values=['TUYEN_MOI', 'NGHI_VIEC', 'THAI_SAN_DI_LAM_LAI', 'NGHI_THAI_SAN', 'DIEU_CHUYEN_DEN', 'DIEU_CHUYEN_DI'],
#         aggfunc='sum'
#     )
#     df_RP_HR_pivot_factory['Tuyển mới'] = df_RP_HR_pivot_factory['TUYEN_MOI']
#     df_RP_HR_pivot_factory['Nghỉ việc'] = df_RP_HR_pivot_factory['NGHI_VIEC'].apply(lambda x: -x)
#     df_RP_HR_pivot_factory['Thai sản đi làm lại'] = df_RP_HR_pivot_factory['THAI_SAN_DI_LAM_LAI']
#     df_RP_HR_pivot_factory['Nghỉ thai sản'] = df_RP_HR_pivot_factory['NGHI_THAI_SAN'].apply(lambda x: -x)
#     df_RP_HR_pivot_factory['Điều chuyển đến'] = df_RP_HR_pivot_factory['DIEU_CHUYEN_DEN']
#     df_RP_HR_pivot_factory['Điều chuyển đi'] = df_RP_HR_pivot_factory['DIEU_CHUYEN_DI'].apply(lambda x: -x)
#     df_RP_HR_pivot_factory['+/-'] = df_RP_HR_pivot_factory['Tuyển mới'] + df_RP_HR_pivot_factory['Nghỉ việc'] + df_RP_HR_pivot_factory['Thai sản đi làm lại'] + \
#         df_RP_HR_pivot_factory['Nghỉ thai sản'] + df_RP_HR_pivot_factory['Điều chuyển đến'] + df_RP_HR_pivot_factory['Điều chuyển đi']
#     df_RP_HR_pivot_factory = df_RP_HR_pivot_factory.drop(['TUYEN_MOI', 'NGHI_VIEC', 'THAI_SAN_DI_LAM_LAI', 'NGHI_THAI_SAN', 'DIEU_CHUYEN_DEN', 'DIEU_CHUYEN_DI'], axis=1)

#     # st.dataframe(df_RP_HR_pivot)
#     # st.dataframe(df_RP_HR_pivot_factory)
# ####
st.markdown("---")
st.subheader(f"Tổng thời gian làm việc {nha_may} (giờ) + số công nhân (CN May + TNC01)")
df_TGLV['NGAY'] = pd.to_datetime(df_TGLV['NGAY'])
df_TGLV = df_TGLV.query('NGAY >= @start_date and NGAY <= @end_date')
df_TGLV = df_TGLV.sort_values('NGAY',ascending=True)
df_TGLV['Tổng số giờ'] = df_TGLV['HC'] + df_TGLV['OT'] + df_TGLV['OT_CN']
###
df_TGLV_so_CN_chuyen['NGAY'] = pd.to_datetime(df_TGLV_so_CN_chuyen['NGAY'])
df_TGLV_so_CN_chuyen = df_TGLV_so_CN_chuyen.query('NGAY >= @start_date and NGAY <= @end_date')
df_TGLV_so_CN_chuyen = df_TGLV_so_CN_chuyen.sort_values(['NGAY','CHUYEN'],ascending=True)

cols = st.columns(5)
with cols[0]:
    st.info("Tổng TGLV")
    tong_TGLV = df_TGLV['Tổng số giờ'].sum()
    st.metric(f"{nha_may}",value=f"{tong_TGLV:,.0f}")
    if nha_may != 'NT1':
        tong_TGLV_BL1 = df_TGLV[df_TGLV['BLOCK'] == 'BL1']['Tổng số giờ'].sum()
        st.metric(f"Block 1",value=f"{tong_TGLV_BL1:,.0f}")
        tong_TGLV_BL2 = df_TGLV[df_TGLV['BLOCK'] == 'BL2']['Tổng số giờ'].sum()
        st.metric(f"Block 2",value=f"{tong_TGLV_BL2:,.0f}")
with cols[1]:
    st.info("Hành chính")
    tong_TGLV_hanh_chinh = df_TGLV['HC'].sum()
    st.metric(f"{nha_may}",value=f"{tong_TGLV_hanh_chinh:,.0f}")
    if nha_may != 'NT1':
        tong_TGLV_hanh_chinh_BL1 = df_TGLV[df_TGLV['BLOCK'] == 'BL1']['HC'].sum()
        st.metric(f"Block 1",value=f"{tong_TGLV_hanh_chinh_BL1:,.0f}")
        tong_TGLV_hanh_chinh_BL2 = df_TGLV[df_TGLV['BLOCK'] == 'BL2']['HC'].sum()
        st.metric(f"Block 2",value=f"{tong_TGLV_hanh_chinh_BL2:,.0f}")
with cols[2]:
    st.info("OT thường")
    tong_TGLV_OT = df_TGLV['OT'].sum()
    st.metric(f"{nha_may}",value=f"{tong_TGLV_OT:,.0f}")
    if nha_may != 'NT1':
        tong_TGLV_OT_BL1 = df_TGLV[df_TGLV['BLOCK'] == 'BL1']['OT'].sum()
        st.metric(f"Block 1",value=f"{tong_TGLV_OT_BL1:,.0f}")
        tong_TGLV_OT_BL2 = df_TGLV[df_TGLV['BLOCK'] == 'BL2']['OT'].sum()
        st.metric(f"Block 2",value=f"{tong_TGLV_OT_BL2:,.0f}")
with cols[3]:
    st.info("OT Chủ nhật")
    tong_TGLV_OT_CN = df_TGLV['OT_CN'].sum()
    st.metric(f"{nha_may}",value=f"{tong_TGLV_OT_CN:,.0f}")
    if nha_may != 'NT1':
        tong_TGLV_OT_CN_BL1 = df_TGLV[df_TGLV['BLOCK'] == 'BL1']['OT_CN'].sum()
        st.metric(f"Block 1",value=f"{tong_TGLV_OT_CN_BL1:,.0f}")
        tong_TGLV_OT_CN_BL2 = df_TGLV[df_TGLV['BLOCK'] == 'BL2']['OT_CN'].sum()
        st.metric(f"Block 2",value=f"{tong_TGLV_OT_CN_BL2:,.0f}")
with cols[4]:
    st.info("Số công nhân")
    df_TGLV_tong = df_TGLV.groupby(by=['NHA_MAY','NGAY']).agg({'SO_CN':'sum','HC' : 'sum'}).reset_index()
    so_CN = df_TGLV_tong[df_TGLV_tong['HC'] > 0]['SO_CN'].mean()
    st.metric(f"{nha_may}",value=f"{so_CN:,.0f}")
    if nha_may != 'NT1':
        so_CN_BL1 = df_TGLV[(df_TGLV['BLOCK'] == 'BL1') & (df_TGLV['HC'] > 0)]['SO_CN'].mean()
        st.metric(f"Block 1",value=f"{so_CN_BL1:,.0f}")
        so_CN_BL2 = df_TGLV[(df_TGLV['BLOCK'] == 'BL2') & (df_TGLV['HC'] > 0)]['SO_CN'].mean()
        st.metric(f"Block 2",value=f"{so_CN_BL2:,.0f}")      
with st.expander("Dữ liệu chi tiết theo ngày"):
    df_TGLV['HC'] = df_TGLV['HC'].apply(lambda x : f"{x:,.0f}")
    df_TGLV['OT'] = df_TGLV['OT'].apply(lambda x : f"{x:,.0f}")
    df_TGLV['OT_CN'] = df_TGLV['OT_CN'].apply(lambda x : f"{x:,.0f}")
    df_TGLV['Tổng số giờ'] = df_TGLV['Tổng số giờ'].apply(lambda x : f"{x:,.0f}")
    df_TGLV['NGAY'] = df_TGLV['NGAY'].dt.date
    st.markdown('Block')
    df_TGLV
    df_TGLV_so_CN_chuyen = df_TGLV_so_CN_chuyen.drop(columns=['NHA_MAY'])
    df_TGLV_so_CN_chuyen['NGAY'] = df_TGLV_so_CN_chuyen['NGAY'].dt.date
    st.markdown('Chuyền')
    df_TGLV_so_CN_chuyen

st.markdown("---")
st.subheader("Tuyển mới")
df_tuyen_moi = get_data("HR",
                        f"""
                        SELECT FACTORY AS NHA_MAY,MST,HO_TEN,NGAY_VAO,DEPARTMENT AS BO_PHAN,SECTION_CODE AS XUONG,LINE AS CHUYEN,
                        JOB_TITLE_VN AS CHUC_DANH,HEADCOUNT_CATEGORY AS KOIS,DATEDIFF(YEAR,NGAY_SINH,GETDATE()) AS TUOI,QUAN_HUYEN,TINH_TP
                        FROM DANH_SACH_CBCNV WHERE NGAY_VAO BETWEEN '{start_date}' AND '{end_date}' AND FACTORY = '{nha_may}'
                        """)
df_tuyen_moi['nhom_tuoi'] = df_tuyen_moi['TUOI'].apply(lambda x: "Trên 45 tuổi" if x > 45 else "36-45 tuổi" if x > 35 else "26-35 tuổi" if x > 25 else "18-25 tuổi")
df_tuyen_moi['Phan_loai'] = df_tuyen_moi['CHUC_DANH'] .apply(
    lambda x: "Công nhân may" if (
        (x == 'Công nhân may công nghiệp') or 
        (x == 'Công nhân thử việc may')
    ) else "Khác"
)
df_tuyen_moi['COUNT'] = 1
tong_tuyen_moi = df_tuyen_moi['MST'].count()
st.info(f"Tổng tuyển mới : {tong_tuyen_moi}")
cols = st.columns([1, 1, 1])
with cols[0]:
    # category_orders= ['18-25 tuổi', '26-35 tuổi', '36-45 tuổi', 'Trên 45 tuổi']
    # df_tuyen_moi['Phan_loai'] = pd.Categorical(df_tuyen_moi['Phan_loai'], categories=category_orders, ordered=True)
    fig = px.pie(
        df_tuyen_moi,
        color='Phan_loai',
        names= 'Phan_loai' ,
        title= "Tỉ lệ phân bổ theo công việc"     
    )
    fig.update_traces(
        textinfo = 'percent+value',
        textposition = 'inside',
        textfont = dict(size = 16)
    )
    fig.update_layout(dragmode="pan")

    st.plotly_chart(fig,use_container_width=True,key='pie1',config= config)
with cols[1]:
    fig = px.pie(
        df_tuyen_moi,
        color='nhom_tuoi',
        names= 'nhom_tuoi' ,
        title= "Tỉ lệ phân bổ theo nhóm tuổi" 
    )
    fig.update_traces(
        textinfo = 'percent',
        textposition = 'inside',
        textfont = dict(size = 16)
    )
    fig.update_layout(dragmode="pan")

    st.plotly_chart(fig,use_container_width=True,config= config)
    # st.write(df_tuyen_moi)
with cols[2]:
    df_tuyen_moi_groupby_chuc_danh = df_tuyen_moi.groupby(by=['CHUC_DANH','XUONG']).agg({'COUNT' : 'sum'}).reset_index()
    # st.dataframe(df_tuyen_moi_groupby_chuc_danh)
    fig = px.bar(
        df_tuyen_moi_groupby_chuc_danh,
        y ='CHUC_DANH',
        x= 'COUNT',
        color='XUONG',
        title= "Tổng số lượng tuyển mới theo chức danh",
        text= 'COUNT'
    )
    fig.update_yaxes(
        dtick= "D1"
    )
    fig.update_layout(
        xaxis_title = 'Số người tuyển mới',
        yaxis_title = 'Chức danh',
        legend_title_text = ""
    )
    fig.update_traces(
        textposition = 'outside',
        textfont = dict(color = 'white' , size = 16)
    )
    fig.update_layout(dragmode="pan")

    st.plotly_chart(fig,use_container_width=True,config= config)
with st.expander("Dữ liệu tuyển mới chi tiết"):
    st.dataframe(df_tuyen_moi)
###
st.markdown("---")
st.subheader("Nghỉ việc")
df_nghi_viec = get_data("HR",
                        f"""
                        SELECT FACTORY AS NHA_MAY,MST,HO_TEN,NGAY_VAO,NGAY_NGHI,DATEDIFF(DAY,NGAY_VAO,NGAY_NGHI) AS SO_NGAY,DEPARTMENT AS BO_PHAN,SECTION_CODE AS XUONG,LINE AS CHUYEN,
                        JOB_TITLE_VN AS CHUC_DANH,HEADCOUNT_CATEGORY AS KOIS,QUAN_HUYEN,TINH_TP
                        FROM DANH_SACH_CBCNV WHERE NGAY_NGHI BETWEEN '{start_date}' AND '{end_date}' AND FACTORY = '{nha_may}'
                        """)
df_nghi_viec['Thâm niên'] = df_nghi_viec['SO_NGAY'].apply(lambda x: "Trên 1 năm" if x > 365 else "6-12 tháng" if x > 182 else "3-6 tháng" if x > 91 else "1-3 tháng" if x >30 else "Dưới 1 tháng")
df_nghi_viec['Phan_loai'] = df_nghi_viec['CHUC_DANH'] .apply(
    lambda x: "Công nhân may" if (
        (x == 'Công nhân may công nghiệp') or 
        (x == 'Công nhân thử việc may')
    ) else "Khác"
)
df_nghi_viec['COUNT'] = 1
tong_nghi_viec = df_nghi_viec['MST'].count()
st.info(f"Tổng nghỉ việc : {tong_nghi_viec}")
cols = st.columns([1, 1, 1])
with cols[0]:
    fig = px.pie(
        df_nghi_viec,
        color='Phan_loai',
        names= 'Phan_loai' ,
        title= "Tỉ lệ phân bổ theo công việc" 
    )
    fig.update_traces(
        textinfo = 'percent+value',
        textposition = 'inside',
        textfont = dict(size = 16)
    )
    fig.update_layout(dragmode="pan")

    st.plotly_chart(fig,use_container_width=True,key='pie2',config= config)
with cols[1]:
    fig = px.pie(
        df_nghi_viec,
        color='Thâm niên',
        names= 'Thâm niên' ,
        title= "Tỉ lệ phân bổ theo thâm niên làm việc" 
    )
    fig.update_traces(
        textinfo = 'percent',
        textposition = 'inside',
        textfont = dict(size = 16)
    )
    fig.update_layout(dragmode="pan")

    st.plotly_chart(fig,use_container_width=True,config= config)

with cols[2]:
    df_nghi_viec_groupby_chuc_danh = df_nghi_viec.groupby(by=['CHUC_DANH','XUONG']).agg({'COUNT' : 'sum'}).reset_index()
    fig = px.bar(
        df_nghi_viec_groupby_chuc_danh,
        y ='CHUC_DANH',
        x= 'COUNT',
        color='XUONG',
        title= "Tổng số lượng nghỉ việc theo chức danh",
        text= 'COUNT'
    )
    fig.update_yaxes(
        dtick= "D1"
    )
    fig.update_layout(
        xaxis_title = 'Số người nghỉ việc',
        yaxis_title = 'Chức danh',
        legend_title_text = ""
    )
    fig.update_traces(
        textposition = 'outside',
        textfont = dict(color = 'white' , size = 16)
    )
    fig.update_layout(dragmode="pan")

    st.plotly_chart(fig,use_container_width=True,config= config)
with st.expander("Dữ liệu nghỉ việc chi tiết"):
    st.dataframe(df_nghi_viec)
# ###