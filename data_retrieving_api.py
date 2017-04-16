from data_retrieving import DataRetrieving
from bottle import Bottle, get, post, request, run
import codecs

app = Bottle()


@app.get('/<request_text>')
def get_basic(request_text=None):
    print(request_text)
    request_text = request_text.strip()

    print(request_text.encode('iso-8859-1').decode('utf-8'))
    #request_text=request_text.encode('iso-8859-1').decode('utf-8')

    request_text = codecs.decode(bytes(request_text, 'iso-8859-1'), 'utf-8')

    print(request_text)

    if request_text:
        result = DataRetrieving.get_data(request_text)
        result_string = 'CNTK: ',result.cntk_response,', Solr Result: ',result.response

        return result_string


run(app, host='localhost', port=8019, debug=True)
