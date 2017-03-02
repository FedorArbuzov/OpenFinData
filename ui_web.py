from messenger_manager import MessengerManager
from bottle import Bottle, get, post, request, run
import codecs

app = Bottle()


@app.get('/')
def main():
    return '<center><h1>Welcome to Datatron Home API page</h1></center>'


@app.get('/get/<request_text>')
def get_basic(request_text=None):
    request_text = request_text.lower().strip()
    if request_text:
        greets = MessengerManager.greetings(request_text)
        if greets:
            return greets

        result = MessengerManager.make_request(request_text.lower(), 'WEB')
        return result.toJSON()


@app.post('/post')
def post_basic():
    req = request.forms.get('request')
    # Исправлена кодировка для POST-запросов
    req = codecs.decode(bytes(req, 'iso-8859-1'), 'utf-8')
    if req:
        return MessengerManager.make_request(req.lower(), 'WEB').toJSON()


@app.error(404)
def error404(error):
    return '<center><h1>Nothing here sorry: %s</h1></center>' % error


run(app, host='localhost', port=8019, debug=True)
