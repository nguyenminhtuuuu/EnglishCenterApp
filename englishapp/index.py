import re

import cloudinary
from flask import render_template, request, redirect, flash, url_for, jsonify
import math
from englishapp import dao, app, login, admin, db
from flask_login import login_user, current_user, logout_user, login_required
import cloudinary.uploader

from englishapp.models import UserEnum


@app.route('/')
def index():
    q = request.args.get('q')
    capDo_id = request.args.get('capDo_id')
    page = request.args.get('page')
    khoahoc = dao.load_khoahoc(q=q, capDo_id=capDo_id, page=page)
    message = None
    if q and not khoahoc:
        message = f"Không tìm thấy khóa học! Vui lòng tìm kiếm khóa học khác!"
    pages = math.ceil(dao.count_khoahoc()/app.config["PAGE_SIZE"])

    return render_template('index.html', khoahoc=khoahoc, message=message, pages=pages)


@app.route("/khoahoc/<int:id>")
def details(id):
    kh = dao.get_khoahoc_by_maKH(id)
    lh = dao.get_lophoc_by_maKH(id)
    return render_template("chitiet-khoahoc.html", kh=kh, lh=lh)



@app.route("/login", methods=['get', 'post'])
def login_my_user():
    if current_user.is_authenticated:
        return redirect('/')


    err_msg = None
    if request.method.__eq__('POST'):
        username = request.form.get("username")
        password = request.form.get("password")

        user = dao.auth_user(username, password)

        if user:
            login_user(user)
            return redirect('/')
        else:
            flash("Tài khoản hoặc mật khẩu không đúng!", "danger")
            return redirect(url_for('login_my_user'))


    return render_template("login.html")

@app.context_processor #định danh biến toàn cục
def common_attribute():
    return {
        "capdo" : dao.load_capdo()
    }

@app.route("/logout")
def logout_my_user():
    logout_user()
    return redirect('/login')



@app.route("/register",  methods=['get', 'post'])
def register():
    err_msg = None

    if request.method.__eq__("POST"):
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        email = request.form.get('email')
        # import pdb #kiểm tra lỗi
        # pdb.set_trace()

        if not password.__eq__(confirm):
            err_msg = "Mật khẩu không khớp!"
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            err_msg = "Định dạng email không hợp lệ!"
        else:
            name = request.form.get("name")
            username = request.form.get("username")
            avatar = request.files.get("avatar")
            path_file = None
            if avatar:
                res = cloudinary.uploader.upload(avatar)
                path_file = res["secure_url"]
            try:
                dao.add_user(name, username, password, email, avatar=path_file)
                return redirect('/login')
            except:
                db.session.rollback()
                err_msg = "Hệ thống đang có lỗi! Vui lòng quay lại sau!"


    return render_template("register.html", err_msg=err_msg)




@login.user_loader
def get_user(user_id):
    return dao.get_user_by_id(user_id)


@app.route("/admin-login", methods=["post"])
def login_admin_process():
    username = request.form.get("username")
    password = request.form.get("password")

    user = dao.auth_user(username, password)

    if user:
        login_user(user)
        return redirect("/admin")

    else:
        err_msg = "Tài khoản hoặc mật khẩu không đúng!"


# ĐĂNG KÝ KHÓA HỌC
@app.route("/dangky/<int:lophoc_id>")
@login_required
def dang_ky_khoa_hoc(lophoc_id):
    success, message, phieu_dk = dao.dang_ky_khoa_hoc(current_user.id, lophoc_id)

    if success:
        flash(message, "success")
        return redirect(url_for('xem_phieu_dang_ky'))
    else:
        flash(message, "danger")
        lophoc = dao.Lophoc.query.get(lophoc_id)
        return redirect(url_for('details', id=lophoc.maKH))


@app.route("/phieu-dang-ky")
@login_required
def xem_phieu_dang_ky():
    phieu_dk = dao.get_dang_ky_by_user(current_user.id)
    return render_template("phieu-dang-ky.html", phieu_dk=phieu_dk)


@app.route("/hoadon-cua-toi")
@login_required
def hoadon_cua_toi():
    if current_user.role != UserEnum.USER:
        flash("Bạn không có quyền truy cập!", "danger")
        return redirect('/')

    hoadons = dao.get_hoadon_by_user(current_user.id)
    return render_template("hoadon-user.html", hoadons=hoadons)


@app.route("/hoadon/<int:hoadon_id>/thanh-toan", methods=["POST"])
@login_required
def thanh_toan_hoadon(hoadon_id):
    if current_user.role != UserEnum.USER:
        flash("Bạn không có quyền thực hiện chức năng này!", "danger")
        return redirect('/')

    phuongThucTT = request.form.get('phuongThucTT')

    hoadon = dao.get_hoadon_by_id(hoadon_id)
    if not hoadon or hoadon.phieudangky.hocvien_id != current_user.id:
        flash("Hóa đơn không tồn tại hoặc không thuộc về bạn!", "danger")
        return redirect(url_for('hoadon_cua_toi'))

    success, message = dao.update_trangthai_hoadon(hoadon_id, 'Đã thanh toán', phuongThucTT)

    if success:
        flash(message, "success")
    else:
        flash(message, "danger")

    return redirect(url_for('hoadon_cua_toi'))


