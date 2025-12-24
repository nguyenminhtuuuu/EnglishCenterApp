import email
import json
import hashlib

from sqlalchemy import func, extract, case
from datetime import datetime, timedelta
from englishapp import app, db
# from models import Capdo, Khoahoc, Lophoc, User, PhieuDangKy, HoaDon, KetQuaHocTap, UserEnum
from englishapp.models import (
    Capdo, Khoahoc, Lophoc,
    User, PhieuDangKy,
    HoaDon, KetQuaHocTap
)
UserEnum = User.role.type.enum_class



def load_capdo():
    # with open("data/capdo.json", encoding="utf-8") as f:
    #      return json.load(f)
    return Capdo.query.all()

def load_khoahoc(q=None, id=None,capDo_id=None, page=None):
    # with open("data/khoahoc.json", encoding="utf-8") as f:
    #     khoahoc = json.load(f)
    #
    #     if q:
    #         #xử lý để không phân biệt hoa/thường
    #         q = q.lower()
    #         khoahoc = [k for k in khoahoc if q in k["name"].lower()]
    #
    #     if id:
    #         khoahoc = [k for k in khoahoc if k["id"].__eq__(int(id))]
    #
    #     return khoahoc





    query = Khoahoc.query

    if q:
        query = query.filter(Khoahoc.name.contains(q))

    if id:
        query = query.filter(Khoahoc.id.__eq__(id))

    if capDo_id:
        query = query.filter(Khoahoc.capDo_id == int(capDo_id))

    if page:
        size = app.config["PAGE_SIZE"]
        start = (int(page)-1)*size
        end = start + size
        query = query.slice(start, end)

    return query.all()




def add_user(name,username, password, avatar):
    password = hashlib.md5(password.strip().encode("utf-8")).hexdigest()
    u = User(name=name, username=username.strip(), password=password, email=email.strip(),avatar=avatar)
    db.session.add(u)
    db.session.commit()



def get_khoahoc_by_maKH(id):
    # with open("data/khoahoc.json", encoding="utf-8") as f:
    #     khoahoc = json.load(f)
    #
    #     for k in khoahoc:
    #         if k["id"].__eq__(id):
    #             return k

    return Khoahoc.query.get(id)



def get_lophoc_by_maKH(id):
    with open("data/lophoc.json", encoding="utf-8") as f:
        lophoc = json.load(f)

    result = []
    for l in lophoc:
        if l["maKH"] == id:
            result.append(l)

    return result


def auth_user(username, password):
    password= str(hashlib.md5(password.encode('utf-8')).hexdigest())
    return User.query.filter(User.username.__eq__(username)and User.password.__eq__(password)).first()


def get_user_by_id(id):
    return User.query.get(id)

def count_khoahoc():
    return Khoahoc.query.count()


def count_khoahoc_by_capdo():
    query = db.session.query(Capdo.id, Capdo.name, func.count(Khoahoc.id)).join(Khoahoc, Khoahoc.capDo_id.__eq__(Capdo.id), isouter=True).group_by(Capdo.id)

    #print(query)

    return query.all()

# ĐĂNG KÝ KHÓA HỌC
def dang_ky_khoa_hoc(hocvien_id, lophoc_id):
    try:
        lophoc = Lophoc.query.get(lophoc_id)
        if not lophoc:
            return False, "Lớp học không tồn tại", None

        # Kiểm tra số lượng học viên tối đa
        so_hv_da_dang_ky = PhieuDangKy.query.filter_by(
            lophoc_id=lophoc_id,
            trangThai__in=['Chờ xác nhận', 'Đã xác nhận']
        ).count()

        if so_hv_da_dang_ky >= lophoc.soHVToiDa:
            return False, "Lớp học đã đầy", None

        # Kiểm tra học viên đã đăng ký lớp này chưa
        dang_ky = PhieuDangKy.query.filter_by(
            hocvien_id=hocvien_id,
            lophoc_id=lophoc_id,
            trangThai__in=['Chờ xác nhận', 'Đã xác nhận']
        ).first()

        if dang_ky:
            return False, "Bạn đã đăng ký lớp học này rồi", None

        # Tạo mã đăng ký
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        maDK = f"DK{timestamp}"

        # Tạo phiếu đăng ký
        phieu_dk = PhieuDangKy(
            maDK=maDK,
            hocvien_id=hocvien_id,
            lophoc_id=lophoc_id,
            trangThai='Chờ xác nhận'
        )
        db.session.add(phieu_dk)
        db.session.flush()  # Lấy ID cho phieu_dk

        # Tạo hóa đơn
        maHD = f"HD{timestamp}"
        hoadon = HoaDon(
            maHD=maHD,
            tongTien=lophoc.Khoahoc.hocPhi,
            trangThai='Chưa thanh toán',
            phieudangky_id=phieu_dk.id
        )
        db.session.add(hoadon)

        db.session.commit()
        return True, "Đăng ký thành công! Vui lòng thanh toán học phí.", phieu_dk

    except Exception as e:
        db.session.rollback()
        return False, f"Có lỗi xảy ra: {str(e)}", None

