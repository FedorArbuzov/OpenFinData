from messenger_manager import MessengerManager
from bottle import Bottle, request, run
import codecs

app = Bottle()


@app.get('/')
def main():
    return '<center><h1>Welcome to Datatron Home API page</h1></center>'


@app.post('/post')
def post_basic():
    # Получение полей
    request_text = request.forms.get('Request')
    source = request.forms.get('Source')
    user_id = request.forms.get('UserId')
    user_name = request.forms.get('UserName')
    request_id = request.forms.get('RequestId')

    # Исправление кодировки
    request_text = codecs.decode(bytes(request_text, 'iso-8859-1'), 'utf-8')
    source = codecs.decode(bytes(source, 'iso-8859-1'), 'utf-8')
    user_id = codecs.decode(bytes(user_id, 'iso-8859-1'), 'utf-8')
    user_name = codecs.decode(bytes(user_name, 'iso-8859-1'), 'utf-8')
    request_id = codecs.decode(bytes(request_id, 'iso-8859-1'), 'utf-8')

    # если все поля заполнены
    if request_text and source and user_id and user_name and request_id:
        return MessengerManager.make_request(request_text, source, user_id, user_name, request_id).toJSON()


@app.error(404)
def error404(error):
    return '<center><h1>Nothing here sorry: %s</h1></center>' % error


run(app, host='0.0.0.0', port=8019, debug=True)
