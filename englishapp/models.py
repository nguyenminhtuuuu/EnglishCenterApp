
from datetime import datetime
import json
from englishapp import db, app
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, DATETIME, Enum, Float
from sqlalchemy.orm import relationship, backref
from flask_login import UserMixin
from enum import Enum as RoleEnum


class UserEnum(RoleEnum):
    USER = 1
    ADMIN = 2
    TEACHER = 3
    CASHIER = 4

class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    active = Column(Boolean, default=True)
    created_date = Column(DateTime, default=datetime.now())
    def __str__(self):
        return self.name

class User(Base, UserMixin):
    username = Column(String(150), nullable=False, unique=True)
    password = Column(String(150), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    avatar = Column(String(300), default="https://res.cloudinary.com/deeqcwnpm/image/upload/v1764919829/cld-sample.jpg")
    role = Column(Enum(UserEnum), nullable=False, default=UserEnum.USER)


class Capdo(Base):
    khoahocs = relationship('Khoahoc', backref="Capdo", lazy=True)



class Khoahoc(Base):
    capDo_id = Column(Integer, ForeignKey(Capdo.id), nullable=False)
    hocPhi = Column(Integer, nullable=False)
    image = Column(String(300), default='https://res.cloudinary.com/deeqcwnpm/image/upload/v1765041156/daily_conversational_english_p81vyi.png')
    description = Column(String(300))
    lophocs = relationship('Lophoc', backref="Khoahoc", lazy=True)


class Lophoc(Base):
    soHVToiDa = Column(Integer, nullable=False)
    lichHoc = Column(String(50), nullable=False)
    ngayBD = Column(String(50), nullable=False)
    ngayKT = Column(String(50), nullable=False)
    maKH = Column(Integer, ForeignKey(Khoahoc.id), nullable=False)


class PhieuDangKy(db.Model):
    __tablename__ = 'phieudangky'

    id = Column(Integer, primary_key=True, autoincrement=True)
    maDK = Column(String(20), unique=True, nullable=False)
    ngayDK = Column(DateTime, default=datetime.now())
    trangThai = Column(String(50), default='Chờ xác nhận')
    hocvien_id = Column(Integer, ForeignKey(User.id), nullable=False)
    lophoc_id = Column(Integer, ForeignKey(Lophoc.id), nullable=False)

    # Quan hệ với HoaDon
    hoadon = relationship('HoaDon', backref='phieudangky', uselist=False, lazy=True)
    ketquahoctap = relationship('KetQuaHocTap', backref='phieudangky', uselist=False, lazy=True)

    def __str__(self):
        return self.maDK


class HoaDon(db.Model):
    __tablename__ = 'hoadon'

    id = Column(Integer, primary_key=True, autoincrement=True)
    maHD = Column(String(20), unique=True, nullable=False)
    ngayTao = Column(DateTime, default=datetime.now())
    tongTien = Column(Float, nullable=False)
    trangThai = Column(String(50), default='Chưa thanh toán')
    phuongThucTT = Column(String(50))
    phieudangky_id = Column(Integer, ForeignKey(PhieuDangKy.id), nullable=False)

    def __str__(self):
        return self.maHD


class KetQuaHocTap(db.Model):
    __tablename__ = 'ketquahoctap'

    id = Column(Integer, primary_key=True, autoincrement=True)
    diemGiuaKy = Column(Float, default=0)
    diemCuoiKy = Column(Float, default=0)
    diemTongKet = Column(Float, default=0)
    xepLoai = Column(String(20), default='Chưa xếp loại')
    trangThai = Column(String(20), default='Đang học')  # Đang học, Hoàn thành, Trượt
    phieudangky_id = Column(Integer, ForeignKey(PhieuDangKy.id), nullable=False)
    created_date = Column(DateTime, default=datetime.now())

    def __str__(self):
        return f"Kết quả {self.id} - Điểm: {self.diemTongKet}"

    @property
    def is_dat(self):
        return self.diemTongKet >= 5 if self.diemTongKet else False

if __name__ == "__main__":
    with app.app_context():
        # db.create_all()
        #
        # c1 = Capdo(name="Beginner")
        # c2 = Capdo(name="Intermediate")
        # c3 = Capdo(name="Advanced")
        # db.session.add_all([c1, c2, c3])
        # db.session.commit()
        #
        # with open("data/khoahoc.json", encoding="utf-8") as f:
        #     khoahoc = json.load(f)
        #
        #     for k in khoahoc:
        #         db.session.add(Khoahoc(**k))
        #
        #     db.session.commit()
        #
        #
        # with open("data/lophoc.json", encoding="utf-8") as f:
        #     lophoc = json.load(f)
        #
        #     for l in lophoc:
        #             db.session.add(Lophoc(**l))
        #
        # import hashlib
        #
        # # Tạo user mẫu
        # u1 = User(name="Admin", username="admin",
        #   password=str(hashlib.md5("123".encode("utf-8")).hexdigest()), email ="nguyenhuynhnhuybt@gmail.com",
        #   role=UserEnum.ADMIN)
        # u2 = User(name="User", username="user",
        #   password=str(hashlib.md5("123".encode("utf-8")).hexdigest()), email ="nhuy06022005@gmail.com",
        #   role=UserEnum.USER)
        #
        # db.session.add_all([u1,u2])
        db.session.commit()