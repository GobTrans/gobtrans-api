#!/usr/bin/env python
from flask import Flask, jsonify
from flask.views import MethodView
from flaskext.sqlalchemy import SQLAlchemy
from mimerender_flask import mimerender

from lib.xmlutils import dict2xml

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/aa/hijosdeobdulio/gobtrans-api/api/api.db'
app.debug=True
db = SQLAlchemy(app)

class Parliamentary(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), index=True)

    def to_dict(self):
        cols = [ col.name for col in self.__table__.columns ]
        return {'parliamentary':dict(zip(cols, [ getattr(self, col) for col in cols ]))}

class ParliamentariesAPI(MethodView):
    def toxml(parliamentaries):
        res = ["<parliamentaries>"]
        for p in parliamentaries:
            res.append("<parliamentary><id>%d</id><name>%s</name></parliamentary>" % (p['id'], p['name']))
        res.append('</parliamentaries>')
        return "".join(res)

    @mimerender(
        default='json',
        json=jsonify,
        xml=dict2xml,
    )
    def get(self, id=None):
        if id is None:
            return {'parliamentaries': map(Parliamentary.to_dict, Parliamentary.query.all())}
        return {'parliamentaries': map(Parliamentary.to_dict, Parliamentary.query.filter_by(id=id).all())}

    def post(self, id, name):
        p = Parliamentary(id=id, name=name)
        db.session.add(p)
        db.session.commit()
        return "OK"

parliamentaries_view = ParliamentariesAPI.as_view('parliamentaries_api')
app.add_url_rule('/parliamentaries/', defaults={'id': None}, view_func=parliamentaries_view, methods=['GET'])
app.add_url_rule('/parliamentaries/<int:id>/', view_func=parliamentaries_view, methods=['GET'])
app.add_url_rule('/parliamentaries/<int:id>/<name>', view_func=parliamentaries_view, methods=['POST'])

if __name__ == '__main__':
    app.run()
