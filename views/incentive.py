import streamlit as st 
import pandas as pd
import plotly.express as px 
import plotly.graph_objects as go 
from datetime import date,datetime
from load_data import get_data
import math
import numpy as np

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
reports = ['Tổng hợp','Công nhân Cắt','Công nhân may','Công nhân QC1','Công nhân Là','Công nhân QC2','Công nhân đóng gói','Công nhân NDC','Công nhân phụ','Quản lý']
bao_cao = st.sidebar.selectbox("Chọn báo cáo",options= reports,index=0)

st.markdown(f'<h1 class="centered-title">BÁO CÁO THƯỞNG NĂNG SUẤT ({bao_cao})</h1>', unsafe_allow_html=True)
#Config chung cho plotly chart
config = {
    'displayModeBar': True,  # Hiển thị/thêm thanh công cụ
    'modeBarButtonsToRemove': ['zoom', 'select', 'lasso2d', 'resetScale', 'toImage'],  # Ẩn nút
    'displaylogo': False,  # Ẩn logo Plotly
    'modeBarButtonsToAdd': []  # Đảm bảo không thêm bất kỳ nút nào khác
}

if bao_cao == 'Tổng hợp':
    df_nhom_cat = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                           TGLV as TONG_TGLV,TONG_THUONG,SO_NGAY,N'Cắt' as NHOM
                           FROM TONG_HOP_TGLV_TONG_THUONG_CN_CAT WHERE NHA_MAY in ({', '.join(f'\'{item}\'' for item in nha_may)})
                           """)
    
    df_nhom_may = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                           TONG_TGLV,TONG_THUONG,SO_NGAY,'May' as NHOM
                           FROM TONG_HOP_TIEN_THUONG_HIEU_SUAT_CN_MAY WHERE NHA_MAY in ({', '.join(f'\'{item}\'' for item in nha_may)}) 
                           """)
    
    df_nhom_qc1 = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                           TONG_TGLV,TONG_THUONG,SO_NGAY,N'QC1' as NHOM
                           FROM TONG_HOP_TIEN_THUONG_HIEU_SUAT_TGLV_QC1 WHERE NHA_MAY in ({', '.join(f'\'{item}\'' for item in nha_may)})
                           """)
    
    df_nhom_la = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                           TONG_TGLV,TONG_THUONG,SO_NGAY,N'Là' as NHOM
                           FROM TONG_HOP_TIEN_THUONG_HIEU_SUAT_TGLV_LA WHERE NHA_MAY in ({', '.join(f'\'{item}\'' for item in nha_may)})
                           """)
    
    df_nhom_qc2 = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                           TONG_TGLV,TONG_THUONG,SO_NGAY,N'QC2' as NHOM
                           FROM TONG_HOP_TIEN_THUONG_HIEU_SUAT_TGLV_QC2 WHERE NHA_MAY in ({', '.join(f'\'{item}\'' for item in nha_may)})
                           """)
    
    df_nhom_hoan_thien = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                           TGLV AS TONG_TGLV,TONG_THUONG,SO_NGAY,N'Hoàn thiện' as NHOM
                           FROM TONG_HOP_TGLV_TONG_THUONG_CN_DONG_GOI WHERE NHA_MAY in ({', '.join(f'\'{item}\'' for item in nha_may)})
                           """)
    
    df_nhom_NDC = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                           TGLV AS TONG_TGLV,TONG_THUONG,SO_NGAY,N'NDC' as NHOM
                           FROM TONG_HOP_TGLV_TONG_THUONG_CN_NDC WHERE NHA_MAY in ({', '.join(f'\'{item}\'' for item in nha_may)})
                           """)
    
    df_nhom_phu = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                           TGLV AS TONG_TGLV,TONG_THUONG,SO_NGAY,N'CN Phụ' as NHOM
                           FROM TONG_HOP_TGLV_TONG_THUONG_CN_PHU WHERE NHA_MAY in ({', '.join(f'\'{item}\'' for item in nha_may)})
                           """)
    
    df_nhom_quan_ly = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                           TGLV AS TONG_TGLV,TONG_THUONG,SO_NGAY,N'Quản lý' as NHOM
                           FROM TONG_HOP_TGLV_TONG_THUONG_QUAN_LY WHERE NHA_MAY in ({', '.join(f'\'{item}\'' for item in nha_may)})
                           """)
    
    df = pd.concat([df_nhom_cat,df_nhom_may,df_nhom_qc1,df_nhom_la,df_nhom_qc2,df_nhom_hoan_thien,df_nhom_NDC,df_nhom_phu,df_nhom_quan_ly])
    df['XUONG'] = df['CHUYEN'].apply(lambda x: (x[:1] + 'NDC') if 'NDC' in x \
        else (x[:1] + 'TNC') if 'TNC' in x \
        else (x[:1] + 'P0' + x[1:2]))
    
    nam = df['NAM'].sort_values(ascending=False).unique()
    sel_nam = st.sidebar.selectbox("Chọn năm",options=nam)
    thang = df[df['NAM']==sel_nam]['THANG'].sort_values(ascending = False).unique()
    sel_thang = st.sidebar.selectbox("Chọn tháng",options=thang)
    so_ngay_min = df[(df['NAM']==sel_nam) & (df['THANG']==sel_thang)]['SO_NGAY'].min()
    so_ngay_max = df[(df['NAM']==sel_nam) & (df['THANG']==sel_thang)]['SO_NGAY'].max()
    sel_so_ngay_min,sel_so_ngay_max = st.sidebar.slider("Chọn số ngày làm việc",value=(so_ngay_min,so_ngay_max))
    df = df.query("THANG == @sel_thang and NAM == @sel_nam and SO_NGAY >= @sel_so_ngay_min and SO_NGAY <= @sel_so_ngay_max")
    
    cols = st.columns(len(nha_may))
    
    df_list = [df[df['NHA_MAY'] == fac] for fac in nha_may]
    
    max_tien = max(df.groupby(by=['NHOM'])["TONG_THUONG"].sum().max() for df in df_list) * 1.2
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_filter = df_list[i]
            tong_thuong = df_filter['TONG_THUONG'].sum()
            st.metric(f"Tổng tiền thưởng Incentive nhà máy {fac}",value=f"{tong_thuong:,.0f} VNĐ")
            ###
            df_tong_thuong = df_filter.groupby(by=['NHOM']).agg({'TONG_THUONG' : 'sum'}).reset_index()
            df_tong_thuong['Tổng tiền thưởng'] = df_tong_thuong['TONG_THUONG'].apply(lambda x: f"{x/1_000_000:,.1f} triệu")
            category_orders={'NHOM' : ['Cắt','May','QC1','Là','QC2','Hoàn thiện','NDC','CN Phụ','Quản lý']}
            fig = px.bar(
                df_tong_thuong,
                y='NHOM',
                x='TONG_THUONG',
                text= 'Tổng tiền thưởng',
                category_orders=category_orders
            )
            fig.update_layout(
                title = 'Tổng tiền thưởng theo từng nhóm',
                xaxis_title = 'Nhóm',
                yaxis_title = 'Tổng tiền thưởng'
            )
            fig.update_traces(
                textposition = 'outside'
            )
            fig.update_xaxes(
                range = [0, max_tien]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,config = config)
    
    max_tien_tb = max(df.groupby(by=['NHOM'])["TONG_THUONG"].mean().max() for df in df_list) * 1.2 
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_filter = df_list[i]
            tbthuong = df_filter['TONG_THUONG'].mean()
            st.metric(f"Trung bình tiền thưởng 1 công nhân {fac}",value=f"{tbthuong:,.0f} VNĐ")
            ###        
            df_tb_thuong = df_filter.groupby(by=['NHOM']).agg({'TONG_THUONG' : 'mean'}).reset_index()
            df_tb_thuong['Tổng tiền thưởng'] = df_tb_thuong['TONG_THUONG'].apply(lambda x: f"{x/1_000:,.0f} nghìn")
            category_orders={'NHOM' : ['Cắt','May','QC1','Là','QC2','Hoàn thiện','NDC','CN Phụ','Quản lý']}
            fig = px.bar(
                df_tb_thuong,
                y='NHOM',
                x='TONG_THUONG',
                # color='XUONG',
                # barmode='group',
                text= 'Tổng tiền thưởng',
                category_orders=category_orders
            )
            fig.update_layout(
                title = 'Trung bình tiền thưởng 1 công nhân theo từng nhóm',
                xaxis_title = 'Nhóm',
                yaxis_title = 'Trung bình tiền thưởng'
            )
            fig.update_traces(
                textposition = 'outside'
            )
            fig.update_xaxes(
                range = [0,max_tien_tb]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,config = config)
            
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_filter = df_list[i]
            df_xuong_nhom = df_filter.groupby(by = ['XUONG','NHOM']).agg({'TONG_THUONG' : 'sum'}).reset_index()
            # st.write(df_xuong_nhom)
            fig = px.sunburst(
                df_xuong_nhom,
                path= ['XUONG','NHOM'],
                color='NHOM',
                values='TONG_THUONG',
                title= f'Phân bổ tổng tiền thưởng theo xưởng, nhóm {fac}'
            )
            fig.update_layout(dragmode="pan")
            
            st.plotly_chart(fig,use_container_width=True,config = config)
    
    max_xuong_nhom_tb =  max(df.groupby(by = ['XUONG','NHOM'])["TONG_THUONG"].mean().max() for df in df_list) * 1.2 
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_filter = df_list[i]
            df_xuong_nhom_tb = df_filter.groupby(by = ['XUONG','NHOM']).agg({'TONG_THUONG' : 'mean'}).reset_index()
            # st.write(df_xuong_nhom_tb)
            fig = px.bar(
                df_xuong_nhom_tb,
                x= 'NHOM',
                y='TONG_THUONG',
                color='XUONG',
                barmode='group',
                category_orders=category_orders    
            )
            fig.update_layout(
                title= f'Trung bình tiền thưởng theo xưởng, nhóm {fac}',
                xaxis_title = 'Nhóm',
                yaxis_title = 'Trung bình tiền thưởng',
                bargap=0.1,
                legend_title='Xưởng'
                )
            fig.update_yaxes(
                range = [0,max_xuong_nhom_tb]
            )
            fig.update_layout(dragmode="pan")
            
            st.plotly_chart(fig,use_container_width=True,config = config)
            
    with st.expander("Dữ liệu chi tiết"):
        st.dataframe(df)
        
if bao_cao == 'Công nhân Cắt':
    df = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                           TGLV as TONG_TGLV,TONG_THUONG,SO_NGAY
                           FROM TONG_HOP_TGLV_TONG_THUONG_CN_CAT WHERE NHA_MAY in ({', '.join(f'\'{item}\'' for item in nha_may)})
                           """)
    df['XUONG'] = df['CHUYEN'].apply(lambda x: x[:1] +'TNC' if 'TNC' in x \
                                    else x[:1] + 'NDC' if 'NDC' in x \
                                        else x[:1] + 'P0' + x[1:2])
    df['CHUC_VU'] = df['CHUC_VU'].str.replace(r'thợ cắt|Thợ Cắt','Thợ cắt',regex=True)
    df['CHUC_VU'] = df['CHUC_VU'].str.replace(r'Công nhân vận hành máy Cắt','Công nhân vận hành máy cắt',regex=True)
    nam = df['NAM'].sort_values(ascending=False).unique()
    sel_nam = st.sidebar.selectbox("Chọn năm",options=nam)
    df_fitered = df[df['NAM'] == sel_nam]
    thang = df_fitered['THANG'].sort_values(ascending=False).unique()
    sel_thang = st.sidebar.selectbox("Chọn tháng",options=thang)
    df_fitered = df_fitered[df_fitered['THANG'] == sel_thang]
    so_ngay_min = df_fitered['SO_NGAY'].min()
    so_ngay_max = df_fitered['SO_NGAY'].max()
    so_ngay_from,so_ngay_to = st.sidebar.slider("Chọn số ngày làm việc",value=(so_ngay_min,so_ngay_max))
    df_fitered = df_fitered.query("SO_NGAY >= @so_ngay_from and SO_NGAY <= @so_ngay_to")
    df_fitered['Tiền thưởng'] = df_fitered['TONG_THUONG'].apply(lambda x: f"{x/1_000:,.0f} nghìn")
    
    df_list = [df_fitered[df_fitered['NHA_MAY'] == fac] for fac in nha_may]
    cols = st.columns(len(nha_may))
    
    max_thuong = max(df["TONG_THUONG"].max() for df in df_list) * 1.2
    max_ngay = max(df["SO_NGAY"].max() for df in df_list) * 1.2
    
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_fac = df_fitered[df_fitered["NHA_MAY"] == fac]
            tong_thuong = df_fac['TONG_THUONG'].sum()
            st.metric(f"Tổng tiền thưởng nhóm Cắt {fac}",value=f"{tong_thuong:,.0f}")
            ###
            fig = px.scatter(df_fac,
                            x='SO_NGAY',
                            y='TONG_THUONG',
                            color='CHUC_VU',
                            size='TONG_TGLV',
                            hover_data={
                                'MST' : True,
                                'HO_TEN' : True,
                                'TONG_TGLV' : True,
                                'Tiền thưởng' : True,
                                'TONG_THUONG' : False
                            }
                            )
            fig.update_layout(
                title = 'Phân bổ tiền thưởng theo số ngày làm việc',
                xaxis_title = 'Số ngày làm việc',
                yaxis_title = 'Tiền thưởng',
                legend_title = 'Chức danh'
            )
            fig.update_traces(
                marker = dict(line = dict(width = 1, color = 'white'))
            )
            fig.update_xaxes(
                range = [0,max_ngay]
            )
            fig.update_yaxes(
                range = [0,max_thuong]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,config = config)
            
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_fac = df_fitered[df_fitered["NHA_MAY"] == fac]
            tb_thuong = df_fac['TONG_THUONG'].mean()
            st.metric(f"Trung bình tiền thưởng công nhân Cắt {fac}",value=f"{tb_thuong:,.0f}")
            ###
            df_chuc_vu = df_fac.groupby(by=['XUONG','CHUC_VU']).agg({'TONG_THUONG' : 'mean'}).reset_index()
            df_chuc_vu['Trung bình thưởng'] = df_chuc_vu['TONG_THUONG'].apply(lambda x: f"{x:,.0f}")
            ds_chuc_vu = ['Công nhân trải vải','Công nhân vận hành máy cắt','Thợ cắt']
            df_chuc_vu = df_chuc_vu[df_chuc_vu['CHUC_VU'].isin(ds_chuc_vu)]
            fig = px.bar(
                df_chuc_vu,
                x='CHUC_VU',
                y='TONG_THUONG',
                color='XUONG',
                barmode='group',
                text='Trung bình thưởng'
            )
            fig.update_layout(
                title = "Trung bình tiền thưởng theo chức danh",
                xaxis_title = 'Chức danh',
                yaxis_title = 'Trung bình tiền thưởng',
                legend_title = 'Xưởng'
            )
            fig.update_traces(
                textposition = 'outside'
            )
            fig.update_yaxes(
                range = [0,max_thuong]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,config = config)
            
    with st.expander("Dữ liệu chi tiết"):
        st.dataframe(df_fitered)
    
    st.markdown("---")
    
    df_nhom = get_data(DB='INCENTIVE',query=f"""
                           SELECT * FROM THUONG_NHOM_CAT_HANG_NGAY WHERE NHA_MAY IN ({', '.join(f'\'{item}\'' for item in nha_may)}) AND NHOM NOT LIKE '%99'
                           ORDER BY NGAY,NHOM
                           """)
    df_nhom['NAM'] = df_nhom['NGAY'].apply(lambda x: x[:4])
    df_nhom['THANG'] = df_nhom['NGAY'].apply(lambda x: x[5:7])
    df_nhom= df_nhom.query("NAM == @sel_nam and THANG == @sel_thang")
    df_nhom['Hiệu suất'] = df_nhom['EFF'].apply(lambda x: f"{x:,.0%}")
    df_nhom['Thưởng nhóm'] = df_nhom['TONG_THUONG_NHOM'].apply(lambda x: f"{x/1_000:,.0f} nghìn")

    df_nhom_list = [df_nhom[df_nhom['NHA_MAY'] == fac] for fac in nha_may]
    max_eff = max(df["EFF"].max() for df in df_nhom_list) * 1.1
    min_eff = max(df["EFF"].min() for df in df_nhom_list) * 0.8
    
    cols2 = st.columns(len(nha_may))
    for i, fac in enumerate(nha_may):
        with cols2[i]:
            df_nhom_fac = df_nhom_list[i]
            fig = px.line(
                df_nhom_fac,
                x="NGAY",
                y="EFF",
                color= 'NHOM',
                text=  'Hiệu suất'
            )
            fig.update_xaxes(
                dtick = 'D1',
                tickformat = '%d/%m'
            )
            fig.update_layout(
                title = f'Hiệu suất từng nhóm theo ngày {fac}',
                xaxis_title = "Ngày",
                yaxis_title = "Hiệu suất",
                legend_title = 'Nhóm'
            )
            fig.update_traces(
                textposition = 'top center'
            )
            fig.update_yaxes(
                range = [min_eff, max_eff]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,key=f'line1{fac}',config = config)
    
    max_thuongnhom = max(df['TONG_THUONG_NHOM'].max() for df in df_nhom_list) * 1.1
    min_thuongnhom = max(df['TONG_THUONG_NHOM'].min() for df in df_nhom_list) * 0.8
    for i, fac in enumerate(nha_may):
        with cols2[i]:
            df_nhom_fac = df_nhom_list[i]
            fig = px.line(
                df_nhom_fac,
                x="NGAY",
                y="TONG_THUONG_NHOM",
                color= 'NHOM',
                text=  'Thưởng nhóm'
                )
            fig.update_xaxes(
                dtick = 'D1',
                tickformat = '%d/%m'
            )
            fig.update_layout(
                title = f'Hiệu suất từng nhóm theo ngày {fac}',
                xaxis_title = "Ngày",
                yaxis_title = "Thưởng nhóm",
                legend_title = 'Nhóm'
            )
            fig.update_traces(
                textposition = 'top center'
            )
            fig.update_yaxes(
                range = [min_thuongnhom, max_thuongnhom]
            )
            fig.update_layout(dragmode="pan")
            
            st.plotly_chart(fig,use_container_width=True,key=f'line2{fac}',config = config)
    
    with st.expander("Dữ liệu thưởng nhóm chi tiết"):
        st.dataframe(df_nhom)

