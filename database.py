import sqlite3
import pandas as pd 
import json
# Tên file database của dự án
DB_NAME = 'edudata.db'

# ========================================================
# 1. HÀM KHỞI TẠO BẢNG (CÓ THÊM CỘT VAI TRÒ)
# ========================================================
def khoi_tao_he_thong():
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # Tạo bảng nếu chưa có (Có thêm cột vai_tro mặc định là Giao_vien)
        cursor.execute('''CREATE TABLE IF NOT EXISTS GiaoVien 
                          (username TEXT PRIMARY KEY, password TEXT, vai_tro TEXT DEFAULT 'Giao_vien')''')
        
        # [Mẹo thông minh]: Nếu bảng cũ chưa có cột vai_tro, ta ép nó mọc thêm cột mới!
        try:
            cursor.execute("ALTER TABLE GiaoVien ADD COLUMN vai_tro TEXT DEFAULT 'Giao_vien'")
        except:
            pass # Lỗi văng ra khi cột đã có sẵn -> Ta kệ nó, bỏ qua.

        # Bơm nick admin tối cao (bắt buộc phải là Quan_tri)
        cursor.execute("SELECT * FROM GiaoVien WHERE username = 'admin'")
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO GiaoVien (username, password, vai_tro) VALUES ('admin', '123', 'Quan_tri')")
        else:
            # Lỡ admin bị giáng chức thì buff lại lên làm Quan_tri
            cursor.execute("UPDATE GiaoVien SET vai_tro = 'Quan_tri' WHERE username = 'admin'")
            
        conn.commit()
        conn.close()
    except Exception as e:
        print("Lỗi khởi tạo:", e)

khoi_tao_he_thong() # Kích hoạt

# ========================================================
# 2. CÁC HÀM QUẢN LÝ QUYỀN (THÊM VÀO DƯỚI CÙNG FILE)
# ========================================================
def lay_vai_tro(username):
    """Hỏi xem người này chức vụ gì"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT vai_tro FROM GiaoVien WHERE username = ?", (username,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else 'Giao_vien'
    except:
        return 'Giao_vien'

def cap_nhat_quyen(username, vai_tro_moi):
    """Admin dùng hàm này để thăng chức/giáng chức người khác"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("UPDATE GiaoVien SET vai_tro = ? WHERE username = ?", (vai_tro_moi, username))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def lay_danh_sach_tai_khoan_va_quyen():
    """Lấy danh sách cho Admin xem ai đang làm chức gì"""
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql_query("SELECT username, vai_tro FROM GiaoVien", conn)
        conn.close()
        return df
    except:
        return None

