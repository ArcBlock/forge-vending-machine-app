import logging
import sys

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from helpers import get_parties_states
from helpers import PARTY_TYPES, PARTY_LIST
sys.path.append('./src')


# set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

app = dash.Dash(__name__)

css_url = 'https://codepen.io/chriddyp/pen/bWLwgP.css'
app.css.append_css({"external_url": css_url})

df_account_states = pd.DataFrame(get_parties_states(PARTY_LIST))
logger.debug(f"\n {df_account_states}")

df_txs = pd.DataFrame

party_options = [
    {"label": str(party), "value": str(PARTY_TYPES[party])}
    for party in PARTY_TYPES
]
logger.debug(party_options)


def build_banner():
    return html.Div(
        id="banner",
        className="banner",
        children=[
            html.Div(
                id="banner-text",
                children=[
                    html.H5("Vending Machine's Trustworthy Ledger"),
                    html.H6("Bills Reporting And Market Analysis"),
                ],
            ),
        ],
    )


# Layout
app.layout = html.Div(
    id="big-app-container",
    children=[
        build_banner(),
        dcc.Interval(
            id="interval-component",
            interval=3 * 1000,  # in milliseconds
            n_intervals=0,
        ),
        html.Div(
            id="app-container",
            children=[
                # Main app
                html.Div(
                    id="app-content",
                    children=[
                        html.P("Filter by party:", className="control_label"),
                        dcc.RadioItems(
                            id="party_selector",
                            options=[
                                {"label": "All ", "value": "all"},
                                {"label": "Operators", "value": "operator"},
                                {"label": "Manufacturers ",
                                    "value": "manufacturer"},
                                {"label": "Suppliers ", "value": "supplier"},
                                {"label": "Proprietors ", "value": "location"},
                            ],
                            value="operator",
                            labelStyle={"display": "inline-block"},
                            className="form-check",
                        ),
                        dcc.Dropdown(
                            id="party_options",
                            options=party_options,
                            multi=False,
                            value='',
                            className="dropdown",
                        ),
                        html.Div(id='selector_output')
                    ]),
            ],
        ),
    ],
)

# Create callback

# Radio -> dropdown options
@app.callback(Output("party_options", "options"), [Input("party_selector", "value")])
def display_type(selector):
    if selector == "all":
        return party_options
    return [party for party in party_options if selector in party['value']]


# Dropdown -> selector output
@app.callback(
    Output('selector_output', 'children'),
    [Input('party_options', 'value'),
     Input('interval-component', 'n_intervals')])
def update_output(value, n):
    if value == "":
        return 'Please choose the ledger you want to check'

    logger.info("updating df...")
    df_account_states = pd.DataFrame(get_parties_states(PARTY_LIST))
    output = df_account_states[df_account_states['moniker'] == value]
    return html.Div(
        children=(
            html.H5(output['moniker']),
            html.P(f"Address: {output['address'].values[0]}"),
            html.P(f"Balance: {output['balance'].values[0]}"),
            html.P(f"Number of TXs: {output['num_txs'].values[0]}"),
        )
    )


if __name__ == '__main__':
    app.run_server(debug=True)
