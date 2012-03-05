# -*- coding: utf-8 -*-
from api import ParliamentariesAPI
from app import app


parliamentaries_view = ParliamentariesAPI.as_view('parliamentaries_api')

app.add_url_rule('/parliamentaries/',
                 view_func=parliamentaries_view, methods=['GET'])
app.add_url_rule('/parliamentaries/<int:id>/', view_func=parliamentaries_view,
                 methods=['GET'])
app.add_url_rule('/parliamentaries/<name>/', view_func=parliamentaries_view,
                 methods=['GET'])
#app.add_url_rule('/parliamentaries/<name>/', view_func=parliamentaries_view,
#                 methods=['GET', 'POST'])
#app.add_url_rule('/parliamentaries/<int:id>/<name>/',
#                 view_func=parliamentaries_view, methods=['PUT'])
