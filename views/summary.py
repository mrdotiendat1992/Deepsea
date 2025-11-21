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
from io import BytesIO
import warnings
warnings.filterwarnings("ignore")

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

df1 = get_data('DW','SELECT * FROM ETS_5 WHERE WORKDATE < CAST(GETDATE() AS DATE)')
min_date = df1['WorkDate'].min()
max_date = df1['WorkDate'].max()

df1= df1.groupby(by=['WorkDate','Line']).agg({
    'Total_Qty':'sum',
    'SAH_A' : 'sum'
})

df2 = get_data('DW','SELECT * FROM PPC')
#st.dataframe(df2)
df3 = get_data('DW',"SELECT * FROM HR_INCLUDE_TNC WHERE KOIS = 'K' AND WORKDATE >= '2024-09-01'")
# st.dataframe(df3)

#ghép các bảng với nhau
df = pd.merge(df2,df1, on = ['WorkDate','Line'], how= 'outer')
df = pd.merge(df,df3, on=['WorkDate','Line'], how= 'left')
# xuất ra file excel

df = df.drop(columns='Fty')
df['Fty'] = 'NT' + df["Line"].str[0:1]

df = df.drop(columns='Unit')
df['Unit'] = df["Line"].str[0:1] + 'P0' + df["Line"].str[1:2]

#di chuyển cột
move_col = df.pop('Fty')
df.insert(0,'Fty',move_col)
move_col = df.pop('Unit')
df.insert(1,'Unit',move_col)
move_col = df.pop('Line')
df.insert(2,'Line',move_col)
move_col = df.pop('Style_P')
df.insert(2,'Style_P',move_col)
df.rename(columns={'Total_Qty':'Qty_A'}, inplace= True)
df.dropna(subset=['Fty'])
df = df[df['Fty'] != 'nan']

#chuyển cột WorkDate về dạng date
df['WorkDate'] = pd.to_datetime(df['WorkDate'], format='%Y-%m-%d')
df['WorkDate'] = df['WorkDate'].dt.date

df['Attn_P'] = df.apply(
    lambda 
    row: 0.9 if (row['Fty'] == 'NT1' and row['WorkDate'] < date(2025,11,10))
    else 0.91 if (row['Fty'] in ['NT2','NT3'] and row['WorkDate'] >= date(2025,5,1))
    else 0.93 if (row['Fty'] in ['NT2','NT3'])
    else 0.95, 
    axis=1)
df['Total_hours_P'] = df['Hours_P'] * df['Worker_P'] * df['Attn_P']
df['WS*Hours_A'] = df['Worker_A']*df['Hours_A']
# Lưu df ra file để kiểm tra

###########################
fty = ['NT1','NT2', 'NT3']
sel_fty = st.sidebar.multiselect("Chọn nhà máy:",options = fty,default=fty)
unit = df[df['Fty'].isin(sel_fty)]['Unit'].unique()
unit_sorted = sorted(unit, reverse= False)
sel_unit = st.sidebar.multiselect("Chọn xưởng:", options= unit, default= unit_sorted)

today = date.today() if date.today().day >1 else date.today() - timedelta(days=1)
first_day_of_month =  today.replace(day=1)
start_date = st.sidebar.date_input(label="Từ ngày:",value= first_day_of_month)

end_date = st.sidebar.date_input(label="Đến ngày:", value= max_date)

styles = df[
(df['Unit'].isin(sel_unit)) & 
(df['WorkDate'] >= start_date) & 
(df['WorkDate'] <= end_date)]['Style_P'].unique()
sel_style = st.sidebar.multiselect("Chọn Style:",options=styles,default=styles)

df_ppc = get_data("DW",f"SELECT * FROM PPC WHERE WORKDATE between '{start_date}' and '{end_date}' and line not like '%F%'")
df_ppc['Attn'] = df_ppc['Line'].apply(lambda x: 0.9 if str(x)[:1] == '1' else 0.93)
df_ppc['Total_hours_P'] = df_ppc['Hours_P'] * df_ppc['Worker_P'] * df_ppc['Attn']
df_ppc['Eff'] = df_ppc['SAH_P']/df_ppc['Total_hours_P']
df_ppc['Fty'] = 'NT' + df_ppc['Line'].str[:1]
df_ppc = df_ppc[df_ppc['Fty'].isin(sel_fty)]
df_ppc['Unit'] = df_ppc["Line"].str[0:1] + 'P0' + df_ppc["Line"].str[1:2]

