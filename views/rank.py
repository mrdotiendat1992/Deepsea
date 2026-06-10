import streamlit as st 
from streamlit_js_eval import streamlit_js_eval
from load_data import get_data
import pandas as pd
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
st.markdown(f'<h1 class="centered-title">BẢNG XẾP HẠNG</h1>', unsafe_allow_html=True)
# st.markdown("---")
rp_type = st.sidebar.radio("Xếp hạng theo",options=['Hiệu suất','Tiền thưởng','Tỉ lệ lỗi'])
chuyen_cong_nhan = st.sidebar.radio("Chuyền/Công nhân",options=['Xưởng','Chuyền','Công nhân'])
ds_nha_may = ['NT1','NT2']
nha_may = st.sidebar.multiselect("Chọn nhà máy",options=ds_nha_may,default=ds_nha_may)
### Lấy dữ liệu từ SQL nhóm theo chuyền
df_chuyen = get_data("INCENTIVE","""
                     SELECT 'NT' + LEFT(Line,1) as NHA_MAY,WorkDate as NGAY,Line as CHUYEN,
                     SAH,Total_hours as TGLV,TONG_THUONG
                     FROM THUONG_NHOM_MAY_HANG_NGAY 
                     WHERE WorkDate < CAST(GETDATE() AS DATE)
                     ORDER BY WORKDATE,LINE
                     """)

df_chuyen['NGAY'] = pd.to_datetime(df_chuyen['NGAY'], format='%Y-%m-%d')
df_chuyen['NAM'] = df_chuyen['NGAY'].dt.year.astype(str)
df_chuyen['THANG'] = df_chuyen['NGAY'].dt.month.astype(str).str.zfill(2)
ds_nam = sorted(df_chuyen['NAM'].unique(),reverse =True)
nam = st.sidebar.selectbox("Chọn năm",options=ds_nam)
ds_thang = sorted(df_chuyen[df_chuyen['NAM'] == nam]['THANG'].unique(),reverse=True)
thang = st.sidebar.selectbox("Chọn tháng",options=ds_thang)
ngay_min = df_chuyen[(df_chuyen['NAM'] == nam) & (df_chuyen['THANG'] == thang)]['NGAY'].min()
ngay_max = df_chuyen[(df_chuyen['NAM'] == nam) & (df_chuyen['THANG'] == thang)]['NGAY'].max()
tu_ngay = st.sidebar.date_input("Từ ngày",value=ngay_min)
den_ngay = st.sidebar.date_input("Đến ngày",value=ngay_max)
df_ten_chuyen = pd.DataFrame({'CHUYEN' : ['11S01','11S03','11S05','11S07','11S09','11S11','11S13', \
                                        '12S01','12S03','12S05','12S07','12S09','12S11','12S13', \
                                        '21S01','21S03','21S05','21S07','21S09','21S11','21S13', \
                                        '22S01','22S03','22S05','22S07','22S09','22S11','22S13', \
                                        '23S01','23S03','23S05','23S07','23S09','23S11','23S13', \
                                        '24S01','24S03','24S05','24S07','24S09','24S11','24S13', \
                                        '25S01','25S03','25S05','25S07','25S09','25S11','25S13'],\
                'TEN' : ['🦈Cá mập','🐬Cá heo','🦁Sư tử','🐅Hổ','😸Mèo','🙉Khỉ','🦓Ngựa',\
                    '🦈Cá mập','🐬Cá heo','🦁Sư tử','🐅Hổ','😸Mèo','🙉Khỉ','🦓Ngựa',\
                    '🦈Cá mập','🐬Cá heo','🦁Sư tử','🐅Hổ','😸Mèo','🙉Khỉ','🦓Ngựa',\
                    '🦈Cá mập','🐬Cá heo','🦁Sư tử','🐅Hổ','😸Mèo','🙉Khỉ','🦓Ngựa',\
                    '🦈Cá mập','🐬Cá heo','🦁Sư tử','🐅Hổ','😸Mèo','🙉Khỉ','🦓Ngựa',\
                    '🦈Cá mập','🐬Cá heo','🦁Sư tử','🐅Hổ','😸Mèo','🙉Khỉ','🦓Ngựa',\
                    '🦈Cá mập','🐬Cá heo','🦁Sư tử','🐅Hổ','😸Mèo','🙉Khỉ','🦓Ngựa',\
                    ]})