# QUẢN LÝ HÓA ĐƠN
@app.route("/admin/hoadon")
@login_required
def quan_ly_hoadon():
    if current_user.role != UserEnum.ADMIN:
        flash("Bạn không có quyền truy cập trang này!", "danger")
        return redirect('/')

    trangThai = request.args.get('trangThai')
    keyword = request.args.get('keyword')
    hoadons = dao.get_all_hoadon(trangThai=trangThai, keyword=keyword)

    tong_doanh_thu = sum(h.tongTien for h in hoadons if h.trangThai == 'Đã thanh toán')

    return render_template("quan-ly-hoadon.html",
                           hoadons=hoadons,
                           tong_doanh_thu=tong_doanh_thu,
                           trangThai=trangThai,
                           keyword=keyword)


@app.route("/admin/hoadon/<int:hoadon_id>/update", methods=["POST"])
@login_required
def update_hoadon_admin(hoadon_id):
    if current_user.role != UserEnum.ADMIN:
        flash("Bạn không có quyền thực hiện chức năng này!", "danger")
        return redirect('/')

    trangThai = request.form.get('trangThai')
    phuongThucTT = request.form.get('phuongThucTT')

    success, message = dao.update_trangthai_hoadon(hoadon_id, trangThai, phuongThucTT)

    if success:
        flash(message, "success")
    else:
        flash(message, "danger")

    return redirect(url_for('quan_ly_hoadon'))


# THỐNG KÊ - BÁO CÁO
@app.route("/admin/thong-ke-bao-cao")
@login_required
def thong_ke_bao_cao():
    if current_user.role != UserEnum.ADMIN:
        flash("Bạn không có quyền truy cập trang này!", "danger")
        return redirect('/')

    # Lấy tham số
    nam = request.args.get('nam')
    if nam:
        nam = int(nam)

    # PHẦN THỐNG KÊ
    so_luong_hv = dao.thong_ke_so_luong_hv_theo_khoa()
    ty_le_dat = dao.thong_ke_ty_le_dat_theo_khoa()

    # PHẦN BÁO CÁO
    doanh_thu_thang = dao.bao_cao_doanh_thu_theo_thang(nam)
    doanh_thu_khoa = dao.bao_cao_doanh_thu_theo_khoa()
    # Thống kê tổng quan
    tong_quan = dao.thong_ke_tong_quan()

    # Danh sách năm có dữ liệu
    nam_co_du_lieu = dao.get_nam_co_du_lieu()

    return render_template("thong-ke-bao-cao.html",
                           so_luong_hv=so_luong_hv,
                           ty_le_dat=ty_le_dat,
                           doanh_thu_thang=doanh_thu_thang,
                           doanh_thu_khoa=doanh_thu_khoa,
                           tong_quan=tong_quan,
                           nam_co_du_lieu=nam_co_du_lieu,
                           nam_hien_tai=nam)


# API cho biểu đồ
@app.route("/admin/api/so-luong-hv-theo-khoa")
@login_required
def api_so_luong_hv_theo_khoa():
    if current_user.role != UserEnum.ADMIN:
        return jsonify({"error": "Unauthorized"}), 403

    data = dao.thong_ke_so_luong_hv_theo_khoa()

    labels = [item.ten_khoa_hoc for item in data]
    values = [int(item.so_luong_hv or 0) for item in data]

    return jsonify({
        "labels": labels,
        "datasets": [{
            "label": "Số lượng học viên",
            "data": values,
            "backgroundColor": [
                'rgba(255, 99, 132, 0.7)',
                'rgba(54, 162, 235, 0.7)',
                'rgba(255, 206, 86, 0.7)',
                'rgba(75, 192, 192, 0.7)',
                'rgba(153, 102, 255, 0.7)',
                'rgba(255, 159, 64, 0.7)',
                'rgba(201, 203, 207, 0.7)'
            ]
        }]
    })

@app.route("/admin/api/doanh-thu-theo-thang")
@login_required
def api_doanh_thu_theo_thang():
    if current_user.role != UserEnum.ADMIN:
        return jsonify({"error": "Unauthorized"}), 403

    nam = request.args.get('nam')
    if nam:
        nam = int(nam)

    data = dao.bao_cao_doanh_thu_theo_thang(nam)

    # Chuẩn bị dữ liệu cho biểu đồ
    months = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10', 'T11', 'T12']
    doanh_thu_data = [0] * 12

    for item in data:
        thang = int(item.thang)
        if 1 <= thang <= 12:
            doanh_thu_data[thang - 1] = float(item.doanh_thu or 0)
    return jsonify({
        "labels": months,
        "datasets": [{
            "label": "Doanh thu ($)",
            "data": doanh_thu_data,
            "backgroundColor": "rgba(54, 162, 235, 0.5)",
            "borderColor": "rgba(54, 162, 235, 1)",
            "borderWidth": 1
        }]
    })



if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True,port=5000)