if bao_cao == 'Công nhân may':
    df_cn_may = get_data(DB='INCENTIVE',query=f"SELECT * FROM TONG_HOP_TIEN_THUONG_HIEU_SUAT_CN_MAY WHERE NHA_MAY IN ({', '.join(f'\'{item}\'' for item in nha_may)}) ORDER BY CHUYEN")
    
    df_cn_may['XUONG'] = df_cn_may['CHUYEN'].str[0:1] + 'P0' + df_cn_may['CHUYEN'].str[1:2]
    df_cn_may['SAH'] = df_cn_may['EFF_TB']*df_cn_may['TONG_TGLV']
    df_cn_may_selected = df_cn_may.query('NHA_MAY in @nha_may')
    df_cn_may_selected = df_cn_may_selected[~df_cn_may_selected['CHUYEN'].str.contains('TNC')]
    xuong = st.sidebar.multiselect("Chọn xưởng",options=df_cn_may_selected['XUONG'].unique(),default=df_cn_may_selected['XUONG'].unique())
    df_cn_may_selected= df_cn_may_selected[df_cn_may_selected['XUONG'].isin(xuong)]
    
    cols = st.columns(2)
    with cols[0]:
        nam_opt = df_cn_may_selected['NAM'].sort_values(ascending=False).unique()
        nam = st.selectbox("Chọn năm",options=nam_opt)
    with cols[1]:   
        df_cn_may_selected = df_cn_may_selected.query('NAM == @nam')
        thang_opt = df_cn_may_selected['THANG'].sort_values(ascending=False).unique()
        thang = st.selectbox("Chọn tháng",options=thang_opt)
    
    df_cn_may_selected = df_cn_may_selected.query('NAM == @nam and THANG == @thang')
    chuyen = st.multiselect("Chọn chuyền",options= df_cn_may_selected['CHUYEN'].unique(),default=df_cn_may_selected['CHUYEN'].unique())
        
    df_cn_may_selected = df_cn_may_selected[df_cn_may_selected['CHUYEN'].isin(chuyen)]
    df_cn_may_selected['Hiệu suất'] = df_cn_may_selected['EFF_TB'].apply(lambda x: f"{x:.0%}")
    df_cn_may_selected['Tiền thưởng'] = df_cn_may_selected['TONG_THUONG'].apply(lambda x: f"{x:,.0f}")
    df_cn_may_selected = df_cn_may_selected.dropna(subset=["EFF_TB"])
    ###

    so_ngay_min = df_cn_may_selected['SO_NGAY'].min()
    so_ngay_max = df_cn_may_selected['SO_NGAY'].max()
    so_ngay_from,so_ngay_to = st.sidebar.slider("Chọn số ngày làm việc",min_value= so_ngay_min,max_value=so_ngay_max,value=[so_ngay_min,so_ngay_max])
    df_cn_may_selected = df_cn_may_selected.query('SO_NGAY >= @so_ngay_from and SO_NGAY <=@so_ngay_to')
    
    df_cn_may_list = [df_cn_may_selected[df_cn_may_selected['NHA_MAY'] == fac] for fac in nha_may]
    cols2 = st.columns(len(nha_may))
    
    for i, fac in enumerate(nha_may):
        with cols2[i]:
            df_fac = df_cn_may_list[i]
            
            so_cn = df_fac['MST'].count()
            Eff_tb = df_fac['SAH'].sum()/df_fac['TONG_TGLV'].sum()
            Incentive_tb = df_fac['TONG_THUONG'].mean()
            so_ngay_tb = df_fac['SO_NGAY'].mean()
            st.info(f"Tổng quan {fac}")
            st.metric(label="Số ngày làm việc trung bình",value= f"{so_ngay_tb:,.0f}")
            st.metric(label="Số công nhân",value= f"{so_cn:,.0f}")
            st.metric(label="Hiệu suất trung bình",value= f"{Eff_tb:,.0%}")
            st.metric(label="Tiền thưởng trung bình",value= f"{Incentive_tb:,.0f}")
    
    max_thuong = max(df["TONG_THUONG"].max() for df in df_cn_may_list) * 1.2
    for i, fac in enumerate(nha_may):
        with cols2[i]:
            df_fac = df_cn_may_list[i]
            SCP_order = ['U','N','S','M']
            fig = px.scatter(
                df_fac,
                x= "EFF_TB",
                y= "TONG_THUONG",
                color= "SCP",
                color_discrete_map={
                    'U' : 'red',
                    'N' : 'blue',
                    'S' : 'green',
                    'M' : 'purple'
                },
                size= "TONG_TGLV",
                hover_data={
                    'MST':True,
                    'HO_TEN' : True,
                    'CHUYEN' : True,
                    'EFF_TB' : False,
                    'TONG_THUONG' : False,
                    'Hiệu suất' : True,
                    'Tiền thưởng' : True,
                    'SCP' : False
                },
                category_orders= {'SCP' : SCP_order},
                # symbol='XUONG',
                size_max= 10
            )
            fig.update_layout(
                xaxis_title = 'Hiệu suất trung bình',
                yaxis_title = "Tổng thưởng (VNĐ)",
                title = f"Phân bổ tiền thưởng theo hiệu suất {fac}"
            )
            fig.update_xaxes(
                tickformat = '.0%',
            )
            fig.update_traces(
                marker = dict(line = dict(width = 1,color = 'white')),
            )
            fig.update_yaxes(
                range=[0, max_thuong]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,config = config)
    
    for i, fac in enumerate(nha_may):
        with cols2[i]:
            df_fac = df_cn_may_list[i]
            SCP_order = ['U','N','S','M']
            fig = px.pie(
                df_fac[df_fac['SCP'].isin(SCP_order)],
                color="SCP",
                names="SCP",
                category_orders={"SCP" : SCP_order},
                color_discrete_map={
                    'U' : 'red',
                    'N' : 'blue',
                    'S' : 'green',
                    'M' : 'purple'
                }
            )
            fig.update_layout(
                title = f"Tỉ lệ công nhân theo SCP {fac}"
            )
            fig.update_traces(
                textinfo = 'percent+label',
                textposition = 'inside',
                textfont = dict(size = 14)
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,config = config)
    
    
    eff_max = max(df["EFF_TB"].max() for df in df_cn_may_list) * 1.2
    y_max = 0
    for df in df_cn_may_list:
        counts, bins = np.histogram(df["EFF_TB"], bins=20)
        y_max = max(y_max, max(counts))
    
    for i, fac in enumerate(nha_may):
        with cols2[i]:
            df_fac = df_cn_may_list[i]
            fig = px.histogram(
                df_fac,
                x= "EFF_TB",
                text_auto= True,
                nbins=20
            )
            fig.update_layout(
                title = f"Phân bổ công nhân theo hiệu suất {fac}",
                xaxis_title = "Hiệu suất",
                yaxis_title = "Số công nhân"
            )
            fig.update_xaxes(
                tickformat = ".0%"
            )
            fig.update_traces(
                textposition = 'outside'
            )
            fig.update_yaxes(
                range = [0, y_max * 1.5]
            )
            fig.update_xaxes(
                range = [-0.05, eff_max]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,config = config)
    
    max_thuong_2 = max(df["TONG_THUONG"].max() for df in df_cn_may_list) * 1.2
    for i, fac in enumerate(nha_may):
        with cols2[i]:
            df_fac = df_cn_may_list[i]
            SCP_order = ['U','N','S','M']
            fig = px.box(
                df_fac,
                x= "SCP",
                y= "TONG_THUONG",
                color="SCP",
                category_orders= {"SCP" : SCP_order},
                color_discrete_map={
                    'U' : 'red',
                    'N' : 'blue',
                    'S' : 'green',
                    'M' : 'purple'
                }
            )
            fig.update_layout(
                title = f"Phân bổ tiền thưởng theo bậc kỹ năng {fac}",
                yaxis_title = "Tiền thưởng"
            )
            fig.update_yaxes(
                range=[0, max_thuong_2]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,config = config)
    
    max_thuong_3 = max(df.groupby(by="SCP")["TONG_THUONG"].mean().max() for df in df_cn_may_list) * 1.2
    for i, fac in enumerate(nha_may):
        with cols2[i]:
            df_fac = df_cn_may_list[i]
            df_cn_may_selected_SCP = df_fac.groupby(by="SCP").agg({"TONG_THUONG" : 'mean'}).reset_index()
            df_cn_may_selected_SCP['Tổng thưởng'] = df_cn_may_selected_SCP['TONG_THUONG'].apply(lambda x: f"{x:,.0f}")
            SCP_order = ['U','N','S','M']
            fig = px.bar(
                df_cn_may_selected_SCP,
                x='SCP',
                y= "TONG_THUONG",
                text= 'Tổng thưởng',
                color="SCP",
                color_discrete_map={
                    'U' : 'red',
                    'N' : 'blue',
                    'S' : 'green',
                    'M' : 'purple'
                },
                category_orders={"SCP" : SCP_order}
            )
            fig.update_traces(
                textposition = 'outside'
            )
            fig.update_layout(
                title = f'Tiền thưởng trung bình theo bậc kỹ năng {fac}',
                yaxis_title = 'Tiền thưởng'
            )
            fig.update_yaxes(
                range=[0, max_thuong_3]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,config = config)
        
