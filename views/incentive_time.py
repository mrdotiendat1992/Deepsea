import streamlit as st 
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go 
from datetime import date,datetime
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
fty =['NT1','NT2']
nha_may = st.sidebar.multiselect("Chọn nhà máy",options=fty,default=fty)
reports = ['Công nhân Cắt','Công nhân may','Công nhân QC1','Công nhân Là','Công nhân QC2','Công nhân đóng gói','Công nhân NDC','Công nhân phụ','Quản lý']
bao_cao = st.sidebar.selectbox("Chọn báo cáo",options= reports,index=0)

st.markdown(f'<h1 class="centered-title">BÁO CÁO THƯỞNG NĂNG SUẤT THEO CÁC THÁNG</h1>', unsafe_allow_html=True)
st.markdown(f'<h1 class="centered-title">({bao_cao})</h1>', unsafe_allow_html=True)
#Config chung cho plotly chart
config = {
    'displayModeBar': True,  # Hiển thị/thêm thanh công cụ
    'modeBarButtonsToRemove': ['zoom', 'select', 'lasso2d', 'resetScale', 'toImage'],  # Ẩn nút
    'displaylogo': False,  # Ẩn logo Plotly
    'modeBarButtonsToAdd': []  # Đảm bảo không thêm bất kỳ nút nào khác
}

def drawPlot(df, nhom):
    df['XUONG'] = df['CHUYEN'].apply(lambda x: (x[:1] + 'NDC') if 'NDC' in x \
        else (x[:1] + 'TNC') if 'TNC' in x \
        else (x[:1] + 'P0' + x[1:2]))
    df["THANG"] = df["THANG"].astype(int)
    
    nam = df['NAM'].sort_values(ascending=False).unique()
    sel_nam = st.sidebar.selectbox("Chọn năm",options=nam)
    so_thang_min = int(df[(df['NAM']==sel_nam)]['THANG'].min())
    so_thang_max = int(df[(df['NAM']==sel_nam)]['THANG'].max())
    sel_so_thang_min, sel_so_thang_max = st.sidebar.slider("Chọn khoảng tháng",min_value=so_thang_min, max_value=so_thang_max, value=(so_thang_min, so_thang_max), step=1 )
    df = df.query("NAM == @sel_nam and THANG >= @sel_so_thang_min and THANG <= @sel_so_thang_max")
    
    df_list = [df[df['NHA_MAY'] == fac] for fac in nha_may] 
    cols = st.columns(len(nha_may))
    
    max_thang = int(max(df["THANG"].max() for df in df_list)) + 1
    min_thang = int(max(df["THANG"].min() for df in df_list)) - 1

    max_thuong = max(df.groupby(by=['THANG'])["TONG_THUONG"].sum().max() for df in df_list) * 1.2
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_fac = df_list[i]
            
            df_tb_thuong = df_fac.groupby(by=['THANG']).agg({'TONG_THUONG' : 'sum'}).reset_index()
            df_tb_thuong['TB_TIEN_THUONG'] = df_tb_thuong['TONG_THUONG'].apply(lambda x: f"{x/1_000_000:,.1f} triệu")

            fig = px.line(df_tb_thuong, x="THANG", y="TONG_THUONG", text="TB_TIEN_THUONG")
            
            fig.update_layout(
                title = f'Tổng tiền thưởng nhóm {nhom} theo tháng {fac}',
                xaxis_title = 'Tháng',
                yaxis_title = 'Tổng tiền thưởng'
            )
            fig.update_traces(
                textposition = 'top center'
            )
            fig.update_yaxes(
                range = [0, max_thuong]
            )
            fig.update_xaxes(
                type="linear",
                tickmode="linear", 
                dtick=1,
                range=[min_thang, max_thang]
            )
            fig.update_layout(dragmode="pan")
            
            st.plotly_chart(fig,use_container_width=True,key=f'line1{fac}',config = config)

    max_tb_thuong = max(df.groupby(by=['THANG'])["TONG_THUONG"].mean().max() for df in df_list) * 1.2
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_fac = df_list[i]
            
            df_tb_thuong = df_fac.groupby(by=['THANG']).agg({'TONG_THUONG' : 'mean'}).reset_index()
            df_tb_thuong['Trung bình tiền thưởng'] = df_tb_thuong['TONG_THUONG'].apply(lambda x: f"{x/1_000_000:,.1f} triệu")

            fig = px.line(df_tb_thuong, x="THANG", y="TONG_THUONG", text="Trung bình tiền thưởng")
            
            fig.update_layout(
                title = f'Trung bình tiền thưởng nhóm {nhom} theo tháng {fac}',
                xaxis_title = 'Tháng',
                yaxis_title = 'Trung bình tiền thưởng'
            )
            fig.update_traces(
                textposition = 'top center'
            )
            fig.update_yaxes(
                range = [0, max_tb_thuong]
            )
            fig.update_xaxes(
                type="linear",
                tickmode="linear", 
                dtick=1,
                range=[min_thang, max_thang]
            )
            fig.update_layout(dragmode="pan")
            
            st.plotly_chart(fig,use_container_width=True,key=f'line2{fac}',config = config)

