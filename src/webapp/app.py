import logging
import sys

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import difflib
import pandas as pd
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from helpers import get_parties_states, query_rows
from helpers import PARTY_TYPES, PARTY_LIST
sys.path.append('./src')


# set up logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

app = dash.Dash(__name__)

# allow dynamic callbacks
app.config['suppress_callback_exceptions'] = True

# add external css
# css_url = 'https://codepen.io/chriddyp/pen/bWLwgP.css'
# app.css.append_css({"external_url": [css_url]})

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
                    html.H3("Vending Machine's Trustworthy Ledger"),
                    html.H5("Bills Reporting And Market Analysis"),
                ],
            ),
        ],
    )


def create_tab2():
    return html.Div(
        id="tab-2-content",
        className="row",
        children=[
            html.Div(
                className="col-xl-4",
                children=[
                    html.Div(
                        id="selector",
                        className="pretty_container",
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
                                    {"label": "Locations ", "value": "location"},
                                ],
                                value="operator",
                                labelStyle={
                                    'display': 'inline-block',
                                    'margin': '2px',
                                },
                            ),
                            dcc.Dropdown(
                                id="party_options",
                                options=party_options,
                                multi=False,
                                value='',
                            ),
                        ]
                    )                               
                ],
            ),
            html.Div(
                
                className="col-xl-8",
                children=[
                    html.Div(
                        id="main-content",
                        className="pretty_container",
                        children=[
                            html.Div(id='selector_output')
                        ]
                    )   
                ]
            )  
        ]
    )


# Layout
app.layout = html.Div(
    id="big-app-container",
    className="container-fluid",
    children=[
        build_banner(),
        dcc.Interval(
            id="interval-component",
            interval=3 * 1000,  # in milliseconds
            n_intervals=0,
        ),
        html.Div(
            id="app-container",
            className="container-fluid",
            children=[
                dcc.Tabs(
                    id="tabs", 
                    parent_className='custom-tabs',
                    className="custom-tabs-container",
                    value='tab-2', 
                    children=[
                        dcc.Tab(
                            label='1', 
                            value='tab-1', 
                            className='custom-tab',
                            selected_className='custom-tab--selected'
                        ),
                        dcc.Tab(
                            label='2', 
                            value='tab-2',
                            className='custom-tab',
                            selected_className='custom-tab--selected'
                        ),
                    ],
                    colors={
                        "border": "white",
                        "primary": "#4E6AF6",
                        "background": "#c4ccf5",
                    } 
                ),
                html.Div(id='app-content', className='app-content')
            ]
        )
    ]
)


# Create callback

@app.callback(Output('app-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3('Tab content 1')
        ])
    elif tab == 'tab-2':
        return create_tab2()

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
    logger.info(f"option's value is {value}")
    if value == "" or value == None:
        return 'Please choose the ledger you want to check'

    logger.info("updating df...")

    # wallet's state info
    df_account_states = pd.DataFrame(get_parties_states(PARTY_LIST))
    output = df_account_states[df_account_states['moniker'] == value]

    # txs info
    column = difflib.get_close_matches(value, ['operator', 'manufacturer', 'location', 'supplier'])[0]
    df_txs = query_rows(column, value).sort_values(by=['time'], ascending=False)
    shown_columns = ['item', 'price', 'time', 'vending_machine', 'hash']
    table = dash_table.DataTable(
                data=df_txs.to_dict('records'),
                columns=[{'id': c, 'name': c} for c in shown_columns],
                style_table={'overflowX': 'scroll'},
                style_cell={'textAlign': 'left', 'margin': '10px'},
                style_as_list_view=True,
                page_size= 20,
            )  

    
    layout = html.Div(
                children=[
                    html.Div(
                        className="row",
                        children=[
                            html.Div(
                                className='col', 
                                children=[
                                    html.H4(output['moniker']),
                                    html.P(f"Address: {output['address'].values[0]}"),
                                ],
                            ),
                            html.Div(
                                className='col',
                                children=[
                                    html.H4(output['balance'].values[0], style={'textAlign': 'right'}),
                                    html.H5("Balance", style={'textAlign': 'right'})
                                ]
                            ),
                        ]
                    ),
                    html.P(f"Number of bills: {output['num_txs'].values[0]}"),
                    table,
                ]
            )
            
    return layout


if __name__ == '__main__':
    app.run_server(debug=True)