st.markdown(f'<h1 class="centered-title">BÁO CÁO TỔNG HỢP</h1>', unsafe_allow_html=True)

df4 = df[
(df['Unit'].isin(sel_unit)) & 
(df['WorkDate'] >= start_date) & 
(df['WorkDate'] <= end_date) &
(df['Style_P'].isin(sel_style))]

df_tnc = get_data("INCENTIVE",f"""select hs.NHA_MAY, hs.SAH, hs.SO_GIO from HIEU_SUAT_CN_TNC01 hs
LEFT JOIN INCENTIVE.DBO.TRANG_THAI_DON_HANG dh
ON hs.CHUYEN = dh.CHUYEN AND hs.NGAY = dh.NGAY
WHERE hs.CHUYEN_HR LIKE '%TNC01%' AND dh.CHUYEN_MOI = N'TRÊN 2 THÁNG'
AND hs.NGAY BETWEEN '{start_date}' AND '{end_date}'""")

df_tnc = df_tnc[(df_tnc['NHA_MAY'].isin(sel_fty))]

df_ppc = df_ppc[(df_ppc['Unit'].isin(sel_unit)) & 
(df_ppc['Style_P'].isin(sel_style))]

Qty_A = df4[df4['Line'] != '11S02']['Qty_A'].sum()
Qty_A = df4['Qty_A'].sum()
Qty_P = df4['Qty_P'].sum()
SAH_A = df4['SAH_A'].sum() 
SAH_P = df4['SAH_P'].sum()
Total_hours_A = df4['Total_hours_A'].sum() 
Total_hours_P = df4['Total_hours_P'].sum()
Eff_A = SAH_A/Total_hours_A
Eff_P = SAH_P/Total_hours_P
Attn_A = df4['Total_hours_A'].sum()/(df4['WS*Hours_A']).sum()
Attn_P = df4['Attn_P'].mean()
Worker_A = df4[df4['WorkDate'] == end_date]['Worker_A'].sum()
Worker_P = df4[df4['WorkDate'] == end_date]['Worker_P'].sum()
Hour_A = df4['Total_hours_A'].sum()/df4['Worker_A'].sum()
Hour_P = df4['Total_hours_P'].sum()/df4['Worker_P'].sum()
SAH_CN_A = df4['SAH_A'].sum()/df4['Worker_A'].sum()
SAH_CN_P = df4['SAH_P'].sum()/df4['Worker_P'].sum()

df4['WorkDate'] = pd.to_datetime(df4['WorkDate'])
df_intern = df4[((df4['Line'] == '25S01') & (df4['WorkDate'] >= '2025-06-01') & (df4['WorkDate'] < '2025-08-01'))]

df4 = df4[~((df4['Line'] == '25S01') & (df4['WorkDate'] >= '2025-06-01') & (df4['WorkDate'] < '2025-08-01'))]
data = {
    'Sản lượng': [f'{Qty_P:,.0f}', f'{Qty_A:,.0f}'],
    'SAH': [f'{SAH_P:,.0f}', f'{SAH_A:,.0f}'],
    'Tổng TGLV': [f'{Total_hours_P:,.0f}', f'{Total_hours_A:,.0f}'],
    'Hiệu suất': [f'{Eff_P:,.1%}', f'{Eff_A:,.1%}'],
    'Tổng CN may': [f'{Worker_P:,.0f}', f'{Worker_A:,.0f}'],
    'Tỉ lệ đi làm': [f'{Attn_P:,.0%}', f'{Attn_A:,.1%}'],
    'Số giờ làm việc': [f'{Hour_P:,.1f}', f'{Hour_A:,.1f}'],
    'SAH/CN/Ngày': [f'{SAH_CN_P:,.1f}', f'{SAH_CN_A:,.1f}']
}
# df4.to_excel("df_summary_check.xlsx",index=False)
summary_df = pd.DataFrame(data, index=['Kế hoạch', 'Thực tế'])

# Hàm export Excel
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Summary', index=True)
        workbook = writer.book
        worksheet = writer.sheets['Summary']

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
    file_name=f"tong_hop_{now_str}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