if bao_cao == 'Công nhân Cắt':
    df = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                           TGLV as TONG_TGLV,TONG_THUONG,SO_NGAY,N'Cắt' as NHOM
                           FROM TONG_HOP_TGLV_TONG_THUONG_CN_CAT WHERE NHA_MAY in ({', '.join(f'\'{item}\'' for item in nha_may)})
                           """)
    
    drawPlot(df, 'Cắst')

if bao_cao == 'Công nhân may':
    df = get_data(DB='INCENTIVE',query=f"""
                        SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                        TONG_TGLV,TONG_THUONG,SO_NGAY,'May' as NHOM
                        FROM TONG_HOP_TIEN_THUONG_HIEU_SUAT_CN_MAY WHERE NHA_MAY in ({', '.join(f'\'{item}\'' for item in nha_may)}) 
                        """)
    drawPlot(df, 'May')

if bao_cao == 'Công nhân QC1':
    df = get_data(DB='INCENTIVE',query=f"""
                        SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                        TONG_TGLV,TONG_THUONG,SO_NGAY,N'QC1' as NHOM
                        FROM TONG_HOP_TIEN_THUONG_HIEU_SUAT_TGLV_QC1 WHERE NHA_MAY in ({', '.join(f'\'{item}\'' for item in nha_may)})
                        """)
    drawPlot(df, 'QC1')

if bao_cao == 'Công nhân Là':
    df = get_data(DB='INCENTIVE',query=f"""
                        SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                        TONG_TGLV,TONG_THUONG,SO_NGAY,N'Là' as NHOM
                        FROM TONG_HOP_TIEN_THUONG_HIEU_SUAT_TGLV_LA WHERE NHA_MAY in ({', '.join(f'\'{item}\'' for item in nha_may)})
                        """)
    drawPlot(df, 'Là')

if bao_cao == 'Công nhân QC2':
    df = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                           TONG_TGLV,TONG_THUONG,SO_NGAY,N'QC2' as NHOM
                           FROM TONG_HOP_TIEN_THUONG_HIEU_SUAT_TGLV_QC2 WHERE NHA_MAY in ({', '.join(f'\'{item}\'' for item in nha_may)})
                           """)
    drawPlot(df, 'QC2')

if bao_cao == 'Công nhân đóng gói':
    df = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                           TGLV AS TONG_TGLV,TONG_THUONG,SO_NGAY,N'Hoàn thiện' as NHOM
                           FROM TONG_HOP_TGLV_TONG_THUONG_CN_DONG_GOI WHERE NHA_MAY in ({', '.join(f'\'{item}\'' for item in nha_may)})
                           """)
    drawPlot(df, 'Đóng gói')

if bao_cao == 'Công nhân NDC':
    df = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                           TGLV AS TONG_TGLV,TONG_THUONG,SO_NGAY,N'NDC' as NHOM
                           FROM TONG_HOP_TGLV_TONG_THUONG_CN_NDC WHERE NHA_MAY in ({', '.join(f'\'{item}\'' for item in nha_may)})
                           """)
    drawPlot(df, 'NDC')

if bao_cao == 'Công nhân phụ':
    df = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                           TGLV AS TONG_TGLV,TONG_THUONG,SO_NGAY,N'CN Phụ' as NHOM
                           FROM TONG_HOP_TGLV_TONG_THUONG_CN_PHU WHERE NHA_MAY in ({', '.join(f'\'{item}\'' for item in nha_may)})
                           """)
    drawPlot(df, 'Phụ')

if bao_cao == 'Quản lý':
    df = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                           TGLV AS TONG_TGLV,TONG_THUONG,SO_NGAY,N'Quản lý' as NHOM
                           FROM TONG_HOP_TGLV_TONG_THUONG_QUAN_LY WHERE NHA_MAY in ({', '.join(f'\'{item}\'' for item in nha_may)})
                           """)
    drawPlot(df, 'Quản lý')