def get_dang_ky_by_user(user_id):
    # Lấy danh sách phiếu đăng ký của user
    return PhieuDangKy.query.filter_by(hocvien_id=user_id).order_by(PhieuDangKy.ngayDK.desc()).all()

def get_hoadon_by_user(user_id):
    # Lấy danh sách hóa đơn của user
    return HoaDon.query.join(PhieuDangKy).filter(PhieuDangKy.hocvien_id == user_id).order_by(
        HoaDon.ngayTao.desc()).all()


# QUẢN LÝ HÓA ĐƠN
def get_all_hoadon(trangThai=None, keyword=None):
    # Lấy tất cả hóa đơn
    query = HoaDon.query.join(PhieuDangKy).join(User).join(Lophoc).join(Khoahoc)

    if trangThai:
        query = query.filter(HoaDon.trangThai == trangThai)

    if keyword:
        query = query.filter(
            (User.name.contains(keyword)) |
            (User.phone.contains(keyword)) |
            (HoaDon.maHD.contains(keyword)) |
            (Khoahoc.name.contains(keyword))
        )

    return query.order_by(HoaDon.ngayTao.desc()).all()


def get_hoadon_by_id(hoadon_id):
    return HoaDon.query.get(hoadon_id)


def update_trangthai_hoadon(hoadon_id, trangThai, phuongThucTT=None):
    try:
        hoadon = HoaDon.query.get(hoadon_id)
        if not hoadon:
            return False, "Hóa đơn không tồn tại"

        hoadon.trangThai = trangThai

        if phuongThucTT:
            hoadon.phuongThucTT = phuongThucTT

        if trangThai == 'Đã thanh toán':
            hoadon.phieudangky.trangThai = 'Đã xác nhận'

        db.session.commit()
        return True, "Cập nhật thành công"

    except Exception as e:
        db.session.rollback()
        return False, f"Có lỗi xảy ra: {str(e)}"


# THỐNG KÊ BÁO CÁO
# PHẦN THỐNG KÊ
def thong_ke_so_luong_hv_theo_khoa():
    return db.session.query(
        Khoahoc.name.label('ten_khoa_hoc'),
        func.count(PhieuDangKy.id).label('so_luong_hv')
    ).join(Lophoc, Khoahoc.id == Lophoc.maKH)\
     .join(PhieuDangKy, Lophoc.id == PhieuDangKy.lophoc_id)\
     .filter(PhieuDangKy.trangThai == 'Đã xác nhận')\
     .group_by(Khoahoc.id)\
     .order_by(func.count(PhieuDangKy.id).desc())\
     .all()


def thong_ke_ty_le_dat_theo_khoa():
    """
    Thống kê tỷ lệ đạt theo khóa học
    """
    results = db.session.query(
        Khoahoc.name.label('ten_khoa_hoc'),
        func.count(KetQuaHocTap.id).label('tong_so'),
        func.count(
            case(
                (KetQuaHocTap.diemTongKet >= 5, 1),
                else_=None
            )
        ).label('so_dat'),

        func.avg(KetQuaHocTap.diemTongKet).label('diem_trung_binh')
        ).join(Lophoc, Khoahoc.id == Lophoc.maKH) \
            .join(PhieuDangKy, Lophoc.id == PhieuDangKy.lophoc_id) \
            .join(KetQuaHocTap, PhieuDangKy.id == KetQuaHocTap.phieudangky_id) \
            .filter(KetQuaHocTap.trangThai == 'Hoàn thành') \
            .group_by(Khoahoc.id) \
            .all()

    # Tính tỷ lệ đạt
    for result in results:
        if result.tong_so > 0:
            result.ty_le_dat = round((result.so_dat / result.tong_so) * 100, 2)
        else:
            result.ty_le_dat = 0

    return results


