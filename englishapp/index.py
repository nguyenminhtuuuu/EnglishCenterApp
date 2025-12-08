from flask import render_template, request, redirect
import math
from englishapp import dao, app


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

    if request.method.__eq__('POST'):
        username = request.form.get("username")
        password = request.form.get("password")

        if username.__eq__("user") and password.__eq__("123"):
         return redirect('/')

    return render_template("login.html")

@app.context_processor #định danh biến toàn cục
def common_attribute():
    return {
        "capdo" : dao.load_capdo()
    }


if __name__ == '__main__':
    app.run(debug=True)
