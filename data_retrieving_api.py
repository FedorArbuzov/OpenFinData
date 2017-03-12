from data_retrieving import DataRetrieving
from bottle import Bottle, get, post, request, run

app = Bottle()


@app.get('/<request_text>')
def get_basic(request_text=None):
    request_text = request_text.lower().strip()
    if request_text:
        result = DataRetrieving.get_data(request_text)
        return result.toJSON()


run(app, host='localhost', port=8019, debug=True)