# PHẦN BÁO CÁO
def bao_cao_doanh_thu_theo_thang(nam=None):
    query = db.session.query(
        extract('month', HoaDon.ngayTao).label('thang'),
        extract('year', HoaDon.ngayTao).label('nam'),
        func.count(HoaDon.id).label('so_hoa_don'),
        func.sum(HoaDon.tongTien).label('doanh_thu')
    ).filter(HoaDon.trangThai == 'Đã thanh toán')

    if nam:
        query = query.filter(extract('year', HoaDon.ngayTao) == nam)

    return query.group_by('nam', 'thang') \
        .order_by('nam', 'thang') \
        .all()


def bao_cao_doanh_thu_theo_khoa(tu_ngay=None, den_ngay=None):
    query = db.session.query(
        Khoahoc.name.label('ten_khoa_hoc'),
        Capdo.name.label('cap_do'),
        func.count(HoaDon.id).label('so_hoa_don'),
        func.sum(HoaDon.tongTien).label('doanh_thu')
    ).join(Lophoc, Khoahoc.id == Lophoc.maKH) \
        .join(Capdo, Khoahoc.capDo_id == Capdo.id) \
        .join(PhieuDangKy, Lophoc.id == PhieuDangKy.lophoc_id) \
        .join(HoaDon, PhieuDangKy.id == HoaDon.phieudangky_id) \
        .filter(HoaDon.trangThai == 'Đã thanh toán')

    if tu_ngay:
        query = query.filter(HoaDon.ngayTao >= tu_ngay)
    if den_ngay:
        query = query.filter(HoaDon.ngayTao <= den_ngay)

    return query.group_by(Khoahoc.id, Capdo.id) \
        .order_by(func.sum(HoaDon.tongTien).desc()) \
        .all()


def thong_ke_tong_quan():
    tong_hoc_vien = User.query.filter(User.role == UserEnum.USER).count()

    # tong_hoc_vien = User.query.filter_by(role=UserEnum.USER).count()
    tong_khoa_hoc = Khoahoc.query.count()
    tong_lop_hoc = Lophoc.query.count()

    # Doanh thu tổng
    tong_doanh_thu = db.session.query(func.sum(HoaDon.tongTien)) \
                         .filter(HoaDon.trangThai == 'Đã thanh toán') \
                         .scalar() or 0

    # Số hóa đơn đã thanh toán
    tong_hoa_don = HoaDon.query.filter_by(trangThai='Đã thanh toán').count()

    return {
        'tong_hoc_vien': tong_hoc_vien,
        'tong_khoa_hoc': tong_khoa_hoc,
        'tong_lop_hoc': tong_lop_hoc,
        'tong_doanh_thu': tong_doanh_thu,
        'tong_hoa_don': tong_hoa_don
    }


def get_nam_co_du_lieu():
    """
    Lấy danh sách năm có dữ liệu
    """
    years = db.session.query(
        extract('year', HoaDon.ngayTao).label('nam')
    ).filter(HoaDon.trangThai == 'Đã thanh toán') \
        .group_by('nam') \
        .order_by('nam') \
        .all()

    return [year.nam for year in years]

def get_lophoc_by_id(lophoc_id):
    return Lophoc.query.get(lophoc_id)

def get_classes_by_teacher(teacher_id):
    return Lophoc.query.filter_by(giaoVien_id=teacher_id).all()

def get_hocvien_in_lophoc(lophoc_id):
    return PhieuDangKy.query.filter(
        PhieuDangKy.lophoc_id == lophoc_id,
        PhieuDangKy.trangThai == 'Đã xác nhận'  # Chỉ hiện học viên đã đóng tiền
    ).all()


def luu_ket_qua_hoc_tap(phieu_id, diem_gk, diem_ck):
    try:
        ket_qua = KetQuaHocTap.query.filter_by(phieudangky_id=phieu_id).first()
        if not ket_qua:
            ket_qua = KetQuaHocTap(phieudangky_id=phieu_id)
            db.session.add(ket_qua)
        ket_qua.diemGiuaKy = float(diem_gk)
        ket_qua.diemCuoiKy = float(diem_ck)

        if hasattr(ket_qua, 'tinh_diem_tong_ket'):
            ket_qua.tinh_diem_tong_ket()
        else:
            ket_qua.diemTongKet = round((ket_qua.diemGiuaKy * 0.4) + (ket_qua.diemCuoiKy * 0.6), 2)
        db.session.commit()
        return True, "Lưu thành công"

    except Exception as e:
        db.session.rollback()
        print(e)
        return False, f"Lỗi: {str(e)}"
if __name__ == '__main__':
    with app.app_context():
        print(count_khoahoc_by_capdo())

        # print("Thống kê số lượng học viên theo khóa:")
        # print(thong_ke_so_luong_hv_theo_khoa())
        # print("\nThống kê tổng quan:")
        # print(thong_ke_tong_quan())