if bao_cao == 'Công nhân QC1':
    df = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                           TONG_TGLV,EFF_TB,TONG_THUONG,SO_NGAY
                           FROM TONG_HOP_TIEN_THUONG_HIEU_SUAT_TGLV_QC1 WHERE NHA_MAY IN ({', '.join(f'\'{item}\'' for item in nha_may)})
                           """)
    df['XUONG'] = df['CHUYEN'].apply(lambda x: x[:1] +'TNC' if 'TNC' in x \
                                    else x[:1] + 'NDC' if 'NDC' in x \
                                        else x[:1] + 'P0' + x[1:2])
    nam = df['NAM'].sort_values(ascending=False).unique()
    sel_nam = st.sidebar.selectbox("Chọn năm",options=nam)
    df_fitered = df[df['NAM'] == sel_nam]
    thang = df_fitered['THANG'].sort_values(ascending=False).unique()
    sel_thang = st.sidebar.selectbox("Chọn tháng",options=thang)
    df_fitered = df_fitered[df_fitered['THANG'] == sel_thang]
    so_ngay_min = df_fitered['SO_NGAY'].min()
    so_ngay_max = df_fitered['SO_NGAY'].max()
    so_ngay_from,so_ngay_to = st.sidebar.slider("Chọn số ngày làm việc",value=(so_ngay_min,so_ngay_max))
    df_fitered = df_fitered.query("SO_NGAY >= @so_ngay_from and SO_NGAY <= @so_ngay_to")
    df_fitered['Tiền thưởng'] = df_fitered['TONG_THUONG'].apply(lambda x: f"{x/1_000:,.0f} nghìn")
    df_fitered['Hiệu suất'] = df_fitered['EFF_TB'].apply(lambda x: f"{x:,.0%}")
    
    df_list = [df_fitered[df_fitered['NHA_MAY'] == fac] for fac in nha_may]
    cols = st.columns(len(nha_may))
    
    max_thuong = max(df["TONG_THUONG"].max() for df in df_list) * 1.2
    max_eff = max(df["EFF_TB"].max() for df in df_list) * 1.2
    
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_fac = df_list[i]
            tong_thuong = df_fac['TONG_THUONG'].sum()
            st.metric(f"Tổng tiền thưởng nhóm QC1 {fac}",value=f"{tong_thuong:,.0f}")
            
            fig = px.scatter(df_fac,
                            x='EFF_TB',
                            y='TONG_THUONG',
                            color='CHUC_VU',
                            size='TONG_TGLV',
                            hover_data={
                                'MST' : True,
                                'HO_TEN' : True,
                                'TONG_TGLV' : True,
                                'Hiệu suất' : True,
                                'Tiền thưởng' : True,
                                'TONG_THUONG' : False,
                                'EFF_TB' : False,
                                'CHUC_VU' : True
                            }
                        )
            fig.update_layout(
                title = 'Phân bổ tiền thưởng theo hiệu suất cá nhân',
                xaxis_title = 'Hiệu suất cá nhân',
                yaxis_title = 'Tiền thưởng'
            )
            fig.update_xaxes(
                tickformat = ',.0%'
            )
            fig.update_traces(
                marker = dict(line = dict(width = 1, color = 'white'))
            )
            fig.update_yaxes(
                range = [0, max_thuong]
            )
            fig.update_xaxes(
                range = [0, max_eff]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,config = config)
            
    max_tb_thuong = max(df.groupby(by=['XUONG','CHUC_VU'])["TONG_THUONG"].mean().max() for df in df_list) * 1.2 
    
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_fac = df_list[i]
            tb_thuong = df_fac['TONG_THUONG'].mean()
            st.metric(f"Trung bình tiền thưởng công nhân QC1 {fac}",value=f"{tb_thuong:,.0f}")
            ###
            df_chuc_vu = df_fac.groupby(by=['XUONG','CHUC_VU']).agg({'TONG_THUONG' : 'mean'}).reset_index()
            df_chuc_vu['Trung bình thưởng'] = df_chuc_vu['TONG_THUONG'].apply(lambda x: f"{x:,.0f}")
            ds_chuc_vu = ['Công nhân kiểm hàng may']
            df_chuc_vu = df_chuc_vu[df_chuc_vu['CHUC_VU'].isin(ds_chuc_vu)]
            fig = px.bar(
                df_chuc_vu,
                x='CHUC_VU',
                y='TONG_THUONG',
                color='XUONG',
                barmode='group',
                text='Trung bình thưởng'
            )
            fig.update_layout(
                title = "Trung bình tiền thưởng theo chức danh",
                xaxis_title = 'Chức danh',
                yaxis_title = 'Trung bình tiền thưởng',
                legend_title = 'Xưởng'
            )
            fig.update_traces(
                textposition = 'outside'
            )
            fig.update_yaxes(
                range=[0, max_tb_thuong]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,key=f'line2{fac}',config = config)
            
    with st.expander("Dữ liệu chi tiết"):
        st.dataframe(df_fitered)
        
    st.markdown("---")
    
    df_nhom = get_data(DB='INCENTIVE',query=f"""
                           SELECT * FROM THUONG_NHOM_QC1_HANG_NGAY WHERE NHA_MAY IN ({', '.join(f'\'{item}\'' for item in nha_may)}) AND NHOM NOT LIKE '%99'
                           ORDER BY NGAY,NHOM
                           """)
    df_nhom['NAM'] = df_nhom['NGAY'].apply(lambda x: x[:4])
    df_nhom['THANG'] = df_nhom['NGAY'].apply(lambda x: x[5:7])
    df_nhom= df_nhom.query("NAM == @sel_nam and THANG == @sel_thang")
    df_nhom['Hiệu suất'] = df_nhom['EFF'].apply(lambda x: f"{x:,.0%}")
    df_nhom['Thưởng nhóm'] = df_nhom['TONG_THUONG_NHOM'].apply(lambda x: f"{x/1_000:,.0f} nghìn")
    
    df_nhom_list = [df_nhom[df_nhom['NHA_MAY'] == fac] for fac in nha_may]
    cols2 = st.columns(len(nha_may))
    
    max_eff = max(df["EFF"].max() for df in df_nhom_list) * 1.1
    for i, fac in enumerate(nha_may):
        with cols2[i]:
            df_nhom_fac = df_nhom_list[i]
            fig = px.line(
                df_nhom_fac,
                x="NGAY",
                y="EFF",
                color= 'NHOM',
                text=  'Hiệu suất'
            )
            fig.update_xaxes(
                dtick = 'D1',
                tickformat = '%d/%m'
            )
            fig.update_layout(
                title = f'Hiệu suất từng nhóm theo ngày {fac}',
                xaxis_title = "Ngày",
                yaxis_title = "Hiệu suất",
                legend_title = 'Nhóm'
            )
            fig.update_traces(
                textposition = 'top center'
            )
            fig.update_yaxes(
                range = [0, max_eff]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,key=f'line1{fac}',config = config)
    
    max_thuongnhom = max(df["TONG_THUONG_NHOM"].max() for df in df_nhom_list) * 1.2
    for i, fac in enumerate(nha_may):
        with cols2[i]:
            df_nhom_fac = df_nhom_list[i]
            fig = px.line(
                df_nhom_fac,
                x="NGAY",
                y="TONG_THUONG_NHOM",
                color='NHOM',
                text='Thưởng nhóm'
                )
            fig.update_xaxes(
                dtick = 'D1',
                tickformat = '%d/%m'
            )
            fig.update_layout(
                title = f'Tổng tiền thưởng nhóm theo ngày {fac}',
                xaxis_title = "Ngày",
                yaxis_title = "Thưởng nhóm",
                legend_title = 'Nhóm'
            )
            fig.update_traces(
                textposition = 'top center'
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,key=f'qc{fac}',config = config)
            
    with st.expander("Dữ liệu thưởng nhóm chi tiết"):
        st.dataframe(df_nhom)
        
if bao_cao == 'Công nhân Là':
    df = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                           TONG_TGLV,EFF_TB,TONG_THUONG,SO_NGAY
                           FROM TONG_HOP_TIEN_THUONG_HIEU_SUAT_TGLV_LA WHERE NHA_MAY IN ({', '.join(f'\'{item}\'' for item in nha_may)})
                           """)
    df['XUONG'] = df['CHUYEN'].apply(lambda x: x[:1] +'TNC' if 'TNC' in x \
                                    else x[:1] + 'NDC' if 'NDC' in x \
                                        else x[:1] + 'P0' + x[1:2])
    df['CHUC_VU'] = df['CHUC_VU'].str.replace(r'là','Là',regex =True)
    nam = df['NAM'].sort_values(ascending=False).unique()
    sel_nam = st.sidebar.selectbox("Chọn năm",options=nam)
    df_fitered = df[df['NAM'] == sel_nam]
    thang = df_fitered['THANG'].sort_values(ascending=False).unique()
    sel_thang = st.sidebar.selectbox("Chọn tháng",options=thang)
    df_fitered = df_fitered[df_fitered['THANG'] == sel_thang]
    so_ngay_min = df_fitered['SO_NGAY'].min()
    so_ngay_max = df_fitered['SO_NGAY'].max()
    so_ngay_from,so_ngay_to = st.sidebar.slider("Chọn số ngày làm việc",value=(so_ngay_min,so_ngay_max))
    df_fitered = df_fitered.query("SO_NGAY >= @so_ngay_from and SO_NGAY <= @so_ngay_to")
    df_fitered['Tiền thưởng'] = df_fitered['TONG_THUONG'].apply(lambda x: f"{x/1_000:,.0f} nghìn")
    df_fitered['Hiệu suất'] = df_fitered['EFF_TB'].apply(lambda x: f"{x:,.0%}")
    
    df_list = [df_fitered[df_fitered['NHA_MAY'] == fac] for fac in nha_may]
    cols = st.columns(len(nha_may))
    
    max_thuong = max(df["TONG_THUONG"].max() for df in df_list) * 1.2
    max_eff = max(df["EFF_TB"].max() for df in df_list) * 1.2
    
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_fac = df_list[i]
            tong_thuong = df_fac['TONG_THUONG'].sum()
            st.metric(f"Tổng tiền thưởng nhóm Là {fac}",value=f"{tong_thuong:,.0f}")
            ###
            fig = px.scatter(df_fac,
                            x='EFF_TB',
                            y='TONG_THUONG',
                            color='CHUC_VU',
                            size='TONG_TGLV',
                            hover_data={
                                'MST' : True,
                                'HO_TEN' : True,
                                'TONG_TGLV' : True,
                                'Hiệu suất' : True,
                                'Tiền thưởng' : True,
                                'TONG_THUONG' : False,
                                'EFF_TB' : False,
                                'CHUC_VU' : True
                            }
                            )
            fig.update_layout(
                title = f'Phân bổ tiền thưởng theo hiệu suất cá nhân {fac}',
                xaxis_title = 'Hiệu suất cá nhân',
                yaxis_title = 'Tiền thưởng'
            )
            fig.update_xaxes(
                tickformat = ',.0%'
            )
            fig.update_traces(
                marker = dict(line = dict(width = 1, color = 'white'))
            )
            fig.update_yaxes(
                range = [0, max_thuong]
            )
            fig.update_xaxes(
                range=[0, max_eff]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,config = config)
    
    max_thuong_2 = max(df.groupby(by=['XUONG','CHUC_VU'])["TONG_THUONG"].mean().max() for df in df_list) * 1.2
    
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_fac = df_list[i]
            tb_thuong = df_fac['TONG_THUONG'].mean()
            st.metric(f"Trung bình tiền thưởng công nhân Là {fac}",value=f"{tb_thuong:,.0f}")
            ###
            df_chuc_vu = df_fac.groupby(by=['XUONG','CHUC_VU']).agg({'TONG_THUONG' : 'mean'}).reset_index()
            df_chuc_vu['Trung bình thưởng'] = df_chuc_vu['TONG_THUONG'].apply(lambda x: f"{x:,.0f}")
            ds_chuc_vu = ['Công nhân Là']
            df_chuc_vu = df_chuc_vu[df_chuc_vu['CHUC_VU'].isin(ds_chuc_vu)]
            fig = px.bar(
                df_chuc_vu,
                x='CHUC_VU',
                y='TONG_THUONG',
                color='XUONG',
                barmode='group',
                text='Trung bình thưởng'
            )
            fig.update_layout(
                title = f"Trung bình tiền thưởng theo chức danh {fac}",
                xaxis_title = 'Chức danh',
                yaxis_title = 'Trung bình tiền thưởng',
                legend_title = 'Xưởng'
            )
            fig.update_traces(
                textposition = 'outside'
            )
            fig.update_yaxes(
                range=[0, max_thuong_2]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,config = config)
            
    with st.expander("Dữ liệu chi tiết"):
        st.dataframe(df_fitered)
    st.markdown("---")
    
    cols2 = st.columns(len(nha_may))
    df_nhom = get_data(DB='INCENTIVE',query=f"""
                           SELECT * FROM THUONG_NHOM_LA_HANG_NGAY WHERE NHA_MAY IN ({', '.join(f'\'{item}\'' for item in nha_may)}) AND CHUYEN NOT LIKE '%99'
                           ORDER BY NGAY,CHUYEN
                           """)
    df_nhom['NAM'] = df_nhom['NGAY'].apply(lambda x: x[:4])
    df_nhom['THANG'] = df_nhom['NGAY'].apply(lambda x: x[5:7])
    df_nhom= df_nhom.query("NAM == @sel_nam and THANG == @sel_thang")
    df_nhom['Hiệu suất'] = df_nhom['EFF'].apply(lambda x: f"{x:,.0%}")
    df_nhom['Thưởng nhóm'] = df_nhom['TONG_THUONG_NHOM'].apply(lambda x: f"{x/1_000:,.0f} nghìn")
    
    df_nhom_list = [df_nhom[df_nhom['NHA_MAY'] == fac] for fac in nha_may]
    
    max_eff = max(df["EFF"].max() for df in df_nhom_list) * 1.1

    for i, fac in enumerate(nha_may):
        with cols2[i]:
            df_fac = df_nhom_list[i]
            fig = px.line(
                df_fac,
                x="NGAY",
                y="EFF",
                color= 'CHUYEN',
                text=  'Hiệu suất'
            )
            fig.update_xaxes(
                dtick = 'D1',
                tickformat = '%d/%m'
            )
            fig.update_layout(
                title = f'Hiệu suất từng nhóm theo ngày {fac}',
                xaxis_title = "Ngày",
                yaxis_title = "Hiệu suất",
                legend_title = 'Nhóm'
            )
            fig.update_traces(
                textposition = 'top center'
            )
            fig.update_yaxes(
                range = [0, max_eff]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,key=f'line1{fac}',config = config)
    
    max_thuong_3 = max(df["TONG_THUONG_NHOM"].max() for df in df_nhom_list) * 1.1
    for i, fac in enumerate(nha_may):
        with cols2[i]:
            df_fac = df_nhom_list[i]
            fig = px.line(
                df_fac,
                x="NGAY",
                y="TONG_THUONG_NHOM",
                color= 'CHUYEN',
                text=  'Thưởng nhóm'
                )
            fig.update_xaxes(
                dtick = 'D1',
                tickformat = '%d/%m'
            )
            fig.update_layout(
                title = f'Tổng tiền thưởng nhóm theo ngày {fac}',
                xaxis_title = "Ngày",
                yaxis_title = "Thưởng nhóm",
                legend_title = 'Nhóm'
            )
            fig.update_traces(
                textposition = 'top center'
            )
            fig.update_yaxes(
                range = [0, max_thuong_3]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,key=f'line2{fac}',config = config)

    with st.expander("Dữ liệu thưởng nhóm chi tiết"):
        st.dataframe(df_nhom)
        
