#pandas de tinh toan 
# tu dong tinh toan va doc file excel
import pandas as pd

# doc du lieu 
def load_data(upload_file):
    if upload_file is not None: # kiem tra xem file co mo duoc ko?
        df=pd.read_excel(upload_file)# doc file tu bien 
        return df
    else:
        return None
# ham phu tro xep loai
def tieu_chi(diem_so):
    if diem_so>8:
        return "GIỎI"
    elif diem_so>=6.5:
        return "KHÁ"
    elif diem_so>=5.0:
        return "TRUNG BÌNH"
    else:
        return "YẾU "
# ham nhan xet cua giao vien
def tao_nhan_xet(row,danh_sach_mon):
    loi_nhan_xet=[]
    # tim cac mon bi diem kem
    mon_kem=[]
    for mon in danh_sach_mon:
        if row[mon]<5.0:
            mon_kem.append(mon)
    # logic sinh loi noi
    if len(mon_kem)==0:
        if row['ĐTB']>=8.0:
            return "Thành tích tốt, tiếp tục phát huy!"
        else:
            return "Học lực đồng đều,cần cố gắng đạt điểm cao hơn"
    else:
            #noi ten cac mon yeu
            ten_mon=",".join(mon_kem)
            return f"Cần cải thiện môn:{ten_mon}"

# xu ly cac ham tren
def xu_ly_data(df):
    if df is not None: # kiem tra xem khung co bi loi khong 
        cols=df.select_dtypes(include=['number']).columns.tolist()
        cols_to_exclude=['Tuổi','Năm sinh','SBD','Mã SV']
        danh_sach_mon=[c for c in cols if c not in cols_to_exclude]

        df['ĐTB']=df[danh_sach_mon].mean(axis=1) 
        # axis-1: tinh theo hang ngang( tung hoc sinh )
        df['ĐTB']=df['ĐTB'].round(2) # lam tron ket qua
        df['Xếp loại'] = df['ĐTB'].apply(tieu_chi)# dung ham apply() de goi ham tieu chi o tren
        # nhan xet
        df['Nhận xét của giáo viên']=df.apply(lambda row:tao_nhan_xet(row,danh_sach_mon),axis=1)
    return df
#hieu nom na cho ham so 3 la python se tinh trung binh cac hang khac tru cot ho ten,lop
# giai đoạn 1 tính toán cơ bản
# giai đoạn 2 : tự động sinh nhận xét