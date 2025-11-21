import streamlit as st 
import pandas as pd
from load_data import get_data
import plotly.graph_objects as go
from datetime import datetime
import re

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

fty = ['NT1','NT2']
factory = st.selectbox("Chọn nhà máy",options= fty, index= fty.index(st.session_state.factory))

current_year = datetime.now().year

years = list(range(2024, current_year + 1))

selected_year = st.selectbox("Chọn năm", years, index=len(years) - 1)

def get_query(filter_type: str) -> str:
    base_query = """
        WITH Thang_Nam AS (
            SELECT 
                CAST(CAST(y AS VARCHAR(4)) + '-' + RIGHT('0' + CAST(m AS VARCHAR(2)), 2) + '-01' AS DATE) AS StartDate,
                DATEADD(DAY, -1, DATEADD(MONTH, 1, 
                    CAST(CAST(y AS VARCHAR(4)) + '-' + RIGHT('0' + CAST(m AS VARCHAR(2)), 2) + '-01' AS DATE)
                )) AS EndDate,
                y AS Nam,
                m AS Thang
            FROM (
                SELECT y = {year}
            ) AS Years
            CROSS JOIN (
                SELECT m = 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL 
                SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL 
                SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL 
                SELECT 10 UNION ALL SELECT 11 UNION ALL SELECT 12
            ) AS Months
        )

        SELECT 
            tn.thang,
            hc.section_code,
            COUNT(DISTINCT ls.MST) AS so_luong
        FROM Thang_Nam tn
        JOIN Lich_su_cong_viec ls
        ON ls.Trang_thai_lam_viec = N'Đang làm việc'
            AND ls.Nha_may = '{factory}'
            AND (
              (ls.Tu_ngay <= tn.EndDate AND ls.Den_ngay >= tn.StartDate)
            )
        LEFT JOIN HC_Name hc
          ON ls.Chuyen = hc.Line 
          AND ls.Nha_may = hc.Factory 
          AND ls.Grade_code = hc.Grade_code 
        WHERE 
        {additional_conditions}
        GROUP BY tn.Nam, tn.Thang, hc.Section_code
        ORDER BY tn.Nam, tn.Thang, hc.Section_code;
    """

    # Từng loại điều kiện
    conditions = {
        "Kho": "hc.Department LIKE '%WHS%' AND hc.Line NOT LIKE '%FAB%'",
        "Xả vải": "hc.Department LIKE '%WHS%' AND hc.Line LIKE '%FAB%'",
        "Trải vải": """hc.Section_description LIKE '%CUT%' 
                       AND hc.Detail_job_title_VN LIKE N'%trải vải%' 
                       AND hc.Line NOT LIKE '%99' 
                       AND hc.Line NOT LIKE '%00'""",
        "Cắt": """hc.Section_description LIKE '%CUT%' 
                  AND hc.Detail_job_title_VN NOT LIKE N'%trải vải%' 
                  AND hc.Detail_job_title_VN NOT LIKE N'%công nhân phụ cắt%' 
                  AND hc.Detail_job_title_VN NOT LIKE N'%Nhân viên%' 
                  AND hc.Line NOT LIKE '%99' 
                  AND hc.Line NOT LIKE '%00'""",
        "CPI": """hc.Section_description LIKE '%CUT%' 
                  AND hc.Detail_job_title_VN LIKE N'%công nhân phụ cắt%' 
                  AND hc.Line NOT LIKE '%99' 
                  AND hc.Line NOT LIKE '%00'""",
        "May": """hc.Section_description LIKE '%SEW%' 
                  AND hc.Line NOT LIKE '%99' 
                  AND hc.Line NOT LIKE '%00' 
                  AND hc.Line NOT LIKE '20%'""",
        "QC1": """hc.Section_description LIKE '%QC1%' 
                  AND hc.Line NOT LIKE '%99' 
                  AND hc.Line NOT LIKE '%00'""",
        "Là": """hc.Section_description LIKE '%FNS%' 
                 AND hc.Detail_job_title_VN LIKE N'%là%' 
                 AND hc.Line NOT LIKE '%99' 
                 AND hc.Line NOT LIKE '%00'""",
        "QC2": """hc.Section_description LIKE '%QC2%' 
                  AND hc.Line NOT LIKE '%99' 
                  AND hc.Line NOT LIKE '%00'""",
        "Đóng gói": """hc.Section_description LIKE '%FNS%' 
                       AND hc.Detail_job_title_VN LIKE N'%đóng gói%' 
                       AND hc.Line NOT LIKE '%99' 
                       AND hc.Line NOT LIKE '%00'""",
        "Đóng thùng": """hc.Section_description LIKE '%FNS%' 
                         AND hc.Detail_job_title_VN LIKE N'%đóng thùng%' 
                         AND hc.Line NOT LIKE '%99' 
                         AND hc.Line NOT LIKE '%00'""",
    }

    condition = conditions.get(filter_type, "")
    query = base_query.format(year=selected_year, factory=factory, additional_conditions=condition)
    return query
  
