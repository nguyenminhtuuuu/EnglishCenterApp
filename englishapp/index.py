import cloudinary
from flask import render_template, request, redirect, flash, url_for
import math
from englishapp import dao, app, login, admin, db
from flask_login import login_user, current_user, logout_user
import cloudinary.uploader




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

        # import pdb #kiểm tra lỗi
        # pdb.set_trace()

        if password.__eq__(confirm):
            name = request.form.get("name")
            username = request.form.get("username")
            avatar = request.files.get("avatar")

            path_file = None
            if avatar:
                res = cloudinary.uploader.upload(avatar)
                path_file = res["secure_url"]
            try:
                dao.add_user(name, username, password, avatar=path_file)
                return redirect('/login')
            except:
                db.session.rollback()
                err_msg="Hệ thống đang có lỗi! Vui lòng quay lại sau!"
        else:
            err_msg = "Mật khẩu không khớp!"


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

if __name__ == '__main__':
    with app.app_context():
        app.run(debug=True,port=5000)