# st.dataframe(df_ten_chuyen)
df_chuyen = df_chuyen.merge(df_ten_chuyen,on='CHUYEN',how='left')
df_chuyen = df_chuyen.query("NAM == @nam and THANG == @thang and NGAY >= @tu_ngay and NGAY <= @den_ngay")
df_chuyen = df_chuyen[df_chuyen['NHA_MAY'].isin(nha_may)]
df_chuyen[['SAH lũy kế','TGLV lũy kế','Thưởng lũy kế']] = (df_chuyen.groupby('CHUYEN')[['SAH','TGLV','TONG_THUONG']].cumsum())
# st.dataframe(df_chuyen)
###
df_cong_nhan = get_data("INCENTIVE","""
                        SELECT MST,HO_TEN,CHUYEN,NGAY,SAH,SO_GIO as TGLV,THUONG_CA_NHAN
                        FROM INCENTIVE_CN_MAY_HANG_NGAY WHERE THUONG_CA_NHAN >0
                        AND NGAY < CAST(GETDATE() AS DATE)
                        ORDER BY NGAY,CHUYEN
                        """)

df_cong_nhan['NHA_MAY'] = 'NT' + df_cong_nhan['CHUYEN'].str[:1]
df_cong_nhan['NGAY'] = pd.to_datetime(df_cong_nhan['NGAY'], format='%Y-%m-%d')
df_cong_nhan['NAM'] = df_cong_nhan['NGAY'].dt.year.astype(str)
df_cong_nhan['THANG'] = df_cong_nhan['NGAY'].dt.month.astype(str).str.zfill(2)
df_cong_nhan = df_cong_nhan.query("NAM == @nam and THANG == @thang and NGAY >= @tu_ngay and NGAY <=@den_ngay")
df_cong_nhan = df_cong_nhan[df_cong_nhan['NHA_MAY'].isin(nha_may)]
###
## tính toán theo xưởng
df_xuong = df_chuyen[['CHUYEN','SAH','TGLV','TONG_THUONG']].copy()
df_xuong['XUONG'] = df_xuong['CHUYEN'].str[:1] + 'P0' + df_xuong['CHUYEN'].str[1:2]
df_ten_xuong = pd.DataFrame({'XUONG' : ['1P01','1P02','2P01','2P02','2P03','2P04'],\
                'TEN_XUONG' : ['🦁Sư tử','🦅Đại bàng','🐲Rồng vàng','🐜Kiến lửa','🐝 Ong vàng','🦓Ngựa vằn']})
df_xuong = df_xuong.merge(df_ten_xuong,on='XUONG',how='left')
# df_xuong
df_oql = get_data('INCENTIVE',"SELECT * FROM TI_LE_LOI WHERE NGAY < CAST(GETDATE() AS DATE) AND NGAY >= '2024-09-01'")
df_oql['XUONG'] = df_oql['CHUYEN'].str[:1] +'P0' + df_oql['CHUYEN'].str[1:2]
df_oql['NHA_MAY'] = 'NT' + df_oql['CHUYEN'].str[:1]
df_oql['CODE'] = df_oql['CHUYEN'].str[2:-2]
df_oql['NHOM'] = df_oql['CODE'].apply(lambda x: 'Cắt' if x == 'C' else 'May' if x == 'S' else 'QC May' if x == 'QC1'
                              else 'Là' if x == 'I' else 'QC Là' if x == 'QC2' else 'Hoàn thiện' if x == 'F' else '')
df_oql['NGAY'] = pd.to_datetime(df_oql['NGAY'], format='%Y-%m-%d')
df_oql['THANG'] = df_oql['NGAY'].dt.month.astype(str).str.zfill(2)
df_oql['NAM'] = df_oql['NGAY'].dt.year.astype(str)
df_oql.pop('CODE')
#di chuyển cột
move_col = df_oql.pop('NHA_MAY')
df_oql.insert(0,'NHA_MAY',move_col)
move_col = df_oql.pop('XUONG')
df_oql.insert(1,'XUONG',move_col)
df_oql['NGAY'] = pd.to_datetime(df_oql['NGAY'], format='%Y-%m-%d')
df_oql['NGAY'] = df_oql['NGAY'].dt.date

