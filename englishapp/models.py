import json

from englishapp import db, app
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship, backref



class Base(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    def __str__(self):
        return self.name


class Capdo(Base):
    khoahocs = relationship('Khoahoc', backref="Capdo", lazy=True)



class Khoahoc(Base):
    capDo_id = Column(Integer, ForeignKey(Capdo.id), nullable=False)
    hocPhi = Column(Integer, nullable=False)
    image = Column(String(300), default='https://res.cloudinary.com/deeqcwnpm/image/upload/v1765041156/daily_conversational_english_p81vyi.png')
    lophocs = relationship('Lophoc', backref="Khoahoc", lazy=True)


class Lophoc(Base):
    soHVToiDa = Column(Integer, nullable=False)
    lichHoc = Column(String(50), nullable=False)
    ngayBD = Column(String(50), nullable=False)
    ngayKT = Column(String(50), nullable=False)
    maKH = Column(Integer, ForeignKey(Khoahoc.id), nullable=False)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
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
        #         db.session.add(Lophoc(**l))
        #
        #     db.session.commit()