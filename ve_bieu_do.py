import plotly.express as px 
import plotly.graph_objects as go 

# 1. HÀM VẼ PHỔ ĐIỂM
def ve_pho_diem(df):
    fig = px.histogram(
        data_frame=df,      # SỬA: Đưa biến df vào, không dùng ngoặc kép
        x="ĐTB",            # LƯU Ý: Tên cột phải khớp bên file xuly_du_lieu
        nbins=10,           # SỬA: Nên để 10 cột cho thang điểm 10
        title="Phổ Điểm Trung Bình",
        text_auto=True,     # SỬA: Python dùng True viết hoa
        color_discrete_sequence=['#636EFA']
    )
    return fig

# 2. HÀM VẼ BIỂU ĐỒ TRÒN
def ve_ti_le_xep_loai(df): # Sửa tên hàm cho thống nhất
    # Thống kê trước khi vẽ
    # LƯU Ý: Cột cần đếm là 'Xếp loại', không phải 'dem so luong'
    thong_ke = df['Xếp loại'].value_counts().reset_index()
    thong_ke.columns = ['Loại', 'Số lượng']
    
    fig = px.pie(
        data_frame=thong_ke,
        names="Loại",       # Tên miếng bánh (lấy từ bảng thong_ke)
        values="Số lượng",  # Độ to miếng bánh (lấy từ bảng thong_ke)
        title="Tỷ lệ Xếp loại",
        hole=0.4
    )
    return fig

# 3. HÀM VẼ BOXPLOT
def ve_bieu_do_hop(df):
    cols = df.select_dtypes(include=['number']).columns.tolist()
   #loai bo cac cot ko lien quan den tinh toan  
    cols_to_exclude=['ĐTB','Tuổi','Năm sinh','SBD']
    cols=[c for c in cols if c not in cols_to_exclude]
    # ve box plot
    fig=px.box(
        df,
        y=cols,# truyen danh sach cac mon truc y
        title="Phân bố điểm từng môn",
        points="all"#hiển thị cả các điểm chấm dại diện 
    )
    return fig            # SỬA: Trả về fig, không phải gif

# 4. BAR CHART so sánh 
def ve_bieu_do_so_sanh_mon(df):
    # Lấy danh sách cột môn học giống hệt hàm trên
    cols = df.select_dtypes(include=['number']).columns.tolist()
    cols_to_exclude = ['ĐTB', 'Tuổi', 'Năm sinh', 'SBD']
    cols = [c for c in cols if c not in cols_to_exclude]
    
    # Tính trung bình của từng môn
    # Ví dụ: Python: 7.5, Mạng: 6.0 ...
    tb_mon = df[cols].mean().reset_index()
    tb_mon.columns = ['Môn học', 'Điểm TB']
    
    # Vẽ biểu đồ cột ngang hoặc dọc
    fig = px.bar(
        tb_mon,
        x='Môn học',
        y='Điểm TB',
        title="So sánh Điểm Trung Bình giữa các môn",
        text_auto='.2f', # Hiện số điểm làm tròn 2 chữ số
        color='Điểm TB', # Tô màu theo điểm (Cao thì màu sáng, thấp màu tối)
        color_continuous_scale='Viridis' # Dải màu xanh lá - tím rất đẹp
    )
    
    # Kẻ thêm một đường ngang màu đỏ ở mức 5.0 (Mức trung bình)
    fig.add_shape(
        type="line",
        x0=-0.5, x1=len(cols)-0.5, # Kẻ hết chiều ngang biểu đồ
        y0=5.0, y1=5.0,            # Kẻ ở độ cao 5.0
        line=dict(color="Red", width=2, dash="dash"), # Đường nét đứt màu đỏ
    )
    
    return fig
# bieu dô so sanh giua cac lop (new)
def ve_so_sanh_lop(df):
    #kiem tra xem file ex co cot lop ko--> loi neu ko co
    if 'Lớp' not in df.columns:
        return None # ko co se ko ve
    # tinh diem tb tung lop
    # groupby: gom nhom cac ban cung lop lai--> tinh trung binh cot DTB
    tk_lop=df.groupby('Lớp')['ĐTB'].mean().reset_index()

    #sap xep theo thu tu giam dan
    tk_lop=tk_lop.sort_values(by='ĐTB',ascending=False)
    #ve bieu do cot
    fig=px.bar(
        tk_lop,
        x='Lớp',
        y='ĐTB',
        title="So sánh thành tích trung bình giữa các lớp",
        text_auto='.2f',# hien thi so diem tren cot
        color='Lớp'
    )
    return fig