#chuyển cột WorkDate về dạng date
df_oql= df_oql[(df_oql['NHA_MAY'].isin(nha_may)) & 
               (df_oql['THANG']==thang) & 
               (df_oql['NAM']==nam) & 
               (df_oql['NGAY'] >= tu_ngay) & 
               (df_oql['NGAY'] <= den_ngay)]
#config chung cho các biểu đồ plotly
config = {
    'displayModeBar': True,  # Hiển thị/thêm thanh công cụ
    'modeBarButtonsToRemove': ['zoom', 'select', 'lasso2d', 'resetScale', 'toImage'],  # Ẩn nút
    'displaylogo': False,  # Ẩn logo Plotly
    'modeBarButtonsToAdd': []  # Đảm bảo không thêm bất kỳ nút nào khác
}
if chuyen_cong_nhan == "Xưởng":
    st.info("🏆 Bảng xếp hạng xưởng ")
    df_xuong_groupby = df_xuong.groupby(by=["TEN_XUONG",'XUONG']).agg({'SAH' : 'sum','TGLV' : 'sum','TONG_THUONG' : 'sum'}).reset_index()
    df_xuong_groupby['EFF'] = df_xuong_groupby['SAH']/df_xuong_groupby['TGLV']
    df_xuong_groupby['Hiệu suất'] = df_xuong_groupby['EFF'].apply(lambda x: f"{x:,.1%}")
    df_xuong_groupby['Tổng thưởng'] = df_xuong_groupby['TONG_THUONG'].apply(lambda x: f"{x/1_000_000:,.1f} triệu")
    df_xuong_groupby['TEN_XUONG2'] = df_xuong_groupby['TEN_XUONG'] + '-' + df_xuong_groupby['XUONG']
    # df_xuong_groupby

    if rp_type == "Hiệu suất":
        is_mobile = streamlit_js_eval(js_expressions="window.innerWidth < 768", want_output=True)

        if is_mobile:
            col1, col2, col3 = st.columns(3) 
            col1, col2 = col2, col1 
        else:
            col1, col2, col3 = st.columns(3) 

        with col2:
            xuong_num_1 = df_xuong_groupby.sort_values('Hiệu suất',ascending=False).iloc[0,0]
            # hieu_suat_num_1 = df_chuyen_groupby.sort_values('Hiệu suất',ascending=False).iloc[0,5]
            st.metric("Chuyền vô địch",value= f"{xuong_num_1}🥇")
            # st.metric("Hiệu suất", value= f"{hieu_suat_num_1}")
        with col1:
            if not is_mobile:
                st.metric("",value="")
            xuong_num_2 = df_xuong_groupby.sort_values('Hiệu suất',ascending=False).iloc[1,0]
            st.metric("Chuyền Á quân",value= f"{xuong_num_2}🥈")
        with col3:
            if not is_mobile:
                st.metric("",value="")
                st.metric("",value="")
            xuong_num_3 = df_xuong_groupby.sort_values('Hiệu suất',ascending=False).iloc[2,0]
            st.metric("Chuyền hạng 3",value= f"{xuong_num_3}🥉")

        st.markdown("---")

        fig = px.bar(
        df_xuong_groupby.sort_values('EFF',ascending=True).iloc[-10:],
        x="EFF",
        y='TEN_XUONG2',
        text="Hiệu suất"
        )
        fig.update_traces(
            textposition = 'outside'
        )
        max_eff = df_xuong_groupby['EFF'].max()*1.2
        fig.update_xaxes(
            tickformat = ",.0%",
            range = [0,max_eff]
        )
        fig.update_yaxes(
            tickfont = dict(size = 14)
        )
        fig.update_layout(
            title = "Top xưởng có hiệu suất cao nhất",
            xaxis_title = 'Hiệu suất xưởng',
            yaxis_title = 'Xưởng'
        )
        fig.update_layout(dragmode="pan")

        st.plotly_chart(fig,use_container_width=True,config=config)
        ###
        with st.expander("Dữ liệu chi tiết"):
            st.dataframe(df_xuong_groupby.sort_values("EFF",ascending=False))
    if rp_type == "Tiền thưởng":
        col1,col2,col3 = st.columns(3)
        with col2:
            xuong_num_1 = df_xuong_groupby.sort_values('TONG_THUONG',ascending=False).iloc[0,0]
            # hieu_suat_num_1 = df_chuyen_groupby.sort_values('Hiệu suất',ascending=False).iloc[0,5]
            st.metric("Chuyền vô địch",value= f"{xuong_num_1}🥇")
            # st.metric("Hiệu suất", value= f"{hieu_suat_num_1}")
        with col1:
            st.metric("",value="")
            xuong_num_2 = df_xuong_groupby.sort_values('TONG_THUONG',ascending=False).iloc[1,0]
            st.metric("Chuyền Á quân",value= f"{xuong_num_2}🥈")
        with col3:
            st.metric("",value="")
            st.metric("",value="")
            xuong_num_3 = df_xuong_groupby.sort_values('TONG_THUONG',ascending=False).iloc[2,0]
            st.metric("Chuyền hạng 3",value= f"{xuong_num_3}🥉")
        st.markdown("---")
        fig = px.bar(
            df_xuong_groupby.sort_values('TONG_THUONG',ascending=True).iloc[-10:],
            x="TONG_THUONG",
            y='TEN_XUONG2',
            text="Tổng thưởng"
        )
        fig.update_traces(
            textposition = 'outside'
        )
        fig.update_layout(
            title = "Top xưởng có tiền thưởng cao nhất",
            xaxis_title = 'Tiền thưởng',
            yaxis_title = 'Xưởng'
        )
        fig.update_yaxes(
            tickfont = dict(size = 14)
        )
        max_tien_thuong = df_xuong_groupby['TONG_THUONG'].max()*1.2
        fig.update_xaxes(
            range=[0,max_tien_thuong]
        )
        fig.update_layout(dragmode="pan")

        st.plotly_chart(fig,use_container_width=True,config=config)
        ###
        with st.expander("Dữ liệu chi tiết"):
            st.dataframe(df_xuong_groupby.sort_values("TONG_THUONG",ascending=False))
