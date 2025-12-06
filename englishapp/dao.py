import json

def load_capdo():
    with open("data/capdo.json", encoding="utf-8") as f:
         return json.load(f)

def load_khoahoc(q=None, capDo_id=None):
    with open("data/khoahoc.json", encoding="utf-8") as f:
        khoahoc = json.load(f)

        if q:
            #xử lý để không phân biệt hoa/thường
            q = q.lower()
            khoahoc = [k for k in khoahoc if q in k["tenKH"].lower()]

        if capDo_id:
            khoahoc = [k for k in khoahoc if k["capDo_id"].__eq__(int(capDo_id))]

        return khoahoc


def get_khoahoc_by_maKH(maKH):
    with open("data/khoahoc.json", encoding="utf-8") as f:
        khoahoc = json.load(f)

        for k in khoahoc:
            if k["maKH"].__eq__(maKH):
                return k

    return None

if __name__ == '__main__':
    print(get_khoahoc_by_maKH(1))