if bao_cao == 'Công nhân QC2':
    df = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                           TONG_TGLV,EFF_TB,TONG_THUONG,SO_NGAY
                           FROM TONG_HOP_TIEN_THUONG_HIEU_SUAT_TGLV_QC2 WHERE NHA_MAY IN ({', '.join(f'\'{item}\'' for item in nha_may)})
                           """)
    df['CHUC_VU']=df['CHUC_VU'].str.replace(r'là','Là',regex=True)
    df['XUONG'] = df['CHUYEN'].apply(lambda x: x[:1] +'TNC' if 'TNC' in x \
                                    else x[:1] + 'NDC' if 'NDC' in x \
                                        else x[:1] + 'P0' + x[1:2])
    nam = df['NAM'].sort_values(ascending=False).unique()
    sel_nam = st.sidebar.selectbox("Chọn năm",options=nam)
    df_fitered = df[df['NAM'] == sel_nam]
    thang = df_fitered['THANG'].sort_values(ascending=False).unique()
    sel_thang = st.sidebar.selectbox("Chọn tháng",options=thang)
    df_fitered = df_fitered[df_fitered['THANG'] == sel_thang]
    so_ngay_min = df_fitered['SO_NGAY'].min()
    so_ngay_max = df_fitered['SO_NGAY'].max()
    so_ngay_from,so_ngay_to = st.sidebar.slider("Chọn số ngày làm việc",value=(so_ngay_min,so_ngay_max))
    df_fitered = df_fitered.query("SO_NGAY >= @so_ngay_from and SO_NGAY <= @so_ngay_to")
    df_fitered['Tiền thưởng'] = df_fitered['TONG_THUONG'].apply(lambda x: f"{x/1_000:,.0f} nghìn")
    df_fitered['Hiệu suất'] = df_fitered['EFF_TB'].apply(lambda x: f"{x:,.0%}")
    
    df_list = [df_fitered[df_fitered['NHA_MAY'] == fac] for fac in nha_may]
    cols = st.columns(len(nha_may))
    
    max_thuong = max(df["TONG_THUONG"].max() for df in df_list) * 1.2
    max_eff = max(df["EFF_TB"].max() for df in df_list) * 1.5
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_fac = df_list[i]
            tong_thuong = df_fac['TONG_THUONG'].sum()
            st.metric("Tổng tiền thưởng nhóm QC2",value=f"{tong_thuong:,.0f}")

            fig = px.scatter(df_fac,
                            x='EFF_TB',
                            y='TONG_THUONG',
                            color='CHUC_VU',
                            size='TONG_TGLV',
                            hover_data={
                                'MST' : True,
                                'HO_TEN' : True,
                                'TONG_TGLV' : True,
                                'Hiệu suất' : True,
                                'Tiền thưởng' : True,
                                'TONG_THUONG' : False,
                                'EFF_TB' : False,
                                'CHUC_VU' : True
                            }
                            )
            fig.update_layout(
                title = f'Phân bổ tiền thưởng theo hiệu suất cá nhân {fac}',
                xaxis_title = 'Hiệu suất cá nhân',
                yaxis_title = 'Tiền thưởng'
            )
            fig.update_xaxes(
                tickformat = ',.0%'
            )
            fig.update_traces(
                marker = dict(line = dict(width = 1, color = 'white'))
            )
            fig.update_yaxes(
                range = [0, max_thuong]
            )
            fig.update_xaxes(
                range = [0, max_eff]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,key=f"line1{fac}",config = config)
    
    max_thuong_2 = max(df.groupby(by=['XUONG','CHUC_VU'])["TONG_THUONG"].mean().max() for df in df_list) * 1.2
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_fac = df_list[i]
            tb_thuong = df_fac['TONG_THUONG'].mean()
            st.metric("Trung bình tiền thưởng công nhân QC2",value=f"{tb_thuong:,.0f}")
            ###
            df_chuc_vu = df_fac.groupby(by=['XUONG','CHUC_VU']).agg({'TONG_THUONG' : 'mean'}).reset_index()
            df_chuc_vu['Trung bình thưởng'] = df_chuc_vu['TONG_THUONG'].apply(lambda x: f"{x:,.0f}")
            ds_chuc_vu = ['Công nhân kiểm hàng Là']
            df_chuc_vu = df_chuc_vu[df_chuc_vu['CHUC_VU'].isin(ds_chuc_vu)]
            fig = px.bar(
                df_chuc_vu,
                x='CHUC_VU',
                y='TONG_THUONG',
                color='XUONG',
                barmode='group',
                text='Trung bình thưởng'
            )
            fig.update_layout(
                title = f"Trung bình tiền thưởng theo chức danh {fac}",
                xaxis_title = 'Chức danh',
                yaxis_title = 'Trung bình tiền thưởng',
                legend_title = 'Xưởng'
            )
            fig.update_traces(
                textposition = 'outside'
            )
            fig.update_yaxes(
                range = [0, max_thuong_2]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,config = config)
            
    with st.expander("Dữ liệu chi tiết"):
        st.dataframe(df_fitered)
    st.markdown("---")
    
    df_nhom = get_data(DB='INCENTIVE',query=f"""
                           SELECT * FROM THUONG_NHOM_QC2_HANG_NGAY WHERE NHA_MAY IN ({', '.join(f'\'{item}\'' for item in nha_may)}) AND NHOM NOT LIKE '%99'
                           ORDER BY NGAY,NHOM
                           """)
    df_nhom['NAM'] = df_nhom['NGAY'].apply(lambda x: x[:4])
    df_nhom['THANG'] = df_nhom['NGAY'].apply(lambda x: x[5:7])
    df_nhom= df_nhom.query("NAM == @sel_nam and THANG == @sel_thang")
    df_nhom['Hiệu suất'] = df_nhom['EFF'].apply(lambda x: f"{x:,.0%}")
    df_nhom['Thưởng nhóm'] = df_nhom['TONG_THUONG_NHOM'].apply(lambda x: f"{x/1_000:,.0f} nghìn")
    
    df_nhom_list = [df_nhom[df_nhom['NHA_MAY'] == fac] for fac in nha_may]
    cols2 = st.columns(len(nha_may))
    
    max_eff = max(df["EFF"].max() for df in df_nhom_list) * 1.2
    for i, fac in enumerate(nha_may):
        with cols2[i]:
            df_fac = df_nhom_list[i]
            fig = px.line(
                df_fac,
                x="NGAY",
                y="EFF",
                color= 'NHOM',
                text=  'Hiệu suất'
            )
            fig.update_xaxes(
                dtick = 'D1',
                tickformat = '%d/%m'
            )
            fig.update_layout(
                title = f'Hiệu suất từng nhóm theo ngày {fac}',
                xaxis_title = "Ngày",
                yaxis_title = "Hiệu suất",
                legend_title = 'Nhóm'
            )
            fig.update_traces(
                textposition = 'top center'
            )
            fig.update_yaxes(
                range = [0, max_eff]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,key=f'line1_nhom_{fac}',config = config)
            
    max_thuong_3 = max(df["TONG_THUONG_NHOM"].max() for df in df_nhom_list) * 1.2
    for i, fac in enumerate(nha_may):
        with cols2[i]:
            df_fac = df_nhom_list[i]
            fig = px.line(
                df_fac,
                x="NGAY",
                y="TONG_THUONG_NHOM",
                color= 'NHOM',
                text=  'Thưởng nhóm'
            )
            fig.update_xaxes(
                dtick = 'D1',
                tickformat = '%d/%m'
            )
            fig.update_layout(
                title = f'Tổng tiền thưởng nhóm theo ngày {fac}',
                xaxis_title = "Ngày",
                yaxis_title = "Thưởng nhóm",
                legend_title = 'Nhóm'
            )
            fig.update_traces(
                textposition = 'top center'
            )
            fig.update_yaxes(
                range = [0, max_thuong_3]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,key=f'line2_nhom{fac}',config = config)
    with st.expander("Dữ liệu thưởng nhóm chi tiết"):
        st.dataframe(df_nhom)

if bao_cao == 'Công nhân đóng gói':
    df = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                           TGLV as TONG_TGLV,TONG_THUONG,SO_NGAY
                           FROM TONG_HOP_TGLV_TONG_THUONG_CN_DONG_GOI WHERE NHA_MAY IN ({', '.join(f'\'{item}\'' for item in nha_may)})
                           """)
    df['XUONG'] = df['CHUYEN'].apply(lambda x: x[:1] +'TNC' if 'TNC' in x \
                                    else x[:1] + 'NDC' if 'NDC' in x \
                                        else x[:1] + 'P0' + x[1:2])
    nam = df['NAM'].sort_values(ascending=False).unique()
    sel_nam = st.sidebar.selectbox("Chọn năm",options=nam)
    df_fitered = df[df['NAM'] == sel_nam]
    thang = df_fitered['THANG'].sort_values(ascending=False).unique()
    sel_thang = st.sidebar.selectbox("Chọn tháng",options=thang)
    df_fitered = df_fitered[df_fitered['THANG'] == sel_thang]
    so_ngay_min = df_fitered['SO_NGAY'].min()
    so_ngay_max = df_fitered['SO_NGAY'].max()
    so_ngay_from,so_ngay_to = st.sidebar.slider("Chọn số ngày làm việc",value=(so_ngay_min,so_ngay_max))
    df_fitered = df_fitered.query("SO_NGAY >= @so_ngay_from and SO_NGAY <= @so_ngay_to")
    df_fitered['Tiền thưởng'] = df_fitered['TONG_THUONG'].apply(lambda x: f"{x/1_000:,.0f} nghìn")
    
    df_list = [df_fitered[df_fitered['NHA_MAY'] == fac] for fac in nha_may]
    cols = st.columns(len(nha_may))
    
    max_thuong = max(df["TONG_THUONG"].max() for df in df_list) * 1.2
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_fac = df_list[i]
            tong_thuong = df_fac['TONG_THUONG'].sum()
            st.metric(f"Tổng tiền thưởng nhóm đóng gói {fac}",value=f"{tong_thuong:,.0f}")
            ###
            fig = px.scatter(df_fac,
                x='SO_NGAY',
                y='TONG_THUONG',
                color='CHUC_VU',
                size='TONG_TGLV',
                hover_data={
                    'MST' : True,
                    'HO_TEN' : True,
                    'TONG_TGLV' : True,
                    'Tiền thưởng' : True,
                    'TONG_THUONG' : False
            })
            fig.update_layout(
                title = f'Phân bổ tiền thưởng theo số ngày làm việc {fac}',
                xaxis_title = 'Số ngày làm việc',
                yaxis_title = 'Tiền thưởng',
                legend_title = 'Chức danh'
            )
            fig.update_traces(
                marker = dict(line = dict(width = 1, color = 'white'))
            )
            fig.update_yaxes(
                range = [0, max_thuong]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,config = config)
    
    max_thuong_2 = max(df.groupby(by=['XUONG','CHUC_VU'])["TONG_THUONG"].mean().max() for df in df_list) * 1.2
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_fac = df_list[i]
            tb_thuong = df_fac['TONG_THUONG'].mean()
            st.metric(f"Trung bình tiền thưởng công nhân đóng gói {fac}",value=f"{tb_thuong:,.0f}")
            ###
            df_chuc_vu = df_fac.groupby(by=['XUONG','CHUC_VU']).agg({'TONG_THUONG' : 'mean'}).reset_index()
            df_chuc_vu['Trung bình thưởng'] = df_chuc_vu['TONG_THUONG'].apply(lambda x: f"{x:,.0f}")
            ds_chuc_vu = ['Công nhân đóng gói']
            df_chuc_vu = df_chuc_vu[df_chuc_vu['CHUC_VU'].isin(ds_chuc_vu)]
            fig = px.bar(
                df_chuc_vu,
                x='CHUC_VU',
                y='TONG_THUONG',
                color='XUONG',
                barmode='group',
                text='Trung bình thưởng'
            )
            fig.update_layout(
                title = f"Trung bình tiền thưởng theo chức danh {fac}",
                xaxis_title = 'Chức danh',
                yaxis_title = 'Trung bình tiền thưởng',
                legend_title = 'Xưởng'
            )
            fig.update_traces(
                textposition = 'outside'
            )
            fig.update_yaxes(
                range = [0, max_thuong_2]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,config = config)
        
    with st.expander("Dữ liệu chi tiết"):
        st.dataframe(df_fitered)
    st.markdown("---")
    
    df_nhom = get_data(DB='INCENTIVE',query=f"""
                           SELECT * FROM THUONG_NHOM_DONG_GOI_HANG_NGAY WHERE NHA_MAY IN ({', '.join(f'\'{item}\'' for item in nha_may)}) AND NHOM NOT LIKE '%99'
                           ORDER BY NGAY,NHOM
                           """)
    df_nhom['NAM'] = df_nhom['NGAY'].apply(lambda x: x[:4])
    df_nhom['THANG'] = df_nhom['NGAY'].apply(lambda x: x[5:7])
    df_nhom= df_nhom.query("NAM == @sel_nam and THANG == @sel_thang")
    df_nhom['Hiệu suất'] = df_nhom['EFF'].apply(lambda x: f"{x:,.0%}")
    df_nhom['Thưởng nhóm'] = df_nhom['TONG_THUONG_NHOM'].apply(lambda x: f"{x/1_000:,.0f} nghìn")
    ###
    df_nhom_list = [df_nhom[df_nhom['NHA_MAY'] == fac] for fac in nha_may]
    cols2 = st.columns(len(nha_may))
    
    max_eff_2 = max(df["EFF"].max() for df in df_nhom_list) * 1.2
    for i, fac in enumerate(nha_may):
        with cols2[i]:
            df_fac = df_nhom_list[i]
            fig = px.line(
                df_fac,
                x="NGAY",
                y="EFF",
                color= 'NHOM',
                text=  'Hiệu suất'
            )
            fig.update_xaxes(
                dtick = 'D1',
                tickformat = '%d/%m'
            )
            fig.update_layout(
                title = f'Hiệu suất từng nhóm theo ngày {fac}',
                xaxis_title = "Ngày",
                yaxis_title = "Hiệu suất",
                legend_title = 'Nhóm'
            )
            fig.update_traces(
                textposition = 'top center'
            )
            fig.update_yaxes(
                range = [0, max_eff_2]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,key=f'line1{fac}',config = config)
    
    max_thuong_3 = max(df["TONG_THUONG_NHOM"].max() for df in df_nhom_list) * 1.2
    for i, fac in enumerate(nha_may):
        with cols2[i]:
            df_fac = df_nhom_list[i]
            fig = px.line(
                df_fac,
                x="NGAY",
                y="TONG_THUONG_NHOM",
                color= 'NHOM',
                text=  'Thưởng nhóm'
            )
            fig.update_xaxes(
                dtick = 'D1',
                tickformat = '%d/%m'
            )
            fig.update_layout(
                title = f'Hiệu suất từng nhóm theo ngày {fac}',
                xaxis_title = "Ngày",
                yaxis_title = "Thưởng nhóm",
                legend_title = 'Nhóm'
            )
            fig.update_traces(
                textposition = 'top center'
            )
            fig.update_yaxes(
                range = [0, max_thuong_3]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,key=f'line2{fac}',config = config)
    with st.expander("Dữ liệu thưởng nhóm chi tiết"):
        st.dataframe(df_nhom)
        