###
    if rp_type == "Tỉ lệ lỗi":
        df_oql = pd.merge(df_oql,df_ten_xuong,on='XUONG',how= 'left')
        df_oql['TEN_XUONG2'] = df_oql['TEN_XUONG'] +'-'+df_oql['XUONG']
        df_oql= df_oql.dropna(subset='TEN_XUONG')
        df_oql_groupby = df_oql.groupby(by=['NHOM','TEN_XUONG2']).agg({'TI_LE_LOI' : 'mean'}).reset_index()
        df_oql_groupby['TI_LE_LOI_formated'] = df_oql_groupby['TI_LE_LOI'].apply(lambda x: f"{x:,.1%}")
        # df_oql_groupby
        ds_nhom = ['Cắt','May','QC May','Là','QC Là','Hoàn thiện']
        nhom_sel = st.radio(label="Chọn nhóm",options=ds_nhom,horizontal=True,index=1)
        #Nhóm cắt
        df_oql_groupby_nhom = df_oql_groupby[df_oql_groupby['NHOM'] == nhom_sel]
        # df_oql_groupby_nhom
        fig = px.bar(
            df_oql_groupby_nhom.sort_values('TI_LE_LOI',ascending=False),
            x="TI_LE_LOI",
            y='TEN_XUONG2',
            text="TI_LE_LOI_formated"
        )
        fig.update_traces(
            textposition = 'outside'
        )
        row_num = df_oql_groupby_nhom.shape[0]
        row_hight = 35
        fig.update_layout(
            title = f"Tỉ lệ lỗi nhóm {nhom_sel}",
            xaxis_title = 'Tỉ lệ lỗi',
            yaxis_title = 'Xưởng',
            # height = row_num * row_hight
        )
        fig.update_yaxes(
            tickfont = dict(size = 14)
        )
        max_oql = df_oql_groupby_nhom['TI_LE_LOI'].max()*1.2
        fig.update_xaxes(
            range=[0,max_oql],
            tickformat = ",.0%"
        )
        fig.update_layout(dragmode="pan")

        st.plotly_chart(fig,use_container_width=True,key='bar0',config=config)
        ###    
