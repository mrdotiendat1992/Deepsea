# syntax=docker/dockerfile:1
# ============================================================================
#  DeepSea - Streamlit + SQL Server (Python 3.12)
#  Dat file nay tai:  D:\PHANMEM_NT\Deepsea\Dockerfile
#
#  KHAC 4 PROJECT KIA O HAI CHO - doc qua cho do ngac nhien:
#
#   1. KHONG can nt_compat.py.
#      HRM/Incentive dung `DRIVER={SQL Server}` (driver doi 2000, tra DATE/TIME
#      ve dang chuoi) nen phai co lop tuong thich. DeepSea goi THANG
#      "ODBC Driver 17 for SQL Server" trong load_data.py va core/config.py,
#      tuc la da viet theo driver moi ngay tu dau -> khong phai va gi.
#      Cung vi vay Dockerfile nay KHONG tao bi danh [SQL Server] trong odbcinst.
#
#   2. VAN can fix-openssl-legacy.py.
#      Van la con SQL Server do, van chung chi cu ky bang SHA1 ma OpenSSL 3
#      tu choi. Khong co buoc nay se bao:
#          [08001] SSL Provider: [error:0A00014D:SSL routines::legacy sigalg
#          disallowed or unsupported]
# ============================================================================

FROM python:3.12-slim-bookworm

# ---------------------------------------------------------------------------
#  1. Goi he thong + Microsoft ODBC Driver 17
# ---------------------------------------------------------------------------
#  unixodbc-dev: pyodbc can header luc cai (co wheel san thi khong dung den,
#                nhung de day cho chac, khong thi build that bai kho hieu)
#  curl/gnupg  : de lay khoa va kho cua Microsoft
# ---------------------------------------------------------------------------
RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends \
        curl gnupg ca-certificates apt-transport-https \
        unixodbc unixodbc-dev \
        tzdata locales; \
    mkdir -p /etc/apt/keyrings; \
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
        | gpg --dearmor -o /etc/apt/keyrings/microsoft.gpg; \
    echo "deb [signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
        > /etc/apt/sources.list.d/mssql-release.list; \
    apt-get update; \
    ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql17; \
    apt-get clean; rm -rf /var/lib/apt/lists/*

# ---------------------------------------------------------------------------
#  2. Cho phep giao thuc TLS cu de noi duoc toi SQL Server cua cong ty
# ---------------------------------------------------------------------------
#  Chay bang Python chu khong dung sed: cau truc openssl.cnf cua Debian khong
#  co san muc [system_default_sect], sed se "chay thanh cong" ma khong sua gi
#  va loi chi lo ra luc ket noi DB. Script nay tu tao muc con thieu.
#
#  DANH DOI: ha muc an toan TLS cua CA container. Chap nhan duoc vi container
#  chi noi chuyen voi SQL Server trong mang LAN noi bo.
# ---------------------------------------------------------------------------
COPY fix-openssl-legacy.py /tmp/fix-openssl-legacy.py
RUN set -eux; \
    python3 /tmp/fix-openssl-legacy.py; \
    rm -f /tmp/fix-openssl-legacy.py

# ---------------------------------------------------------------------------
#  3. Cai thu vien Python
# ---------------------------------------------------------------------------
#  Dung requirements.docker.txt (UTF-8) chu KHONG dung requirements.txt cua
#  repo - file do la UTF-16 do `pip freeze` chay trong PowerShell, pip tren
#  Linux doc khong ra. Xem giai thich trong requirements.docker.txt.
#
#  Cache mount: cac lan build sau khong phai tai lai ~500MB wheel
#  (numpy, pandas, pyarrow, matplotlib, geopandas... deu nang).
# ---------------------------------------------------------------------------
WORKDIR /app

ARG PIP_INDEX_URL=https://pypi.org/simple
COPY requirements.docker.txt .
RUN --mount=type=cache,target=/root/.cache/pip,id=nt-pip,sharing=locked \
    pip install --retries 10 --timeout 60 \
        --index-url "$PIP_INDEX_URL" \
        -r requirements.docker.txt

# ---------------------------------------------------------------------------
#  4. Chep ma nguon
# ---------------------------------------------------------------------------
#  De SAU buoc pip: sua code thi chi lop nay build lai (vai giay),
#  khong phai cai lai toan bo thu vien (vai phut).
# ---------------------------------------------------------------------------
COPY . .

ENV TZ=Asia/Ho_Chi_Minh \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Cong 100 - giong het `run.bat` cua repo, de nguoi dung khong phai doi dia chi
EXPOSE 100

# ---------------------------------------------------------------------------
#  5. Healthcheck
# ---------------------------------------------------------------------------
#  Streamlit co san endpoint /_stcore/health tra ve chu "ok".
#  Dung endpoint do thay vi goi "/" vi "/" tra ve trang dang nhap nang,
#  kiem tra 30 giay mot lan se ton tai nguyen vo ich.
# ---------------------------------------------------------------------------
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=60s \
    CMD curl -fsS "http://127.0.0.1:${DEEPSEA_PORT:-100}/_stcore/health" || exit 1

# ---------------------------------------------------------------------------
#  6. Lenh chay
# ---------------------------------------------------------------------------
#  Giu nguyen 2 tham so cua run.bat:
#      --server.enableCORS false --server.enableXsrfProtection false
#  Them 4 tham so chi can khi chay trong container:
#      --server.address=0.0.0.0    nghe moi dia chi, khong chi localhost
#                                  (thieu dong nay la ngoai container goi vao
#                                   se bi tu choi, dung kieu kho doan)
#      --server.headless=true      khong co man hinh de mo trinh duyet,
#                                  va bo qua man hoi email cua Streamlit
#      --server.fileWatcherType=none  production khong sua code luc dang chay,
#                                  tat theo doi file cho do ton CPU
#      --browser.gatherUsageStats=false  khong gui thong ke ra ngoai
# ---------------------------------------------------------------------------
CMD ["sh", "-c", "exec streamlit run reports.py \
     --server.port=${DEEPSEA_PORT:-100} \
     --server.address=0.0.0.0 \
     --server.headless=true \
     --server.fileWatcherType=none \
     --server.enableCORS=false \
     --server.enableXsrfProtection=false \
     --browser.gatherUsageStats=false"]
