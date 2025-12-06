from flask import render_template, request
from englishapp import dao, app



@app.route('/')
def index():
    q = request.args.get('q')
    capDo_id = request.args.get('capDo_id')
    khoahoc = dao.load_khoahoc(q=q, capDo_id=capDo_id)
    return render_template('index.html', khoahoc=khoahoc)



@app.route("/khoahoc/<int:maKH>")
def details(maKH):
    kh = dao.get_khoahoc_by_maKH(maKH)
    return render_template("chitiet-khoahoc.html", kh=kh)

@app.context_processor #định danh biến toàn cục
def common_attribute():
    return {
        "capdo" : dao.load_capdo()
    }

if __name__ == '__main__':
    app.run(debug=True)