###
if chuyen_cong_nhan == "Chuyền":
    st.info("🏆 Bảng xếp hạng chuyền ")
    df_chuyen_groupby = df_chuyen.groupby(by=["TEN",'CHUYEN']).agg({'SAH' : 'sum','TGLV' : 'sum','TONG_THUONG' : 'sum'}).reset_index()
    df_chuyen_groupby['EFF'] = df_chuyen_groupby['SAH']/df_chuyen_groupby['TGLV']
    df_chuyen_groupby['Hiệu suất'] = df_chuyen_groupby['EFF'].apply(lambda x: f"{x:,.1%}")
    df_chuyen_groupby['Tổng thưởng'] = df_chuyen_groupby['TONG_THUONG'].apply(lambda x: f"{x/1_000_000:,.1f} triệu")
    # df_chuyen_groupby['TEN_CHUYEN'] = df_chuyen_groupby['TEN'] + '-' + df_chuyen_groupby['CHUYEN']
    df_chuyen_groupby['TEN_CHUYEN'] = df_chuyen_groupby['CHUYEN']

    if rp_type == "Hiệu suất":
        col1,col2,col3 = st.columns(3)
        with col2:
            chuyen_num_1 = df_chuyen_groupby.sort_values('Hiệu suất',ascending=False).iloc[0,1]
            # hieu_suat_num_1 = df_chuyen_groupby.sort_values('Hiệu suất',ascending=False).iloc[0,5]
            st.metric("Chuyền vô địch",value= f"{chuyen_num_1}🥇")
            # st.metric("Hiệu suất", value= f"{hieu_suat_num_1}")
        with col1:
            st.metric("",value="")
            chuyen_num_2 = df_chuyen_groupby.sort_values('Hiệu suất',ascending=False).iloc[1,1]
            st.metric("Chuyền Á quân",value= f"{chuyen_num_2}🥈")
        with col3:
            st.metric("",value="")
            st.metric("",value="")
            chuyen_num_3 = df_chuyen_groupby.sort_values('Hiệu suất',ascending=False).iloc[2,1]
            st.metric("Chuyền hạng 3",value= f"{chuyen_num_3}🥉")
        st.markdown("---")

        fig = px.bar(
        df_chuyen_groupby.sort_values('EFF',ascending=True).iloc[-10:],
        x="EFF",
        y='TEN_CHUYEN',
        text="Hiệu suất"
        )
        fig.update_traces(
            textposition = 'outside'
        )
        max_eff = df_chuyen_groupby['EFF'].max()*1.2
        fig.update_xaxes(
            tickformat = ",.0%",
            range = [0,max_eff]
        )
        fig.update_yaxes(
            tickfont = dict(size = 14)
        )
        fig.update_layout(
            title = "Top 10 chuyền có hiệu suất cao nhất",
            xaxis_title = 'Hiệu suất chuyền',
            yaxis_title = 'Chuyền'
        )
        fig.update_layout(dragmode="pan")

        st.plotly_chart(fig,use_container_width=True,config=config)
        ###
        with st.expander("Dữ liệu chi tiết"):
            st.dataframe(df_chuyen_groupby.sort_values("EFF",ascending=False))
    if rp_type == "Tiền thưởng":
        col1,col2,col3 = st.columns(3)
        with col2:
            chuyen_num_1 = df_chuyen_groupby.sort_values('TONG_THUONG',ascending=False).iloc[0,0]
            # hieu_suat_num_1 = df_chuyen_groupby.sort_values('Hiệu suất',ascending=False).iloc[0,5]
            st.metric("Chuyền vô địch",value= f"{chuyen_num_1}🥇")
            # st.metric("Hiệu suất", value= f"{hieu_suat_num_1}")
        with col1:
            st.metric("",value="")
            chuyen_num_2 = df_chuyen_groupby.sort_values('TONG_THUONG',ascending=False).iloc[1,0]
            st.metric("Chuyền Á quân",value= f"{chuyen_num_2}🥈")
        with col3:
            st.metric("",value="")
            st.metric("",value="")
            chuyen_num_3 = df_chuyen_groupby.sort_values('TONG_THUONG',ascending=False).iloc[2,0]
            st.metric("Chuyền hạng 3",value= f"{chuyen_num_3}🥉")
        st.markdown("---")
        fig = px.bar(
            df_chuyen_groupby.sort_values('TONG_THUONG',ascending=True).iloc[-10:],
            x="TONG_THUONG",
            y='TEN_CHUYEN',
            text="Tổng thưởng"
        )
        fig.update_traces(
            textposition = 'outside'
        )
        fig.update_layout(
            title = "Top 10 chuyền có tiền thưởng cao nhất",
            xaxis_title = 'Tiền thưởng',
            yaxis_title = 'Chuyền'
        )
        fig.update_yaxes(
            tickfont = dict(size = 14)
        )
        max_tien_thuong = df_chuyen_groupby['TONG_THUONG'].max()*1.2
        fig.update_xaxes(
            range=[0,max_tien_thuong]
        )
        fig.update_layout(dragmode="pan")

        st.plotly_chart(fig,use_container_width=True,config=config)
        ###
        with st.expander("Dữ liệu chi tiết"):
            st.dataframe(df_chuyen_groupby.sort_values("TONG_THUONG",ascending=False))
    if rp_type == "Tỉ lệ lỗi":
        # df_oql
        df_oql_groupby = df_oql.groupby(by=['NHOM','CHUYEN']).agg({'TI_LE_LOI' : 'mean'}).reset_index()
        df_oql_groupby['TI_LE_LOI_formated'] = df_oql_groupby['TI_LE_LOI'].apply(lambda x: f"{x:,.1%}")
        # df_oql_groupby
        ds_nhom = ['Cắt','May','QC May','Là','QC Là','Hoàn thiện']
        nhom_sel = st.radio(label="Chọn nhóm",options=ds_nhom,horizontal=True,index=1)
        #Nhóm cắt
        df_oql_groupby_nhom = df_oql_groupby[df_oql_groupby['NHOM'] == nhom_sel]
        # df_oql_groupby_nhom
        fig = px.bar(
            df_oql_groupby_nhom.sort_values('TI_LE_LOI',ascending=False),
            x="TI_LE_LOI",
            y='CHUYEN',
            text="TI_LE_LOI_formated"
        )
        fig.update_traces(
            textposition = 'outside'
        )
        row_num = df_oql_groupby_nhom.shape[0]
        row_hight = 50
        fig.update_layout(
            title = f"Tỉ lệ lỗi nhóm {nhom_sel}",
            xaxis_title = 'Tỉ lệ lỗi',
            yaxis_title = 'Chuyền',
            height = row_num * row_hight
        )
        fig.update_yaxes(
            tickfont = dict(size = 14)
        )
        max_oql = df_oql_groupby_nhom['TI_LE_LOI'].max()*1.2
        fig.update_xaxes(
            range=[0,max_oql],
            tickformat = ",.0%"
        )
        fig.update_layout(dragmode="pan")

        st.plotly_chart(fig,use_container_width=True,key='bar0',config=config)
        ###
