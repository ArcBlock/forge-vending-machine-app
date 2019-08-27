import logging
import sys

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import dash_table
import difflib
import pandas as pd
import plotly.figure_factory as ff
from dash.dependencies import Input
from dash.dependencies import Output
from dash.dependencies import State
from helpers import get_parties_states, query_rows, get_value_prop, heatmap_helper
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

# building components for tab1
def piechart():
    return dcc.Graph(
        id="piechart",
        figure={
            "data": [
                {
                    "labels": [],
                    "values": [],
                    "type": "pie",
                    "marker": {
                        "colors": ['rgb(146, 123, 21)',
                                  'rgb(177, 180, 34)',
                                  'rgb(206, 206, 40)',
                                  'rgb(175, 51, 21)',
                                  'rgb(35, 36, 21)'],
                        # "line": {"color": "white", "width": 3}
                    },
                    "textinfo": "label",
                }
            ],
            "layout": {
                "margin": dict(l=20, r=20, t=20, b=20),
                "showlegend": True,
                "paper_bgcolor": "rgba(0,0,0,0)",
                "plot_bgcolor": "rgba(0,0,0,0)",
                "autosize": True,
            },
        },
    )

def vm_map():
    y, text, z = heatmap_helper()
    colorscale = [[0, '#e8dd9b'], [1, 'rgb(79, 129, 102)']]
    return dcc.Graph(
        id='vm_map',
        figure=ff.create_annotated_heatmap(z, y=y, annotation_text=text, colorscale=colorscale)
    )

def create_tab1():
    return html.Div(
        id="tab-1-content",
        children=[
            piechart(),
            vm_map()
        ]
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
                        "primary": 'rgb(79, 129, 102)', #"#4E6AF6",
                        "background": '#9fb3a9', #"#c4ccf5",
                    } 
                ),
                html.Div(id='app-content', className='app-content')
            ]
        )
    ]
)


# Create callback

# Tab
@app.callback(Output('app-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return create_tab1()
    elif tab == 'tab-2':
        return create_tab2()

'''
Tab1 Callback
'''
# Piechart -> update
@app.callback(Output('piechart', 'figure'), [Input('interval-component', 'n_intervals')])
def update_piechart(n):
    prop_dict = get_value_prop('operator')
    return {
        "data": [{
            "labels":[*prop_dict],
            "values": [*prop_dict.values()],
            "type": "pie",
            "marker": {
                "colors": ['rgb(33, 75, 99)',
                            'rgb(79, 129, 102)',
                            'rgb(151, 179, 100)',
                            'rgb(175, 49, 35)',
                            'rgb(36, 73, 147)'], 
                #  "line": {"color": "white", "width":3}
            },
            # "hoverinfo": "label",
            "textinfo": "label",
            # "hole": 0.3,
        }],
        "layout": {
            "margin": dict(l=20, r=20, t=20, b=20),
            "showlegend": True,
            "paper_bgcolor": "rgba(0,0,0,0)",
            # "plot_bgcolor": "rgba(0,0,0,0)",
            # "font": {"color": "white"},
            "autosize": True,
        },
    }


# Heatmap -> update
@app.callback(Output('vm_map', 'figure'), [Input('interval-component', 'n_intervals')])
def update_map(n):
    y, a_text, z = heatmap_helper()

    hover = []
    for i in range(len(z)):
        y_elem = y[i]
        tmp = []
        for z_elem in z[i]:
            tmp.append("Operator: {} <br> Tx number: {}".format(y_elem, str(z_elem)))
        hover.append(tmp)

    colorscale = [[0, '#e8dd9b'], [1, 'rgb(79, 129, 102)']]
    fig = ff.create_annotated_heatmap(z, y=y, annotation_text=a_text, colorscale=colorscale, text=hover, 
                                        hoverinfo='text', connectgaps=True, showscale=True)
    return fig


'''
Tab2 Callback
'''
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
    logger.debug(f"option's value is {value}")
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