cols = st.columns(4, gap= 'large')
with cols[0]:
    st.info('Sản lượng',icon= "👕" )
    st.metric(label= 'Mục tiêu',value= f'{Qty_P:,.0f}')
    st.metric(label= 'Thực tế',value= f'{Qty_A:,.0f}',delta= f'{(Qty_A-Qty_P):,.0f}')
    
    st.info('Tổng CN May',icon="👩‍💼")
    st.metric(label='Mục tiêu', value= f'{Worker_P:,.0f}')
    st.metric(label='Thực tế', value= f'{Worker_A:,.0f}',delta=f'{(Worker_A-Worker_P):,.0f}')
with cols[1]:
    st.info('Tổng SAH',icon= "💰" )
    st.metric(label= 'Mục tiêu',value= f'{SAH_P:,.0f}')
    st.metric(label= 'Thực tế',value= f'{SAH_A:,.0f}',delta= f'{(SAH_A-SAH_P):,.0f}')
    
    st.info('Tỉ lệ đi làm',icon="🏃")
    st.metric(label='Mục tiêu', value= f'{Attn_P:,.0%}')
    st.metric(label='Thực tế', value= f'{Attn_A:,.1%}',delta=f'{(Attn_A-Attn_P):,.1%}')
with cols[2]:
    st.info('Tổng TGLV',icon= "🕗" )
    st.metric(label= 'Mục tiêu',value= f'{Total_hours_P:,.0f}')
    st.metric(label= 'Thực tế',value= f'{Total_hours_A:,.0f}',delta=f'{(Total_hours_A-Total_hours_P):,.0f}')
    
    st.info('Số giờ làm việc',icon= "🕗" )
    st.metric(label= 'Mục tiêu',value= f'{Hour_P:,.1f}')
    st.metric(label= 'Thực tế',value= f'{Hour_A:,.1f}',delta=f'{(Hour_A-Hour_P):,.1f}')
with cols[3]:
    st.info('Hiệu suất',icon= "📈" )
    st.metric(label= 'Mục tiêu',value= f'{Eff_P:,.1%}')
    st.metric(label= 'Thực tế',value= f'{Eff_A:,.1%}',delta=f'{(Eff_A-Eff_P):,.1%}')
    
    st.info('SAH/CN/Ngày',icon= "💰" )
    st.metric(label= 'Mục tiêu',value= f'{SAH_CN_P:,.1f}')
    st.metric(label= 'Thực tế',value= f'{SAH_CN_A:,.1f}',delta=f'{(SAH_CN_A-SAH_CN_P):,.1f}')
# df5 = nhóm theo ngày    
st.markdown("---")
df5 = df4.groupby(by=df4['WorkDate']).agg({
'Qty_A' : 'sum',
'Qty_P' : 'sum',
'SAH_A' : 'sum',
'SAH_P' : 'sum',
'Total_hours_A' : 'sum',
'Total_hours_P' : 'sum'
    }).reset_index()

df5['SAH_A_formated']= df5['SAH_A'].apply(lambda x: f"{x:,.0f}")
df5 = df5.sort_values('WorkDate')

df6 = pd.melt(df5,id_vars= 'WorkDate',value_vars=['SAH_A','SAH_P'])
df6 = df6.sort_values('WorkDate')
df6 = df6.rename(columns={'value' : 'SAH','variable' : 'Chỉ số'})
df6 = df6.replace({'Chỉ số': {'SAH_A' : 'SAH thực tế','SAH_P' : 'SAH mục tiêu'}})
df6['SAH_formated'] = df6['SAH'].apply(lambda x: f"{x:,.0f}")
# st.dataframe(df6)
fig = px.line(df6,
                x= df6['WorkDate'],
                y= df6['SAH'],
                color=df6['Chỉ số'],
                color_discrete_map={
                    'SAH thực tế' : 'blue',
                    'SAH mục tiêu' : 'red'
                },
                text= df6['SAH_formated']
                )
fig.update_xaxes(
    dtick = 'D1',
    tickangle = 45,
    tickformat = "%d/%m"
)
fig.update_layout(
    xaxis_title = 'Ngày',
    yaxis_title = 'Tổng SAH',
    title = "Tổng SAH theo ngày"
)
fig.update_traces(
    textposition = 'top center',
    textfont = dict(size = 14),
)
fig.update_layout(dragmode="pan")

#config chung cho các biểu đồ plotly
config = {
    'displayModeBar': True,  # Hiển thị/thêm thanh công cụ
    'modeBarButtonsToRemove': ['zoom', 'select', 'lasso2d', 'resetScale', 'toImage'],  # Ẩn nút
    'displaylogo': False,  # Ẩn logo Plotly
    'modeBarButtonsToAdd': []  # Đảm bảo không thêm bất kỳ nút nào khác
}

