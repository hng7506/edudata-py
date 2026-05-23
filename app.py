import streamlit as st
import database # Gọi người thợ quản lý két sắt đến
import giao_dien as ui       # Ông phụ trách giao diện
import xuly_du_lieu as data  # Ông phụ trách tính toán
import ve_bieu_do as chart   # Ông họa sĩ vẽ hình
# import json # thu vien doc/ghi file cau hinh
# import os # thu vien kiem tra file ton tai ko
import os
# from dotenv import load_dotenv
import google.generativeai as genai
API_KEY =st.secrets["Gemini_API_KEY"]
genai.configure(api_key=API_KEY)
model_ai = genai.GenerativeModel('gemini-2.5-flash')


ui.cai_dat_trang()  # Gọi hàm cài đặt trang (Tab browser, icon)

#-----2. khoi tao trang thai moi ( dang nhap )-----
# kiem tra xem da co tai khoan chua
if 'da_dang_nhap' not in st.session_state:
    st.session_state['da_dang_nhap']=False

#----3.ham dang nhap-------
def man_hinh_dang_nhap():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("## 🔐 Cổng Thông Tin EduData")
        
        # Chia 2 Tab: Đăng nhập và Đăng ký
        tab1, tab2 = st.tabs(["🔑 Đăng nhập", "📝 Đăng ký tài khoản"])
        
        # TAB 1: ĐĂNG NHẬP
        with tab1:
            user_input = st.text_input("Tên đăng nhập:")
            pass_input = st.text_input("Mật khẩu:", type="password")
            
            if st.button("Đăng nhập"):
                kiem_tra = database.kiem_tra_dang_nhap(user_input, pass_input)
                if kiem_tra == True:
                    st.session_state['da_dang_nhap'] = True
                    st.session_state['user_dang_nhap'] = user_input 
                    # [MỚI] Lôi cái quân hàm từ Database ra nhét vào túi
                    st.session_state['vai_tro'] = database.lay_vai_tro(user_input)
                    st.success("Đăng nhập thành công!")
                    st.rerun()
                else:
                    st.error("Sai tài khoản hoặc mật khẩu!")
                    
        # TAB 2: ĐĂNG KÝ MỚI
        with tab2:
            st.info("👋 Chào mừng giáo viên mới! Vui lòng tạo tài khoản.")
            new_user = st.text_input("Tạo Tên đăng nhập:")
            new_pass = st.text_input("Tạo Mật khẩu:", type="password")
            
            if st.button("Đăng ký"):
                if new_user == "" or new_pass == "":
                    st.warning("⚠️ Vui lòng không để trống thông tin!")
                else:
                    thanh_cong = database.tao_tai_khoan(new_user, new_pass)
                    if thanh_cong:
                        st.success("🎉 Đăng ký thành công! Hãy chuyển sang Tab Đăng nhập để vào hệ thống.")
                    else:
                        st.error("❌ Tên đăng nhập này đã tồn tại. Vui lòng chọn tên khác!")

