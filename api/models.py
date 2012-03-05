# -*- coding: utf-8 -*-
from app import app

from flaskext.sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)


class Parliamentary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)

    def to_dict(self):
        cols = [col.name for col in self.__table__.columns]
        return {'parliamentary': dict(zip(cols, [getattr(self, col) for col in cols]))}