st.plotly_chart(fig,use_container_width=True,config=config)
#########
df5['Eff_A'] = df5['SAH_A']/df5['Total_hours_A']
df5['Eff_P'] = df5['SAH_P']/df5['Total_hours_P']
# st.dataframe(df5)
df6 = pd.melt(df5,id_vars= 'WorkDate',value_vars=['Eff_A','Eff_P'])
df6 = df6.sort_values('WorkDate')
df6 = df6.rename(columns={'value' : 'Hiệu suất','variable' : 'Chỉ số'})
df6 = df6.replace({'Chỉ số': {'Eff_A' : 'Hiệu suất thực tế','Eff_P' : 'Hiệu suất mục tiêu'}})
df6['Eff_formated'] = df6['Hiệu suất'].apply(lambda x: f"{x:,.1%}")
# st.dataframe(df6)
fig = px.line(df6,
                x= df6['WorkDate'],
                y= df6['Hiệu suất'],
                color=df6['Chỉ số'],
                text= df6['Eff_formated'],
                color_discrete_map={
                    'Hiệu suất thực tế' : 'blue',
                    'Hiệu suất mục tiêu' : 'red'
                }
                )
fig.update_xaxes(
    dtick = 'D1',
    tickangle = 45,
    tickformat = "%d/%m"
)
fig.update_layout(
    xaxis_title = 'Ngày',
    yaxis_title = 'Tổng SAH',
    title = "Hiệu suất trung bình theo ngày"
)
fig.update_traces(
    textposition = 'top center',
    textfont = dict(size = 14),
)

fig.update_layout(dragmode="pan")

st.plotly_chart(fig,config= config,use_container_width=True)

st.markdown("---")
# tính toán SAH, Eff theo xưởng
df_unit_eff = df4.groupby(by = ['Unit']).agg({
    'SAH_A' : 'sum',
    'Total_hours_A' : 'sum',
    'SAH_P' : 'sum',
    'Total_hours_P' : 'sum'
},axis = 1).reset_index()
df_unit_eff['Eff_A'] = (df_unit_eff['SAH_A']/df_unit_eff['Total_hours_A'])
df_unit_eff['Eff_A_formated'] = df_unit_eff['Eff_A'].apply(lambda x: f"{x:.1%}")
df_unit_eff['Eff_P'] = (df_unit_eff['SAH_P']/df_unit_eff['Total_hours_P'])
df_unit_eff['Eff_P_formated'] = df_unit_eff['Eff_P'].apply(lambda x: f"{x:.1%}")
df_unit_eff['SAH_A_formated'] = df_unit_eff['SAH_A'].apply(lambda x: f"{x:,.0f}")
df_unit_eff['SAH_P_formated']= df_unit_eff['SAH_P'].apply(lambda x: f"{x:,.0f}")
cols = st.columns(2)
with cols[0]:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x= df_unit_eff['Unit'],
        y = df_unit_eff['SAH_A'],
        text = df_unit_eff['SAH_A_formated'],
        textposition= 'outside',
        marker=dict(color = 'blue'),
        name = "Thực tế"
    ))
    fig.add_trace(go.Bar(
        x= df_unit_eff['Unit'],
        y = df_unit_eff['SAH_P'],
        text = df_unit_eff['SAH_P_formated'],
        textposition= 'outside',
        marker= dict(color = 'red'),
        name="Mục tiêu"
    ))
    
    fig.update_layout(
        title="Tổng SAH theo xưởng",
        xaxis_title="Xưởng", 
        yaxis_title="Tổng SAH" 
    )

    max_SAH = max(df_unit_eff['SAH_A'].max(),df_unit_eff['SAH_P'].max()) * 1.2
    fig.update_yaxes(
        range = [0,max_SAH],
        # showticklabels = False
    )  
    fig.update_layout(dragmode="pan")

    st.plotly_chart(fig,use_container_width=True,config=config)
