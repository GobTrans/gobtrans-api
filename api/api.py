#!/usr/bin/env python
import os

from flask import Flask, jsonify
from flask.views import MethodView
from mimerender_flask import mimerender

from models import Parliamentary, init_db
from lib.xmlutils import dict2xml

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'api.db')
app.debug=True

db = init_db(app)

class ParliamentariesAPI(MethodView):
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
        print dir(p)
        db.session.add(p)
        db.session.commit()
        return "OK"

parliamentaries_view = ParliamentariesAPI.as_view('parliamentaries_api')
app.add_url_rule('/parliamentaries/', defaults={'id': None}, view_func=parliamentaries_view, methods=['GET'])
app.add_url_rule('/parliamentaries/<int:id>/', view_func=parliamentaries_view, methods=['GET'])
app.add_url_rule('/parliamentaries/<int:id>/<name>', view_func=parliamentaries_view, methods=['POST'])

if __name__ == '__main__':
    app.run()