if bao_cao == 'Công nhân NDC':
    df = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                           TGLV as TONG_TGLV,TONG_THUONG,SO_NGAY
                           FROM TONG_HOP_TGLV_TONG_THUONG_CN_NDC WHERE NHA_MAY IN ({', '.join(f'\'{item}\'' for item in nha_may)})
                           """)
    df['XUONG'] = df['CHUYEN'].apply(lambda x: x[:1] +'TNC' if 'TNC' in x \
                                    else x[:1] + 'NDC' if 'NDC' in x \
                                        else x[:1] + 'P0' + x[1:2])
    nam = df['NAM'].sort_values(ascending=False).unique()
    sel_nam = st.sidebar.selectbox("Chọn năm",options=nam)
    df_fitered = df[df['NAM'] == sel_nam]
    thang = df_fitered['THANG'].sort_values(ascending=False).unique()
    sel_thang = st.sidebar.selectbox("Chọn tháng",options=thang)
    df_fitered = df_fitered[df_fitered['THANG'] == sel_thang]
    so_ngay_min = df_fitered['SO_NGAY'].min()
    so_ngay_max = df_fitered['SO_NGAY'].max()
    so_ngay_from,so_ngay_to = st.sidebar.slider("Chọn số ngày làm việc",value=(so_ngay_min,so_ngay_max))
    df_fitered = df_fitered.query("SO_NGAY >= @so_ngay_from and SO_NGAY <= @so_ngay_to")
    df_fitered['Tiền thưởng'] = df_fitered['TONG_THUONG'].apply(lambda x: f"{x/1_000:,.0f} nghìn")
    
    df_list = [df_fitered[df_fitered['NHA_MAY'] == fac] for fac in nha_may]
    cols = st.columns(len(nha_may))
    
    max_thuong = max(df["TONG_THUONG"].max() for df in df_list) * 1.2
    max_ngay = max(df["SO_NGAY"].max() for df in df_list) * 1.2
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_fac = df_list[i]
            tong_thuong = df_fac['TONG_THUONG'].sum()
            st.metric(f"Tổng tiền thưởng nhóm dò kim {fac}",value=f"{tong_thuong:,.0f}")

            fig = px.scatter(df_fac,
                x='SO_NGAY',
                y='TONG_THUONG',
                color='CHUC_VU',
                size='TONG_TGLV',
                hover_data={
                    'MST' : True,
                    'HO_TEN' : True,
                    'TONG_TGLV' : True,
                    'Tiền thưởng' : True,
                    'TONG_THUONG' : False
            })
            fig.update_layout(
                title = f'Phân bổ tiền thưởng theo số ngày làm việc {fac}',
                xaxis_title = 'Số ngày làm việc',
                yaxis_title = 'Tiền thưởng',
                legend_title = 'Chức danh'
            )
            fig.update_traces(
                marker = dict(line = dict(width = 1, color = 'white'))
            )
            fig.update_yaxes(
                range = [0, max_thuong]
            )
            fig.update_xaxes(
                range = [0, max_ngay]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,config = config)
    
    max_tb_thuong = max(df.groupby(by=['XUONG','CHUC_VU'])["TONG_THUONG"].mean().max() for df in df_list) * 1.2
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_fac = df_list[i]
            tb_thuong = df_fac['TONG_THUONG'].mean()
            st.metric("Trung bình tiền thưởng công nhân dò kim",value=f"{tb_thuong:,.0f}")
            ###
            df_chuc_vu = df_fac.groupby(by=['XUONG','CHUC_VU']).agg({'TONG_THUONG' : 'mean'}).reset_index()
            df_chuc_vu['Trung bình thưởng'] = df_chuc_vu['TONG_THUONG'].apply(lambda x: f"{x:,.0f}")
            ds_chuc_vu = ['Công nhân dò kim']
            df_chuc_vu = df_chuc_vu[df_chuc_vu['CHUC_VU'].isin(ds_chuc_vu)]
            fig = px.bar(
                df_chuc_vu,
                x='CHUC_VU',
                y='TONG_THUONG',
                color='XUONG',
                barmode='group',
                text='Trung bình thưởng'
            )
            fig.update_layout(
                title = f"Trung bình tiền thưởng theo chức danh {fac}",
                xaxis_title = 'Chức danh',
                yaxis_title = 'Trung bình tiền thưởng',
                legend_title = 'Xưởng'
            )
            fig.update_traces(
                textposition = 'outside'
            )
            fig.update_yaxes(
                range = [0, max_tb_thuong]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,config = config)
        
    with st.expander("Dữ liệu chi tiết"):
        st.dataframe(df_fitered)
    st.markdown("---")
    
    df_nhom = get_data(DB='INCENTIVE',query=f"""
                           SELECT * FROM THUONG_NHOM_NDC_HANG_NGAY WHERE NHA_MAY IN ({', '.join(f'\'{item}\'' for item in nha_may)}) AND NHOM NOT LIKE '%99'
                           ORDER BY NGAY,NHOM
                           """)
    df_nhom['NAM'] = df_nhom['NGAY'].apply(lambda x: x[:4])
    df_nhom['THANG'] = df_nhom['NGAY'].apply(lambda x: x[5:7])
    df_nhom= df_nhom.query("NAM == @sel_nam and THANG == @sel_thang")
    df_nhom['Thưởng nhóm'] = df_nhom['THUONG_NHOM'].apply(lambda x: f"{x/1_000:,.0f} nghìn")
    
    df_nhom_list = [df_nhom[df_nhom['NHA_MAY'] == fac] for fac in nha_may]
    cols2 = st.columns(len(nha_may))
    
    max_thuong_nhom = max(df["THUONG_NHOM"].max() for df in df_nhom_list) * 1.2
    for i, fac in enumerate(nha_may):
        with cols2[i]:
            df_fac = df_nhom_list[i]
            fig = px.line(
                df_fac,
                x="NGAY",
                y="THUONG_NHOM",
                color= 'NHOM',
                text=  'Thưởng nhóm'
            )
            fig.update_xaxes(
                dtick = 'D1',
                tickformat = '%d/%m'
            )
            fig.update_layout(
                title = f'Hiệu suất từng nhóm theo ngày {fac}',
                xaxis_title = "Ngày",
                yaxis_title = "Thưởng nhóm",
                legend_title = 'Nhóm'
            )
            fig.update_traces(
                textposition = 'top center'
            )
            fig.update_yaxes (
                range = [0, max_thuong_nhom]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,key=f'line2{fac}',config = config)
    with st.expander("Dữ liệu thưởng nhóm chi tiết"):
        st.dataframe(df_nhom)
        
if bao_cao == 'Công nhân phụ':
    df = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                           TGLV as TONG_TGLV,TONG_THUONG,SO_NGAY
                           FROM TONG_HOP_TGLV_TONG_THUONG_CN_PHU WHERE NHA_MAY IN ({', '.join(f'\'{item}\'' for item in nha_may)})
                           """)
    df['XUONG'] = df['CHUYEN'].apply(lambda x: x[:1] +'TNC' if 'TNC' in x \
                                    else x[:1] + 'NDC' if 'NDC' in x \
                                        else x[:1] + 'P0' + x[1:2])
    nam = df['NAM'].sort_values(ascending=False).unique()
    sel_nam = st.sidebar.selectbox("Chọn năm",options=nam)
    df_fitered = df[df['NAM'] == sel_nam]
    thang = df_fitered['THANG'].sort_values(ascending=False).unique()
    sel_thang = st.sidebar.selectbox("Chọn tháng",options=thang)
    df_fitered = df_fitered[df_fitered['THANG'] == sel_thang]
    so_ngay_min = df_fitered['SO_NGAY'].min()
    so_ngay_max = df_fitered['SO_NGAY'].max()
    so_ngay_from,so_ngay_to = st.sidebar.slider("Chọn số ngày làm việc",value=(so_ngay_min,so_ngay_max))
    df_fitered = df_fitered.query("SO_NGAY >= @so_ngay_from and SO_NGAY <= @so_ngay_to")
    df_fitered['Tiền thưởng'] = df_fitered['TONG_THUONG'].apply(lambda x: f"{x/1_000:,.0f} nghìn")
    
    df_list = [df_fitered[df_fitered['NHA_MAY'] == fac] for fac in nha_may]
    cols = st.columns(len(nha_may))
    
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_fac = df_list[i]
            tong_thuong = df_fac['TONG_THUONG'].sum()
            st.metric(f"Tổng tiền thưởng nhóm công nhân phụ {fac}",value=f"{tong_thuong:,.0f}")
            
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_fac = df_list[i]
            tb_thuong = df_fac['TONG_THUONG'].mean()
            st.metric(f"Trung bình tiền thưởng công nhân phụ {fac}",value=f"{tb_thuong:,.0f}")
    
    max_thuong = max(df["TONG_THUONG"].max() for df in df_list) * 1.2
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_fac = df_list[i]    
            fig = px.scatter(df_fac,
                x='TONG_TGLV',
                y='TONG_THUONG',
                color='CHUC_VU',
                size='SO_NGAY',
                hover_data={
                    'MST' : True,
                    'HO_TEN' : True,
                    'TONG_TGLV' : True,
                    'Tiền thưởng' : True,
                    'TONG_THUONG' : False
            })
            fig.update_layout(
                title = f'Phân bổ tiền thưởng theo số giờ làm việc {fac}',
                xaxis_title = 'Số giờ làm việc',
                yaxis_title = 'Tiền thưởng',
                legend_title = 'Chức danh'
            )
            fig.update_traces(
                marker = dict(line = dict(width = 1, color = 'white'))
            )
            fig.update_yaxes(
                range = [0, max_thuong]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,config = config)
    
    max_thuong_3 = max(df.groupby(by=['XUONG','CHUC_VU'])["TONG_THUONG"].mean().max() for df in df_list) * 1.2
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_fac = df_list[i]    
            df_chuc_vu = df_fac.groupby(by=['XUONG','CHUC_VU']).agg({'TONG_THUONG' : 'mean'}).reset_index()
            df_chuc_vu['Trung bình thưởng'] = df_chuc_vu['TONG_THUONG'].apply(lambda x: f"{x:,.0f}")
            fig = px.bar(
                df_fac,
                x='CHUC_VU',
                y='TONG_THUONG',
                color='XUONG',
                barmode='group',
                # text='Trung bình thưởng'
            )
            fig.update_layout(
                title = f"Trung bình tiền thưởng theo chức danh {fac}",
                xaxis_title = 'Chức danh',
                yaxis_title = 'Trung bình tiền thưởng',
                legend_title = 'Xưởng'
            )
            fig.update_traces(
                textposition = 'outside'
            )
            fig.update_yaxes(
                range = [0, max_thuong_3]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,config = config)
            
    with st.expander("Dữ liệu chi tiết"):
        st.dataframe(df_fitered)
        
