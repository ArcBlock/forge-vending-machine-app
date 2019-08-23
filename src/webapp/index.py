import json
import sys

import dash
import dash_html_components as html
import flask
from flask import Response
from utils import wallets
sys.path.append('./src')
print(sys.path)


server = flask.Flask(__name__)


@server.route('/api/get_states')
def get_states():
    addresses = [item['address'] for item in wallets.operators]

    return Response(json.dumps({'hello': 'world'}), content_type='application/json')


app = dash.Dash(
    __name__,
    server=server,
    routes_pathname_prefix='/'
)

# rpc

app.layout = html.Div("My Dash app")

if __name__ == '__main__':
    app.run_server(debug=True)
