from messenger_manager import MessengerManager
from bottle import Bottle, run

app = Bottle()


@app.route('/<request_text>')
def basic(request_text=None):
    greets = MessengerManager.greetings(request_text)
    if greets:
        return greets

    result = MessengerManager.make_request(request_text.lower(), 'WEB')
    if len(result.messages) == 1:
        return result.messages[0]
    else:
        message = ''
        for msg in result.messages:
            message += msg
        return message


run(app, host='localhost', port=8019, debug=True)

# TODO: POST-method
# TODO: JSON обмен данными
