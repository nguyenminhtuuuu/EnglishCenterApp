import json
import hashlib

from sqlalchemy import func

from englishapp import app, db
from models import Capdo, Khoahoc, Lophoc, User

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
    u = User(name=name, username=username.strip(), password=password, avatar=avatar)
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

    print(query)

    return query.all()

if __name__ == '__main__':
    with app.app_context():
        print(count_khoahoc_by_capdo())