## hiệu suất theo xưởng
with cols[1]:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x= df_unit_eff['Unit'],
        y = df_unit_eff['Eff_A'],
        text = df_unit_eff['Eff_A_formated'],
        textposition= 'outside',
        marker=dict(color = 'blue'),
        name = "Thực tế"
    ))
    fig.add_trace(go.Bar(
        x= df_unit_eff['Unit'],
        y = df_unit_eff['Eff_P'],
        text = df_unit_eff['Eff_P_formated'],
        textposition= 'outside',
        marker= dict(color = 'red'),
        name="Mục tiêu"
    ))
    
    fig.update_layout(
        title="Hiệu suất theo xưởng",
        xaxis_title="Xưởng", 
        yaxis_title="Hiệu suất trung bình" 
    )
    max_SAH = max(df_unit_eff['Eff_A'].max(),df_unit_eff['Eff_P'].max()) * 1.2
    fig.update_yaxes(
        range = [0,max_SAH],
        # showticklabels = False
    )
    fig.update_layout(dragmode="pan")

    st.plotly_chart(fig,use_container_width=True,key='fig2',config=config)

st.markdown("---")
## Heatmap hiệu suất theo chuyền , ngày
df_line_eff = df4.groupby(by = ['WorkDate','Line']).agg({
    'SAH_A' : 'sum',
    'Total_hours_A' : 'sum'
},axis = 1).reset_index()

df_line_eff = df_line_eff[~df_line_eff["Line"].str.contains("F", na=False)]

if 'Total_hours_A' in df_line_eff.columns:
    df_line_eff['Eff_A'] = df_line_eff.apply(
        lambda row: row['SAH_A'] / row['Total_hours_A'] if row['Total_hours_A'] != 0 else 0,
        axis=1
    )
else:
    df_line_eff['Eff_A'] = 0

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
#Ghép bảng df4 và bảng SAM
df4 = pd.merge(df4,df_SAM,on='Style_P',how='left')
df4 = df4[(df4['WorkDate'] >= df4['TU_NGAY']) & (df4['WorkDate'] <= df4['DEN_NGAY'])]
df4 = df4.groupby(['Line', 'WorkDate', 'Style_P'], as_index=False).agg({
    'SAM': 'sum',  
    **{col: 'first' for col in df4.columns if col not in ['Line', 'WorkDate', 'Style_P', 'SAM']} 
})

df_line_eff['Eff_A'] = df_line_eff['Eff_A'].fillna(0)
df_line_eff_pivot = pd.pivot_table(data=df_line_eff,index='Line',columns='WorkDate',values='Eff_A')
df_ppc['Eff'] = df_ppc['Eff'].fillna(0)

df_ppc_intern = df_ppc[((df_ppc['Line'] == '25S01') & (df_ppc['WorkDate'] >= date(2025,6,1)) & (df_ppc['WorkDate'] < date(2025,8,1)))]
df_ppc = df_ppc[~((df_ppc['Line'] == '25S01') & (df_ppc['WorkDate'] >= date(2025,6,1)) & (df_ppc['WorkDate'] < date(2025,8,1)))]
df_line_eff_pivot_ppc = pd.pivot_table(data=df_ppc,index='Line',columns='WorkDate',values='Eff')

df4['Style_P_short'] = df4['Style_P'].str[-4:]
df_line_style = pd.pivot(df4, index=['Line'], columns=['WorkDate'],values='Style_P')
df_line_short_style = pd.pivot(df4, index=['Line'], columns=['WorkDate'],values='Style_P_short')
df_line_SAH = pd.pivot(df4, index=['Line'], columns=['WorkDate'],values='SAH_A')
df_line_SAH_ppc = pd.pivot(df_ppc, index=['Line'], columns=['WorkDate'],values='SAH_P')

image_folder = "images/png/"
df4['Link_anh'] = image_folder + df4['Style_P'] + '.png'
df_line_link_anh = pd.pivot(df4, index=['Line'], columns=['WorkDate'],values='Link_anh')

#pivot lấy bảng SAM
df_line_SAM = pd.pivot(df4, index=['Line'], columns=['WorkDate'],values='SAM')
#Ghép các bảng pivot vào thành bảng chiều dùng làm customdata

df_line_eff_pivot = df_line_eff_pivot.fillna(0)
customdata = np.dstack([df_line_style.values, df_line_SAH.values,df_line_link_anh.values,df_line_SAM, df_line_eff_pivot, df_line_eff_pivot_ppc, df_line_SAH_ppc])