def tao_co_so_du_lieu():
    """Hàm này dùng để khởi tạo file database và xây các bảng (chỉ chạy 1 lần đầu)"""
    # 1. Mở cửa kết nối vào database (nếu chưa có, Python sẽ tự tạo file edudata.db)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # 2. Xây bảng GiaoVien
    # Dùng IF NOT EXISTS để lỡ chạy code nhiều lần cũng không bị lỗi báo bảng đã tồn tại
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS GiaoVien (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT
        )
    ''')

    # 3. Lưu lại các thay đổi và đóng cửa sổ kết nối
    conn.commit()
    conn.close()
    print("✅ Đã khởi tạo thành công Cơ sở dữ liệu EduData!")

def them_tai_khoan(user, password, email):
    """Hàm để thêm một giáo viên mới vào hệ thống"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Dùng dấu '?' để chống bị hacker tấn công SQL Injection
        cursor.execute('''
            INSERT INTO GiaoVien (username, password, email) 
            VALUES (?, ?, ?)
        ''', (user, password, email))
        
        conn.commit()
        conn.close()
        print(f"✅ Đã thêm tài khoản: {user}")
        return True
    except sqlite3.IntegrityError:
        print("⚠️ Lỗi: Tên đăng nhập này đã tồn tại rồi!")
        return False

def kiem_tra_dang_nhap(user, password):
    """Hàm dùng để so sánh lúc giáo viên gõ pass trên màn hình đăng nhập"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Lấy tài khoản có username và password khớp với người dùng nhập
    cursor.execute('''
        SELECT * FROM GiaoVien 
        WHERE username = ? AND password = ?
    ''', (user, password))
    
    tai_khoan = cursor.fetchone() # Lấy ra 1 kết quả đầu tiên
    conn.close()
    
    if tai_khoan is not None:
        return True # Đăng nhập đúng
    else:
        return False # Đăng nhập sai

# --- PHẦN CHẠY THỬ (TEST) ---
if __name__ == '__main__':
    # 1. Tạo file và bảng
    tao_co_so_du_lieu()
    
    # 2. Thêm thử 2 tài khoản (Chạy lần thứ 2 nó sẽ báo lỗi trùng lặp là tính năng hoạt động đúng nhé)
    them_tai_khoan("admin", "123", "admin@gmail.com")
    them_tai_khoan("thayhung", "pass123", "hung@gmail.com")
    
    # 3. Test thử đăng nhập
    print("Test đăng nhập admin/123:", kiem_tra_dang_nhap("admin", "123")) # Sẽ in ra True
    print("Test đăng nhập admin/sai_pass:", kiem_tra_dang_nhap("admin", "456")) # Sẽ in ra False

def luu_du_lieu_file(df, nguoi_tao, ten_file):
    """Nén toàn bộ bảng df thành 1 cục JSON và nhét vào tủ hồ sơ"""
    import json # Khai báo thêm ở đây cho chắc chắn
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # 1. Tạo Tủ hồ sơ (Bảng KhoDuLieu) nếu chưa có
        cursor.execute('''CREATE TABLE IF NOT EXISTS KhoDuLieu 
                          (nguoi_tao TEXT, ten_file TEXT, du_lieu TEXT)''')
                          
        # 2. Chuyển DataFrame thành chuỗi văn bản JSON
        du_lieu_json = df.to_json(orient='records')
        
        # 3. Nếu đã có file tên này rồi thì xóa đi để lưu bản mới (Tránh trùng lặp)
        cursor.execute("DELETE FROM KhoDuLieu WHERE nguoi_tao = ? AND ten_file = ?", (nguoi_tao, ten_file))
        
        # 4. Tống vào tủ
        cursor.execute("INSERT INTO KhoDuLieu VALUES (?, ?, ?)", (nguoi_tao, ten_file, du_lieu_json))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("Lỗi lưu file:", e)
        return False

def lay_danh_sach_file_cua_toi(nguoi_tao):
    """Hỏi tủ xem giáo viên này đang cất những file nào trong đó"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT ten_file FROM KhoDuLieu WHERE nguoi_tao = ?", (nguoi_tao,))
        # Gom kết quả thành một danh sách (List)
        danh_sach = [row[0] for row in cursor.fetchall()]
        conn.close()
        return danh_sach
    except Exception:
        return []

def lay_du_lieu_file(nguoi_tao, ten_file):
    """Lôi cục văn bản JSON ra và biến nó lại thành DataFrame"""
    import pandas as pd
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute("SELECT du_lieu FROM KhoDuLieu WHERE nguoi_tao = ? AND ten_file = ?", (nguoi_tao, ten_file))
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # Giải nén JSON thành bảng DataFrame
            return pd.read_json(row[0], orient='records')
        return None
    except Exception as e:
        print("Lỗi lấy file:", e)
        return None
        
def doi_mat_khau(user, pass_moi):
    """Hàm cập nhật mật khẩu mới vào Database"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        cursor.execute('UPDATE GiaoVien SET password = ? WHERE username = ?', (pass_moi, user))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print("Lỗi đổi mật khẩu:", e)
        return False
# --- BỔ SUNG VÀO DATABASE.PY ---

def tao_tai_khoan(username, password):
    """Hàm cấp thẻ (tạo nick) cho giáo viên mới"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # Nhét tài khoản mới vào Sổ hộ khẩu (Bảng GiaoVien)
        cursor.execute("INSERT INTO GiaoVien (username, password) VALUES (?, ?)", (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # Lỗi này văng ra khi Tên đăng nhập đã có người xài
        return False
    except Exception as e:
        print("Lỗi tạo tài khoản:", e)
        return False

def lay_danh_sach_giao_vien_co_file():
    """Hàm dành riêng cho Hiệu trưởng: Tìm xem những ai đã nộp điểm"""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # Lệnh DISTINCT giúp lọc ra danh sách không bị trùng lặp tên
        cursor.execute("SELECT DISTINCT nguoi_tao FROM KhoDuLieu")
        danh_sach = [row[0] for row in cursor.fetchall()]
        conn.close()
        return danh_sach
    except Exception:
        return []