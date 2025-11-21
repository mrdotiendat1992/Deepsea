import streamlit as st
import pandas as pd

st.markdown(
    """
    <style>
    .centered-title {
        text-align: center;
        margin-top: 20px;
        color: rgb(255,255,255);
        font-size: 48px;
    }
    div.block-container {padding-top: 2rem;}
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown('<h1 class="centered-title">CHATBOT NỘI BỘ</h1>', unsafe_allow_html=True)












####################################################

# from langchain.agents import AgentType
# from langchain_experimental.agents import create_pandas_dataframe_agent
# from langchain_ollama import ChatOllama


# # Hàm đọc dữ liệu từ file
# def read_data(file):
#     if file.name.endswith(".csv"):
#         return pd.read_csv(file)
#     else:
#         return pd.read_excel(file)

# # Trạng thái session
# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []
# if "df" not in st.session_state:
#     st.session_state.df = None

# # Tải file dữ liệu
# uploaded_file = st.file_uploader("Chọn file để tải lên", type=['csv', 'xlsx', 'xls'])

# if uploaded_file:
#     st.session_state.df = read_data(uploaded_file)
#     with st.expander("Dữ liệu chi tiết"):
#         st.dataframe(st.session_state.df)

# # Kiểm tra dữ liệu trước khi chat
# if st.session_state.df is None:
#     st.warning("Vui lòng tải lên một file dữ liệu để bắt đầu.")
# else:
#     # Hiển thị lịch sử chat
#     for message in st.session_state.chat_history:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])

#     # Input từ người dùng
#     user_prompt = st.chat_input("Gõ câu hỏi của bạn ...")

#     if user_prompt:
#         # Thêm tin nhắn của người dùng vào lịch sử
#         st.chat_message("user").markdown(user_prompt)
#         st.session_state.chat_history.append({"role": "user", "content": user_prompt})

#         # Tạo LLM với ChatOllama
#         llm = ChatOllama(model="gemma:2b", temperature=0)

#         # Tạo agent xử lý DataFrame
#         pandas_df_agent = create_pandas_dataframe_agent(
#             llm,
#             st.session_state.df,
#             verbose=True,
#             agent_type=AgentType.OPENAI_FUNCTIONS,
#             allow_dangerous_code=True
#         )
#         messages = [
#         {"role":"system", "content": "You are a helpful assistant"},
#         *st.session_state.chat_history
#         ]
#         # Gửi câu hỏi đến agent
#         response = pandas_df_agent.invoke(messages)
#         assistant_response = response["output"]

#         # Lưu phản hồi của chatbot
#         st.session_state.chat_history.append({"role": "assistant", "content": assistant_response})

#         # Hiển thị phản hồi
#         with st.chat_message("assistant"):
#             st.markdown(assistant_response)

# ########################
# # import streamlit as st
# # import pandas as pd
# # # from langchain.agents import AgentType
# # # from langchain_experimental.agents import create_pandas_dataframe_agent
# # # from langchain_ollama import ChatOllama

# # st.markdown(
# #     """
# #     <style>
# #     .centered-title {
# #         text-align: center;
# #         margin-top: 0px;
# #         color: rgb(255,255,255);
# #         font-size: 48px;
# #     }
# #     div.block-container {padding-top: 2rem;}
# #     </style>
# #     """,
# #     unsafe_allow_html=True
# # )
# # st.markdown('<h1 class="centered-title">CHATBOT NỘI BỘ</h1>', unsafe_allow_html=True)

# # fty = ['NT1','NT2']
# # nha_may = st.sidebar.selectbox("Chọn nhà máy",options= fty, index= fty.index(st.session_state.factory))