df_actual = df_line_eff_pivot.astype(float)
df_plan = df_line_eff_pivot_ppc.astype(float)
df_actual.columns = df_actual.columns.astype(str)
df_plan.columns = df_plan.columns.astype(str)
df_plan = df_plan.loc[df_actual.index, df_actual.columns] 
df_diff = df_actual.subtract(df_plan, fill_value=0)

text_values = df_actual.map(lambda x: f"{x:.0%}")
vmin = df_diff.min().min()
vmax = df_diff.max().max()

padding = max(abs(vmin), abs(vmax)) * 1.1

#Vẽ biểu đồ nhiệt theo Eff
fig = px.imshow(
    df_diff.values,
    x=df_diff.columns,                     
    y=df_diff.index,                        
    color_continuous_scale=[
        [0.0,   "#d73027"],   # đỏ cho cực âm (vd -40)
        [0.1,   "#b2182b"],   # đỏ đậm cho -20
        [0.2,   "#f46d43"],   # cam đậm cho -10
        [0.3,   "#f46d43"],   # cam đậm vừa cho gần 0
        [0.4,   "#fdae61"],   # cam sáng cho âm nhẹ
        [0.4999, "#fee08b"],  # vàng nhạt cho gần 0
        [0.5,   "#ffffbf"],   # vàng trung tính tại 0
        [0.6,   "#a6d96a"],   # xanh lá nhạt
        [0.8,   "#1a9850"],   # xanh đậm
        [1.0,   "#006837"] 
    ],
    zmin=-padding,  
    zmax=padding,    
    text_auto=False)
fig.update_xaxes(
    dtick = 'D1',
    tickformat = '%d/%m',
    tickfont = dict(size = 12)
)
fig.update_yaxes(
    tickfont = dict(size = 14),
    dtick = 'D1'
)
num_row = df_line_eff_pivot.shape[0]
row_hight = 35
min_height = 300
fig.update_layout(
    title = "Biểu đồ nhiệt - Hiệu suất chuyền theo ngày",
    xaxis_title = "Ngày",
    yaxis_title = "Chuyền",
    height = max(num_row * row_hight, min_height)
)
fig.update_traces(
    text=text_values.values,               # text thủ công
    texttemplate='%{text}',                # không định dạng lại
    textfont=dict(size=14),
    customdata=customdata,
    hovertemplate=(
        "Style: %{customdata[0]}<br>"
        "SAM: %{customdata[3]:.4f}<br>"
        "SAH: %{customdata[1]:.0f}<br>"
        "Efficiency PPC: %{customdata[5]:.1%}<br>"
        "Chênh lệch: %{z:.1%}<br>"
        # "<img src='%{customdata[2]}' style='width:100px;height:100px;'>"
    )
)

fig.update_layout(dragmode="pan")

st.plotly_chart(fig,use_container_width=True,key='heatmap0',config=config)
#Vẽ biểu đồ nhiệt theo short style
fig = px.imshow(
    df_diff.values,
    x=df_diff.columns,                     
    y=df_diff.index,                        
    color_continuous_scale=[
        [0.0,   "#d73027"],   # đỏ cho cực âm (vd -40)
        [0.1,   "#b2182b"],   # đỏ đậm cho -20
        [0.2,   "#f46d43"],   # cam đậm cho -10
        [0.3,   "#f46d43"],   # cam đậm vừa cho gần 0
        [0.4,   "#fdae61"],   # cam sáng cho âm nhẹ
        [0.4999, "#fee08b"],  # vàng nhạt cho gần 0
        [0.5,   "#ffffbf"],   # vàng trung tính tại 0
        [0.6,   "#a6d96a"],   # xanh lá nhạt
        [0.8,   "#1a9850"],   # xanh đậm
        [1.0,   "#006837"] 
    ],
    zmin=-padding,  
    zmax=padding,    
    text_auto=False)
fig.update_xaxes(
    dtick = 'D1',
    tickformat = '%d/%m',
    tickfont = dict(size = 12)
)
fig.update_yaxes(
    tickfont = dict(size = 14),
    dtick = 'D1'
)
num_row = df_line_eff_pivot.shape[0]
row_hight = 35
fig.update_layout(
    title = "Style_P",
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
        "Hiệu suất: %{customdata[4]:.1%}<br>"
        "SAH: %{customdata[1]:.0f}<br>"
        "Style: %{customdata[0]}<br>"
        "SAM: %{customdata[3]:.4f}<br>"
        "Chênh lệch Eff: %{z:.1%}<br>"
    ),
    text=df_line_short_style.values, 
    texttemplate="%{text}"
)
fig.update_layout(dragmode="pan")
st.plotly_chart(fig,use_container_width=True,key='heatmap1',config=config)
#Vẽ biểu đồ nhiệt theo SAH

