#dung streamlit de thiet ke giao dien 
import streamlit as st
def cai_dat_trang():#set up web
    st.set_page_config(
        page_title="EduData Insight",
        page_icon="📊",
        layout="wide"
    )
#phan nhan file va hien thi sidebar
def hien_thi_sidebar():
    #trang tri sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3413/3413535.png", width=100)
        st.title("phần mềm đánh giá kết quả học tập")
        st.write("---")
#tao nut up load file
        file_upload = st.file_uploader("Chọn file Excel điểm thi:", type=['xlsx'])
        
        st.info("Lưu ý: File cần có cột Toán, Văn, Anh")
    return file_upload
def hien_thi_header():
    st.title("📊 EDU PROJECT")
    st.markdown("Hệ thống phân tích điểm số tự động")
    st.write("---")