from types import *
from xml.sax.saxutils import escape

def dict2xml(**kwargs):
    res = []

    def dict2xml_rec(d, lastTag=None):
        if type(d) is DictType:
            for key, value in d.iteritems():
                res.append("<%s>" % key)
                dict2xml_rec(value, key)
                res.append("</%s>" % key)
        if type(d) is ListType:
            if len(d):
                for v in d:
                    dict2xml_rec(v, 'list')
        if type(d) in StringTypes: 
            res.append(escape(d))
        if type(d) in (IntType, LongType, FloatType):
            res.append(escape(str(d)))


    dict2xml_rec(kwargs)
    return "".join(res)