df_actual_sah = df_line_SAH.astype(float)
df_plan_sah = df_line_SAH_ppc.astype(float)
df_actual_sah.columns = df_actual_sah.columns.astype(str)
df_plan_sah.columns = df_plan_sah.columns.astype(str)
df_plan_sah = df_plan_sah.loc[df_actual_sah.index, df_actual_sah.columns] 
df_diff_sah = df_actual_sah.subtract(df_plan_sah, fill_value=0)

vmin_sah = df_diff_sah.min().min()
vmax_sah = df_diff_sah.max().max()

padding_sah = max(abs(vmin_sah), abs(vmax_sah)) * 1.1

fig = px.imshow(
    df_diff_sah.values,
    x=df_diff_sah.columns,                     
    y=df_diff_sah.index,                        
    color_continuous_scale=[
        [0.0,   "#d73027"],   # đỏ cho cực âm (vd -40)
        [0.1,   "#b2182b"],   # đỏ đậm cho -20
        [0.2,   "#f46d43"],   # cam đậm cho -10
        [0.3,   "#f46d43"],   # cam đậm vừa cho gần 0
        [0.4,   "#fdae61"],   # cam sáng cho âm nhẹ
        [0.4999, "#fee08b"],  # vàng nhạt cho gần 0
        [0.5,   "#ffffbf"],   # vàng trung tính tại 0
        [0.6,   "#a6d96a"],   # xanh lá nhạt
        [0.8,   "#1a9850"],   # xanh đậm
        [1.0,   "#006837"] 
    ],
    zmin=-padding_sah,  
    zmax=padding_sah,    
    text_auto=False)
fig.update_xaxes(
    dtick = 'D1',
    tickformat = '%d/%m',
    tickfont = dict(size = 12)
)
fig.update_yaxes(
    tickfont = dict(size = 14),
    dtick = 'D1'
)
num_row = df_line_eff_pivot.shape[0]
row_hight = 35
fig.update_layout(
    title = "SAH",
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
        "Hiệu suất: %{customdata[4]:.1%}<br>"
        "Style: %{customdata[0]}<br>"
        "SAM: %{customdata[3]:.4f}<br>"
        "SAH PPC: %{customdata[6]:.1f}<br>"
        "Chênh lệch: %{z:.1f}<br>"
    ),
    text=df_line_SAH.values, 
    texttemplate="%{text:.0f}"
)
fig.update_layout(dragmode="pan")
st.plotly_chart(fig,use_container_width=True,key='heatmap2',config=config)


#Vẽ biểu đồ nhiệt theo SAH thực tập
df_line_SAH_intern = pd.pivot(df_intern, index=['Line'], columns=['WorkDate'],values='SAH_A')
df_line_SAH_intern = df_line_SAH_intern.fillna(0)
df_line_SAH_ppc_intern = pd.pivot(df_ppc_intern, index=['Line'], columns=['WorkDate'],values='SAH_P')
df_line_SAH_ppc_intern = df_line_SAH_ppc_intern.fillna(0)

df_actual_sah_intern = df_line_SAH_intern.astype(float)
df_plan_sah_intern = df_line_SAH_ppc_intern.astype(float)
df_actual_sah_intern.columns = df_actual_sah_intern.columns.astype(str)
df_plan_sah_intern.columns = df_plan_sah_intern.columns.astype(str)
df_plan_sah_intern = df_plan_sah_intern.loc[df_actual_sah_intern.index, df_actual_sah_intern.columns] 
df_diff_sah_intern = df_actual_sah_intern.subtract(df_plan_sah_intern, fill_value=0)

vmin_sah = df_diff_sah_intern.min().min()
vmax_sah = df_diff_sah_intern.max().max()

padding_sah = max(abs(vmin_sah), abs(vmax_sah)) * 1.1

customdata2 = np.dstack([df_line_SAH_intern.values, df_line_SAH_ppc_intern])

