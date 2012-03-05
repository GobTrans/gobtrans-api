#!/usr/bin/env python
# -*- coding: utf-8 -*-
from app import app
from models import Parliamentary, db

from flask import jsonify
from flask.views import MethodView
from flaskmimerender import mimerender
from lib.xmlutils import dict2xml


class ParliamentariesAPI(MethodView):
    @mimerender(default='json',
                json=jsonify,
                xml=dict2xml,
    )
    def get(self, **kwargs):
        return {'parliamentaries': map(Parliamentary.to_dict,
                                       Parliamentary.query.filter_by(**kwargs).all())}

#    def put(self, id, name):
#        p = Parliamentary(id=id, name=name)
#        db.session.add(p)
#        db.session.commit()
#        return "OK"
#
#    def post(self, name):
#        p = Parliamentary(name=name)
#        db.session.add(p)
#        db.session.commit()
#        return str(p.id)


if __name__ == '__main__':
    app.run()
