import datetime

from app.main import db


def check_object_with_json(object, json):
    for key in json.keys():
        try:
            attr = getattr(object, key)
        except Exception:
            attr = getattr(object, key[:-4])
            if isinstance(attr, list) and isinstance(json.get(key), list):
                for item in attr:
                    assert item.id in json.get(key)
            return
        if isinstance(attr, db.Model):
            check_object_with_json(object=attr, json=json.get(key))
        elif isinstance(attr, list) and isinstance(json.get(key), list):
            for i, item in enumerate(attr):
                if isinstance(attr[i], db.Model):
                    check_object_with_json(object=item, json=json.get(key)[i])
        else:
            assert attr == json.get(key)