columns = ["Kho", "Xả vải", "Trải vải", "Cắt", "CPI", "May", "QC1", "Là", "QC2", "Đóng gói", "Đóng thùng"]

result_frames = []

for filter_type in columns:
    query = get_query(filter_type)
    df = get_data('HR',query)
    df['loai'] = filter_type 
    result_frames.append(df)

final_df = pd.concat(result_frames, ignore_index=True)

final_df["section_code"] = final_df["section_code"].apply(
    lambda x: x if re.fullmatch(r"\dP\d{2}", str(x)) else "Khac"
)

current_month = datetime.now().month

if selected_year == 2024:
    final_df = final_df[final_df["thang"] >= 5]
elif selected_year == current_year:
    final_df = final_df[final_df["thang"] <= current_month]

# Lấy danh sách section_code duy nhất và sắp xếp
section_list = sorted(final_df['section_code'].unique())

# Thêm "Tất cả" vào đầu danh sách
section_options = ["Tất cả"] + section_list

# Tạo selectbox với mặc định là "Tất cả"
section_selected = st.selectbox("Chọn Xưởng", section_options, index=0)

# Lọc theo section_code đã chọn
if section_selected == "Tất cả":
    filtered_df = final_df.groupby(["thang", "loai"])["so_luong"].sum().reset_index()
else:
    filtered_df = final_df[final_df["section_code"] == section_selected] \
                     .groupby(["thang", "section_code", "loai"])["so_luong"].sum().reset_index()

# Lấy danh sách 'thang' theo thứ tự xuất hiện
unique_thang = filtered_df["thang"].unique().tolist()

# Tính tổng theo 'thang' để chia phần trăm
total_by_thang = filtered_df.groupby("thang")["so_luong"].sum().to_dict()

# Khởi tạo biểu đồ
fig = go.Figure()

for loai in columns:
    group = filtered_df[filtered_df["loai"] == loai]
    group_sum = group.groupby("thang")["so_luong"].sum()

    # Tính % và sắp xếp theo thứ tự unique_thang
    data_percent = [
        round((group_sum.get(thang, 0) / total_by_thang.get(thang, 1)) * 100, 2)
        for thang in unique_thang
    ]

    # Bỏ nếu tất cả đều bằng 0%
    if all(val == 0 for val in data_percent):
        continue

    fig.add_trace(go.Bar(
        name=loai,
        x=unique_thang,
        y=data_percent,
        text=[f"{val:.1f}%" if val > 0 else "" for val in data_percent],
        textposition='inside',
        hoverinfo='x+y+name'
    ))

# Cập nhật layout
fig.update_layout(
    barmode='stack',
    height=700,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.2,
        xanchor="center",
        x=0.5
    ),
    xaxis=dict(
        title='Tháng',
        tickmode='array',
        tickvals=unique_thang,
    ),
    yaxis=dict(
        title='Tỷ lệ (%)',
        range=[0, 100]  # Vì là phần trăm
    )
)

st.plotly_chart(fig, use_container_width=True)