if chuyen_cong_nhan == "Công nhân":
    st.info("🥇 Bảng xếp hạng công nhân may")
    df_cong_nhan_groupby = df_cong_nhan.groupby(by=['NHA_MAY','MST','HO_TEN']).agg({'SAH' : 'sum','TGLV' : 'sum','THUONG_CA_NHAN' :'sum'}).reset_index()
    df_cong_nhan_groupby['EFF'] = df_cong_nhan_groupby['SAH']/df_cong_nhan_groupby['TGLV']
    df_cong_nhan_groupby['Hiệu suất'] = df_cong_nhan_groupby['EFF'].apply(lambda x: f"{x:,.1%}")
    df_cong_nhan_groupby['Tiền thưởng'] = df_cong_nhan_groupby['THUONG_CA_NHAN'].apply(lambda x: f"{x/1_000:,.0f} nghìn")
    df_cong_nhan_groupby['MST_HO_TEN'] = df_cong_nhan_groupby['NHA_MAY'] + '-' + df_cong_nhan_groupby['MST'] + '-' + df_cong_nhan_groupby['HO_TEN']
    if rp_type == "Hiệu suất":
        col1,col2,col3 = st.columns(3)
        with col2:
            cn_num_1 = df_cong_nhan_groupby.sort_values('EFF',ascending=False).iloc[0,2]
            # hieu_suat_num_1 = df_chuyen_groupby.sort_values('Hiệu suất',ascending=False).iloc[0,5]
            st.metric("Hạng nhất",value= f"{cn_num_1}🥇")
            # st.metric("Hiệu suất", value= f"{hieu_suat_num_1}")
        with col1:
            st.metric("",value="")
            cn_num_2 = df_cong_nhan_groupby.sort_values('EFF',ascending=False).iloc[1,2]
            st.metric("Hạng nhì",value= f"{cn_num_2}🥈")
        with col3:
            st.metric("",value="")
            st.metric("",value="")
            cn_num_3 = df_cong_nhan_groupby.sort_values('EFF',ascending=False).iloc[2,2]
            st.metric("Hạng ba",value= f"{cn_num_3}🥉")
        st.markdown("---")
        fig = px.bar(
            df_cong_nhan_groupby.sort_values('EFF',ascending=True).iloc[-10:],
            x="EFF",
            y='MST_HO_TEN',
            text="Hiệu suất"
        )
        fig.update_traces(
            textposition = 'outside'
        )
        max_eff = df_cong_nhan_groupby['EFF'].max()*1.2
        fig.update_xaxes(
            tickformat = ",.0%",
            range = [0,max_eff]
        )
        fig.update_yaxes(
            tickfont = dict(size = 14)
        )
        fig.update_layout(
            title = "Top 10 công nhân có hiệu suất cao nhất",
            xaxis_title = 'Hiệu suất cá nhân',
            yaxis_title = 'MST - Họ tên'
        )
        fig.update_layout(dragmode="pan")

        st.plotly_chart(fig,use_container_width=True,key='bar_cn1',config=config)
        ###
        with st.expander("Dữ liệu chi tiết"):
            st.dataframe(df_cong_nhan_groupby.sort_values("EFF",ascending=False))
    if rp_type == "Tiền thưởng":
        col1,col2,col3 = st.columns(3)
        with col2:
            cn_num_1 = df_cong_nhan_groupby.sort_values('THUONG_CA_NHAN',ascending=False).iloc[0,2]
            # hieu_suat_num_1 = df_chuyen_groupby.sort_values('Hiệu suất',ascending=False).iloc[0,5]
            st.metric("Hạng nhất",value= f"{cn_num_1}🥇")
            # st.metric("Hiệu suất", value= f"{hieu_suat_num_1}")
        with col1:
            st.metric("",value="")
            cn_num_2 = df_cong_nhan_groupby.sort_values('THUONG_CA_NHAN',ascending=False).iloc[1,2]
            st.metric("Hạng hai",value= f"{cn_num_2}🥈")
        with col3:
            st.metric("",value="")
            st.metric("",value="")
            cn_num_3 = df_cong_nhan_groupby.sort_values('THUONG_CA_NHAN',ascending=False).iloc[2,2]
            st.metric("Hạng 3",value= f"{cn_num_3}🥉")
        st.markdown("---")
        fig = px.bar(
            df_cong_nhan_groupby.sort_values('THUONG_CA_NHAN',ascending=True).iloc[-10:],
            x="THUONG_CA_NHAN",
            y='MST_HO_TEN',
            text="Tiền thưởng"
        )
        fig.update_traces(
            textposition = 'outside'
        )
        fig.update_layout(
            title = "Top 10 công nhân đạt tiền thưởng cao nhất",
            xaxis_title = 'Tiền thưởng',
            yaxis_title = 'MST - Họ tên'
        )
        fig.update_yaxes(
            tickfont = dict(size = 14)
        )
        max_tien_thuong = df_cong_nhan_groupby['THUONG_CA_NHAN'].max()*1.2
        fig.update_xaxes(
            range=[0,max_tien_thuong]
        )
        fig.update_layout(dragmode="pan")

        st.plotly_chart(fig,use_container_width=True,key='bar_cn2',config=config)
        ###
        with st.expander("Dữ liệu chi tiết"):
            st.dataframe(df_cong_nhan_groupby.sort_values('THUONG_CA_NHAN',ascending=False))