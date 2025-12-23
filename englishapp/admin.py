from flask import redirect
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.theme import Bootstrap4Theme
from englishapp import app, db, dao
from englishapp.models import Capdo, Khoahoc,Lophoc, User, UserEnum
from flask_admin import BaseView
from flask_login import logout_user, current_user
from wtforms import TextAreaField
from wtforms.widgets import TextArea



class CKTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get('class'):
            kwargs['class'] += ' ckeditor'
        else:
            kwargs.setdefault('class', 'ckeditor')
        return super(CKTextAreaWidget, self).__call__(field, **kwargs)

class CKTextAreaField(TextAreaField):
    widget = CKTextAreaWidget()




class MyAuthenticatedView(ModelView):
    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.role==UserEnum.ADMIN



class MyCapdoView(MyAuthenticatedView):
    column_list = ["id", "name"]
    column_searchable_list = ["name"]
    column_filters = ["name"]


class MyKhoahocView(MyAuthenticatedView):
    column_list = ['name', 'hocPhi', 'image', 'Capdo', 'description']
    column_searchable_list = ["name"]
    column_filters = ["capDo_id", "name"]
    column_labels = {
        "name": "Tên khóa học",
        "hocPhi": "Học phí",
        "Capdo" : "Cấp độ"
    }
    can_export = True
    extra_js = ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']
    form_overrides = {
        'description': CKTextAreaField
    }


class MyLophocView(MyAuthenticatedView):
    column_list = ['name', 'soHVToiDa', 'lichHoc', 'ngayBD', 'ngayKT']
    column_searchable_list = ["name"]
    column_filters = ["lichHoc", "name"]
    column_labels = {
        "name": "Tên lớp học",
        "lichHoc": "Lịch học"
    }
    can_export = True
    extra_js = ['//cdn.ckeditor.com/4.6.0/standard/ckeditor.js']
    form_overrides = {
        'description': CKTextAreaField
    }



class MyAdminIndexView(AdminIndexView):
    @expose("/")
    def index(self) :
        return self.render('admin/index.html',cate_stats=dao.count_khoahoc_by_capdo())

class MyLogoutView(BaseView):
    @expose("/")
    def index(self):
        logout_user()
        return redirect("/admin")

    def is_accessible(self) -> bool:
        return current_user.is_authenticated


class ThongKeBaoCaoView(BaseView):
    @expose('/')
    def index(self) -> str:
        return redirect("/admin/thong-ke-bao-cao")

    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.role == UserEnum.ADMIN


class QuanLyHoaDonView(BaseView):
    @expose('/')
    def index(self) -> str:
        return redirect("/admin/hoadon")

    def is_accessible(self) -> bool:
        return current_user.is_authenticated and current_user.role == UserEnum.ADMIN

admin = Admin(app=app, name="Enghlish Center", theme=Bootstrap4Theme(), index_view=MyAdminIndexView())

admin.add_view(MyCapdoView(Capdo, db.session, name='Cấp độ', category='Quản lý'))
admin.add_view(MyKhoahocView(Khoahoc, db.session, name='Khóa học', category='Quản lý'))
admin.add_view(MyLophocView(Lophoc, db.session, name='Lớp học', category='Quản lý'))
admin.add_view(QuanLyHoaDonView("Quản lý hóa đơn", category='Báo cáo'))
admin.add_view(ThongKeBaoCaoView("Thống kê - Báo cáo", category='Báo cáo'))
admin.add_view(MyLogoutView("Đăng xuất"))