fig = px.imshow(
    df_diff_sah_intern.values,
    x=df_diff_sah_intern.columns,                     
    y=df_diff_sah_intern.index,                        
    color_continuous_scale=[
        [0.0,   "#d73027"],   # đỏ cho cực âm (vd -40)
        [0.1,   "#b2182b"],   # đỏ đậm cho -20
        [0.2,   "#f46d43"],   # cam đậm cho -10
        [0.3,   "#f46d43"],   # cam đậm vừa cho gần 0
        [0.4,   "#fdae61"],   # cam sáng cho âm nhẹ
        [0.4999, "#fee08b"],  # vàng nhạt cho gần 0
        [0.5,   "#ffffbf"],   # vàng trung tính tại 0
        [0.6,   "#a6d96a"],   # xanh lá nhạt
        [0.8,   "#1a9850"],   # xanh đậm
        [1.0,   "#006837"] 
    ],
    zmin=-padding_sah,  
    zmax=padding_sah,    
    text_auto=False)
fig.update_xaxes(
    dtick = 'D1',
    tickformat = '%d/%m',
    tickfont = dict(size = 12)
)
fig.update_yaxes(
    tickfont = dict(size = 14),
    dtick = 'D1'
)
num_row = df_line_SAH_intern.shape[0]
row_hight = 35
fig.update_layout(
    title = "SAH thực tập",
    xaxis_title = "Ngày",
    yaxis_title = "Chuyền",
    height = max(num_row * row_hight, min_height)
)
fig.update_traces(
    customdata = customdata2,
    textfont=dict(size=14),
    zmin=0,
    zmax=1,
    hovertemplate=(
        "SAH PPC: %{customdata[1]:.1f}<br>"
        "Chênh lệch: %{z:.1f}<br>"
    ),
    text=df_line_SAH_intern.values, 
    texttemplate="%{text:.0f}"
)
fig.update_layout(dragmode="pan")
st.plotly_chart(fig,use_container_width=True,key='heatmap3',config=config)


# #Vẽ biểu đồ nhiệt theo Eff - Style - SAH
# df4['Eff_formated'] = (df4['SAH_A']/df4['Total_hours_A']).apply(lambda x: f"{x:.0%}")
# df4['SAH_A_formated'] = df4['SAH_A'].apply(lambda x: f"{x:.0f}")
# df_line_eff_formated = pd.pivot(df4, index=['Line'], columns=['WorkDate'],values='Eff_formated')
# df_line_SAH_formated= pd.pivot(df4, index=['Line'], columns=['WorkDate'],values='SAH_A_formated')

# text_data = df_line_short_style + "<br>" + df_line_eff_formated + "<br>" + df_line_SAH_formated
# fig = px.imshow(
#     df_line_eff_pivot,
#     color_continuous_scale= "RdYlGn",
#     text_auto= True)
# fig.update_xaxes(
#     dtick = 'D1',
#     tickformat = '%d/%m',
#     tickfont = dict(size = 12)
# )
# fig.update_yaxes(
#     tickfont = dict(size = 14),
#     dtick = 'D1'
# )
# num_row = df_line_eff_pivot.shape[0]
# row_hight = 70
# fig.update_layout(
#     title = "SAH",
#     xaxis_title = "Ngày",
#     yaxis_title = "Chuyền",
#     height = num_row * row_hight
# )
# fig.update_traces(
#     customdata = customdata,
#     textfont=dict(size=14),
#     zmin=0,
#     zmax=1,
#     hovertemplate=(
#         "Hiệu suất: %{z:.1%}<br>"
#         "Style: %{customdata[0]}"
#     ),
#     text=text_data.values, 
#     texttemplate="%{text}"
# )
# st.plotly_chart(fig,use_container_width=True,key='heatmap3')

## Heatmap style theo chuyền , ngày

fig = px.density_heatmap(
    df_line_style,
    color_continuous_scale= "Blues",
    text_auto=True)
fig.update_layout(
    title = 'Phân bổ đơn hàng theo chuyền',
    xaxis_title = 'Chuyền',
    yaxis_title = 'Style',
    coloraxis_colorbar_title='Số ngày'
)
fig.update_xaxes(
    tickfont = dict(size = 14)
)
fig.update_yaxes(
    tickfont = dict(size = 14)
)
fig.update_traces(
    textfont = dict(size = 14)
)
fig.update_layout(dragmode="pan")
st.plotly_chart(fig,use_container_width=True,config=config)
# st.dataframe(df_line_style)
with st.expander("Dữ liệu chi tiết"):
    st.dataframe(df4,hide_index=True)

# while True:
#     time.sleep(30)
#     st.rerun()