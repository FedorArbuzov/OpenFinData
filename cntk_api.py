# -*- coding: utf-8 -*-
"""
Created on Sat Apr  8 23:51:02 2017

@author: imon
"""

from botn import text_to_tags
from bottle import Bottle, request, run
import codecs
from urllib3 import util

app = Bottle()


@app.get('/<request_text>')
def get_basic(request_text=None):
    request_text = request_text.strip()
    print(request_text)
    
    print(util.parse_url(request_text))
    #request_text = codecs.decode(bytes(request_text, 'URL-encoding'), 'utf-8')
    if request_text:
        result = text_to_tags(request_text)
        return result


run(app, host='localhost', port=8020, debug=True)