# hàm chức năng chính
def main_app():
    # --- [SỬA] PHẦN SIDEBAR: THÊM CHỨC NĂNG ĐỔI MẬT KHẨU ---
    with st.sidebar:
        # Nút Đăng xuất (Mình sửa chữ 'Đăng nhập' thành 'Đăng xuất' cho đúng nghĩa)
        if st.button("Đăng xuất 🚪"):
            st.session_state['da_dang_nhap']=False
            st.rerun()
        
        st.write("---")
        # =======================================================
        # BẢNG ĐIỀU KHIỂN PHÂN QUYỀN (Chỉ Admin mới nhìn thấy)
        # =======================================================
        if st.session_state.get('vai_tro') == 'Quan_tri':
            st.write("---")
            with st.expander("🛠️ Quản lý Phân Quyền (Admin)"):
                st.markdown("**Danh sách nhân sự:**")
                df_tk = database.lay_danh_sach_tai_khoan_va_quyen()
                st.dataframe(df_tk, use_container_width=True)
                
                st.markdown("**Cấp quyền mới:**")
                # Khung nhập tên và chọn quyền
                user_can_doi = st.text_input("Nhập tên tài khoản:")
                quyen_moi = st.selectbox("Chọn vai trò:", ["Giao_vien", "Quan_tri"])
                
                if st.button("Cập nhật quyền"):
                    if database.cap_nhat_quyen(user_can_doi, quyen_moi):
                        st.success(f"✅ Đã phong chức {quyen_moi} cho {user_can_doi}")
                        st.rerun() # Tải lại trang để bảng danh sách cập nhật mới
        # =======================================================
        # [MỚI] Chức năng đổi mật khẩu chuẩn thực tế
        with st.expander("⚙️ Đổi mật khẩu"):
            with st.form("form_doi_mk"):
                mk_cu = st.text_input("Nhập Mật khẩu CŨ", type="password")
                mk_moi = st.text_input("Nhập Mật khẩu MỚI", type="password")
                mk_nhap_lai = st.text_input("Xác nhận LẠI Mật khẩu MỚI", type="password")
                btn_luu = st.form_submit_button("Lưu thay đổi")
                
                if btn_luu:
                    user_hien_tai = st.session_state['user_dang_nhap']
                    database.doi_mat_khau(user_hien_tai, mk_moi) 
                    st.success("✅ Đã đổi! Vui lòng đăng nhập lại.")
                    st.session_state['da_dang_nhap'] = False 
                    st.rerun()
    # -------------------------------------------------------
   
    
    # --- 3. HIỂN THỊ KHUNG SƯỜN ---
    ui.hien_thi_header()            # Hiện tiêu đề to đùng
    uploaded_file = ui.hien_thi_sidebar() # Hiện sidebar và nhận file về

    # --- 4. LUỒNG XỬ LÝ CHÍNH (TỰ ĐỘNG LẤY TỪ DATABASE) ---
    df_final = None # Đặt biến chứa dữ liệu để mang đi vẽ biểu đồ

    try:
        # BƯỚC 1: XÁC ĐỊNH NGUỒN DỮ LIỆU SẼ DÙNG
        user_hien_tai = st.session_state['user_dang_nhap']

        # BƯỚC 1: XÁC ĐỊNH NGUỒN DỮ LIỆU SẼ DÙNG
        if uploaded_file is not None:
            # Ưu tiên 1: Đang up file mới
            df_goc = data.load_data(uploaded_file)
            df_final = data.xu_ly_data(df_goc)
            st.success("✅ Đã xử lý file Excel mới!")
            
            # Giao diện đặt tên file
            col_name, col_btn = st.columns([3, 1])
            with col_name:
                ten_file_moi = st.text_input("Tên lớp/Tên file (Ví dụ: Lớp 10A1):")
            with col_btn:
                st.write("") # Mẹo thụt dòng cho nút bấm ngang hàng với ô nhập text
                st.write("")
                if st.button("💾 Lưu Két sắt"):
                    if ten_file_moi.strip() == "":
                        st.warning("⚠️ Hãy nhập tên lớp trước khi lưu!")
                    else:
                        thanh_cong = database.luu_du_lieu_file(df_final, user_hien_tai, ten_file_moi)
                        if thanh_cong:
                            st.success(f"🎉 Đã cất điểm '{ten_file_moi}' vào tủ an toàn!")
                        else:
                            st.error("⚠️ Lỗi lưu file.")
                            
        else:
            # Ưu tiên 2: Không up file -> Hỏi xem tủ hồ sơ có gì không
            # =========================================================
            # [MỚI] CHẾ ĐỘ HIỆU TRƯỞNG (Dành riêng cho nick quan ham)
            # =========================================================
            if st.session_state.get('vai_tro') == 'Quan_tri':
                st.info("👨‍⚖️ Chế độ Hiệu trưởng: Quản lý toàn bộ dữ liệu nhà trường.")
                ds_giao_vien = database.lay_danh_sach_giao_vien_co_file()
                
                if len(ds_giao_vien) == 0:
                    st.warning("Hệ thống chưa có giáo viên nào nộp điểm.")
                else:
                    # Hiệu trưởng chọn giáo viên trước
                    gv_duoc_chon = st.selectbox("👨‍🏫 Chọn Giáo viên để kiểm tra:", ds_giao_vien)
                    
                    # Lấy danh sách lớp của giáo viên đó
                    ds_file_cua_gv = database.lay_danh_sach_file_cua_toi(gv_duoc_chon)
                    file_duoc_chon = st.selectbox("📂 Chọn Lớp:", ds_file_cua_gv)
                    
                    # Lôi dữ liệu ra vẽ biểu đồ
                    df_final = database.lay_du_lieu_file(gv_duoc_chon, file_duoc_chon)
                    
            # =========================================================
            # CHẾ ĐỘ GIÁO VIÊN BÌNH THƯỜNG
            # =========================================================
            else:
                danh_sach_file = database.lay_danh_sach_file_cua_toi(user_hien_tai)
                
                if len(danh_sach_file) == 0:
                    st.info("👈 Tủ hồ sơ trống. Mời thầy/cô tải file Excel ở cột bên trái.")
                else:
                    # Giáo viên thường chỉ thấy file của mình
                    file_duoc_chon = st.selectbox("📂 Chọn lớp để xem báo cáo:", danh_sach_file)
                    df_final = database.lay_du_lieu_file(user_hien_tai, file_duoc_chon)

        
        # =========================================================
        # BƯỚC 2: VẼ BIỂU ĐỒ VÀ BẢNG (Chỉ chạy khi đã có df_final)
        # =========================================================
        if df_final is not None:
            st.write("---")
            # --- Giai đoạn Hiển thị Chỉ số (Metrics) ---
            col1, col2, col3, col4 = st.columns(4)
            
            tong_hs = len(df_final)
            dtb_khoi = df_final['ĐTB'].mean()
            if 'Xếp loại' in df_final.columns:
                so_gioi = len(df_final[df_final['Xếp loại'] == 'Giỏi'])
            else:
                so_gioi = 0
            
            col1.metric("Tổng Sĩ Số", f"{tong_hs} HS")
            col2.metric("Điểm TB Khối", f"{dtb_khoi:.2f}")
            col3.metric("Học Sinh Giỏi", f"{so_gioi} HS")
            
            # tk_hien_tai = lay_thong_tin_tk()
            # col4.metric("User", tk_hien_tai['user'], delta="Online")
            col4.metric("User", st.session_state['user_dang_nhap'], delta="Online")

            st.markdown("### 1. Biểu đồ Tổng quan")
            # --- Giai đoạn Vẽ biểu đồ ---
            c1, c2 = st.columns(2)
            with c1:
                hinh1 = chart.ve_pho_diem(df_final)
                st.plotly_chart(hinh1, use_container_width=True)
            with c2:
                hinh2 = chart.ve_ti_le_xep_loai(df_final)
                st.plotly_chart(hinh2, use_container_width=True)
                
            st.write("_ _ _")
            st.markdown("### 2. So sánh thi đua giữa các lớp")
            hinh_so_sanh = chart.ve_so_sanh_lop(df_final)
            if hinh_so_sanh is not None:
                st.plotly_chart(hinh_so_sanh, use_container_width=True)
            else:
                st.info("⚠️ File không có cột 'Lớp' nên không thể so sánh.")

            c3, c4 = st.columns([2, 1])
            with c3:
                hinh3 = chart.ve_bieu_do_hop(df_final)
                st.plotly_chart(hinh3, use_container_width=True)
                st.caption("💡 Hướng dẫn: Hộp càng ngắn nghĩa là học lực của lớp càng đồng đều.")
            with c4:
                hinh4 = chart.ve_bieu_do_so_sanh_mon(df_final)
                st.plotly_chart(hinh4, use_container_width=True)
                st.caption("💡 Đường kẻ đỏ là mức trung bình (5.0). Cột nào dưới vạch đỏ là môn cần báo động.")

            # --- Giai đoạn Hiển thị bảng chi tiết & Bộ lọc ---
            st.write("---")
            st.subheader("📂 Danh sách chi tiết & Báo cáo")
            
            if 'Xếp loại' in df_final.columns:
                cac_loai = df_final['Xếp loại'].unique().tolist()
                cac_tuy_chon = ['Tất cả'] + cac_loai
                col_filter1, col_filter2 = st.columns(2)
                with col_filter1:
                    chon_loai = st.multiselect("Lọc theo Xếp loại:", options=cac_tuy_chon, default=['Tất cả'])
                
                if 'Tất cả' in chon_loai or len(chon_loai) == 0:
                    df_hien_thi = df_final
                else:
                    df_hien_thi = df_final[df_final['Xếp loại'].isin(chon_loai)]
            else:
                df_hien_thi = df_final

            st.dataframe(df_hien_thi, use_container_width=True)

            csv_data = df_hien_thi.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Tải danh sách về máy (CSV)",
                data=csv_data,
                file_name='ket_qua_hoc_tap.csv',
                mime='text/csv'
            )
            # --- GIAO DIỆN NÚT BẤM AI ---
            # --- GIAO DIỆN NÚT BẤM AI ---
            # ... (code cũ: if df_final is not None:)
        # ... (code cũ: st.dataframe(df_final, use_container_width=True))

        # =========================================================
        # 2. GIAO DIỆN TRỢ LÝ AI (AN TOÀN TUYỆT ĐỐI)
        # =========================================================
        st.write("---")
        with st.expander("🤖 Bật Trợ lý AI Phân tích Điểm số", expanded=False):
            st.info("💡 Mẹo: Hãy hỏi AI về những con số trong bảng phía trên (VD: Ai điểm cao nhất?).")
            
            # Khung hiển thị chat
            khung_chat = st.container(height=300)
            khung_chat.chat_message("ai").write("Chào thầy/cô! Tôi đã sẵn sàng phân tích dữ liệu.")
            
            # Khung nhập liệu
            col_text, col_voice = st.columns([4, 1])
            with col_text:
                cau_hoi_text = st.text_input("Nhập câu hỏi rồi nhấn Enter:")
                
                if cau_hoi_text:
                    khung_chat.chat_message("user").write(cau_hoi_text)
                    
                    # Ép bảng điểm thành định dạng văn bản CSV (Tránh lỗi thư viện tabulate)
                    du_lieu_chu = df_final.to_csv(index=False) 
                    
                    # Gom lệnh cho AI
                    lenh_cho_ai = f"""
                    Bạn là trợ lý ảo hỗ trợ giáo viên. Dưới đây là dữ liệu bảng điểm:
                    {du_lieu_chu}
                    
                    Câu hỏi của giáo viên: "{cau_hoi_text}"
                    Hãy dựa CHÍNH XÁC vào dữ liệu trên để trả lời ngắn gọn.
                    """
                    
                    # Gửi lệnh cho Gemini
                    try:
                        with st.spinner("AI đang phân tích..."):
                            ket_qua = model_ai.generate_content(lenh_cho_ai)
                            khung_chat.chat_message("ai").write(ket_qua.text)
                    except Exception as e:
                        khung_chat.error(f"⚠️ Lỗi hệ thống AI: {e}")
            
            with col_voice:
                st.write("")
                st.write("") 
                if st.button("🎙️ Nói"):
                    st.toast("⚠️ Tính năng Voice sẽ cập nhật ở phiên bản sau!")
    except Exception as e:
        st.error(f"⚠️ Có lỗi xảy ra: {e}")
        st.warning("Gợi ý: Hãy kiểm tra file Excel hoặc cấu trúc Database.")
    
    #giai đoạn1 đã xong

    # giai đoạn 2 : tự động nhận xét, bộ lọc dữ liệu và xuất báo cáo
    # giai đoạn 3: so sánh giữa các lớp với nhau 
    # giai doan 4: them dang nhap
if st.session_state['da_dang_nhap']==False:
    man_hinh_dang_nhap()
else:
    main_app()