if bao_cao == 'Quản lý':
    df = get_data(DB='INCENTIVE',query=f"""
                           SELECT NHA_MAY,NAM,THANG,MST,HO_TEN,CHUYEN,CHUC_VU,
                           TGLV as TONG_TGLV,TONG_THUONG,SO_NGAY
                           FROM TONG_HOP_TGLV_TONG_THUONG_QUAN_LY WHERE NHA_MAY IN ({', '.join(f'\'{item}\'' for item in nha_may)})
                           """)
    df['XUONG'] = df['CHUYEN'].apply(lambda x: x[:1] +'TNC' if 'TNC' in x \
                                    else x[:1] + 'NDC' if 'NDC' in x \
                                        else x[:1] + 'P0' + x[1:2])
    nam = df['NAM'].sort_values(ascending=False).unique()
    sel_nam = st.sidebar.selectbox("Chọn năm",options=nam)
    df_fitered = df[df['NAM'] == sel_nam]
    thang = df_fitered['THANG'].sort_values(ascending=False).unique()
    sel_thang = st.sidebar.selectbox("Chọn tháng",options=thang)
    df_fitered = df_fitered[df_fitered['THANG'] == sel_thang]
    so_ngay_min = df_fitered['SO_NGAY'].min()
    so_ngay_max = df_fitered['SO_NGAY'].max()
    so_ngay_from,so_ngay_to = st.sidebar.slider("Chọn số ngày làm việc",value=(so_ngay_min,so_ngay_max))
    df_fitered = df_fitered.query("SO_NGAY >= @so_ngay_from and SO_NGAY <= @so_ngay_to")
    df_fitered['Tiền thưởng'] = df_fitered['TONG_THUONG'].apply(lambda x: f"{x/1_000:,.0f} nghìn")
    
    df_list = [df_fitered[df_fitered['NHA_MAY'] == fac] for fac in nha_may]
    cols = st.columns(len(nha_may))

    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_fac = df_list[i]  
            tong_thuong = df_fac['TONG_THUONG'].sum()
            st.metric(f"Tổng tiền thưởng nhóm quản lý {fac}",value=f"{tong_thuong:,.0f}")
            
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_fac = df_list[i]  
            tb_thuong = df_fac['TONG_THUONG'].mean()
            st.metric(f"Trung bình tiền thưởng quản lý {fac}",value=f"{tb_thuong:,.0f}")
    
    max_thuong = max(df["TONG_THUONG"].max() for df in df_list) * 1.2
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_fac = df_list[i] 
            fig = px.scatter(df_fac,
                x='TONG_TGLV',
                y='TONG_THUONG',
                color='CHUC_VU',
                size='SO_NGAY',
                hover_data={
                    'MST' : True,
                    'HO_TEN' : True,
                    'TONG_TGLV' : True,
                    'Tiền thưởng' : True,
                    'TONG_THUONG' : False
            })
            fig.update_layout(
                title = f'Phân bổ tiền thưởng theo số giờ làm việc {fac}',
                xaxis_title = 'Số giờ làm việc',
                yaxis_title = 'Tiền thưởng',
                legend_title = 'Chức danh'
            )
            fig.update_traces(
                marker = dict(line = dict(width = 1, color = 'white'))
            )
            fig.update_yaxes(
                range = [0, max_thuong]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,config = config)
    
    max_thuong_tb = max(df.groupby(by=['XUONG','CHUC_VU'])["TONG_THUONG"].mean().max() for df in df_list) * 1.2
    for i, fac in enumerate(nha_may):
        with cols[i]:
            df_fac = df_list[i] 
            df_chuc_vu = df_fac.groupby(by=['XUONG','CHUC_VU']).agg({'TONG_THUONG' : 'mean'}).reset_index()
            df_chuc_vu['Trung bình thưởng'] = df_chuc_vu['TONG_THUONG'].apply(lambda x: f"{x:,.0f}")
            fig = px.bar(
                df_chuc_vu,
                x='CHUC_VU',
                y='TONG_THUONG',
                color='XUONG',
                barmode='group',
                # text='Trung bình thưởng'
            )
            fig.update_layout(
                title = f"Trung bình tiền thưởng theo chức danh {fac}",
                xaxis_title = 'Chức danh',
                yaxis_title = 'Trung bình tiền thưởng',
                legend_title = 'Xưởng'
            )
            fig.update_traces(
                textposition = 'outside'
            )
            fig.update_yaxes(
                range = [0, max_thuong_tb]
            )
            fig.update_layout(dragmode="pan")

            st.plotly_chart(fig,use_container_width=True,config = config)
            
    with st.expander("Dữ liệu chi tiết"):
        st.dataframe(df_fitered)