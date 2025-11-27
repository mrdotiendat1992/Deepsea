git pull origin main

call deepsea_env\Scripts\activate
streamlit run reports.py --server.enableCORS false --server.enableXsrfProtection false --server.port 100
