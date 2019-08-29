import logging
import sys
sys.path.append('./src')
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_daq as daq
import dash_html_components as html
import dash_table
import difflib
import operator
import pandas as pd
import plotly.figure_factory as ff
import plotly.graph_objects as go

from dash.dependencies import Input, Output, State
from datetime import date
from datetime import datetime as dt

from helpers import get_parties_states, get_db, get_distinct_value, query_rows, get_value_prop
from helpers import heatmap_helper, moniker_name_converter, get_wallet_address, get_column, get_value_prop_with_conditions
from helpers import PARTY_TYPES, PARTY_LIST
from utils.conf import share




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
    {"label": str(PARTY_TYPES[party]), "value": str(party)}
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
                "margin": dict(l=20, r=20, t=20, b=30),
                "showlegend": True,
                "paper_bgcolor": "#f9f9f9",
                "autosize": True,
            },
        },
    )


def vm_map():
    y, a_text, z = heatmap_helper()
    colorscale = [[0, '#e8dd9b'], [1, 'rgb(79, 129, 102)']]
    fig = ff.create_annotated_heatmap(z, y=y, annotation_text=a_text, colorscale=colorscale, hoverinfo='text', showscale=True)
    fig.update_layout(
        xaxis=dict(title='Vending Machines', showgrid=False, title_font=dict(color='rgb(33, 75, 99)', size=18), zeroline=False),
        yaxis=dict(title='Operators', title_font=dict(color='rgb(33, 75, 99)', size=18), zeroline=False),
        plot_bgcolor=('white'),
        paper_bgcolor="#f9f9f9",
        # margin=dict(l=20, r=20, t=20, b=30),
    )
                                        
    return dcc.Graph(
        id='vm_map',
        figure=fig,
    )


def geo_scatter():
    colors = ['rgb(33, 75, 99)','rgb(79, 129, 102)','rgb(151, 179, 100)','rgb(175, 49, 35)','rgb(36, 73, 147)']
    fig = go.Figure()
    distinct_op = get_distinct_value('operator')
    for i in range(len(distinct_op)):
        op = distinct_op[i][0]
        df = query_rows('operator', op)
        fig.add_trace(go.Scattergeo(
            locationmode = 'USA-states',
            lon = df['lo_lng'],
            lat = df['lo_lat'],
            text = "vending machine ID: " + df['vm_id'],
            marker = dict(
                color=colors[i],
                opacity=0.8,
                size=18,
                # sizemode = 'area'
            ),
            name = moniker_name_converter(op),
            hoverinfo='text+name'
        ))
    fig.update_layout(
        autosize=True,
        geo = dict(
            scope = 'usa',
            landcolor = '#e3e1cf',
        ),
        legend_orientation="h",
        margin = go.layout.Margin(l=10, r=10, t=10, b=10),
        showlegend = True,
    )
    return dcc.Graph(id='geo-scatter', figure=fig)


def create_tab1():
    return html.Div(
        id="tab-1-content",
        children=[
            html.Div(
                className="row",
                children=[
                    html.Div(
                        className="col-xl-4",
                        children=[
                            html.Div(
                                className="pretty_container_info",
                                children=[
                                    dcc.Markdown('''
                                    #### Welcome to the Vending Machine Market Analytics Dashboard  
                                    Stay up-to-date with the dynamic *Blockchain-backed* statistics of vending machines operators.
                                    >
                                    >  ** Exploration Tips **
                                    >  * Click on the legends of the `map` and the `pie chart` to toggle operators.
                                    >  * Click on the `heatmap` to see the 5 top selling items of the selected vending machine.
                                    >
                                    '''),
                                    html.Br(),
                                ]
                            )
                        ]
                    ),
                    html.Div(
                        className="col-xl-4",
                        children=[
                            html.Div(
                                className="pretty_container_fig",
                                children=[
                                    html.H4("Operator Distribution"),
                                    geo_scatter(),
                                ]
                            )
                        ]
                    ),
                    html.Div(
                        className="col-xl-4",
                        children=[
                            html.Div(
                                className="pretty_container_fig",
                                children=[
                                    html.H4("Market Share"),
                                    piechart(),
                                ]
                            )
                        ]
                    ),
                ]
            ),
            html.Div(
                className="row",
                children=[
                    html.Div(
                        className="col-xl-4",
                        children=[
                            html.Div(
                                id='item-table',
                                className="pretty_container_fig",
                            )
                        ]
                    ),
                    html.Div(
                        className="col-xl-8",
                        children=[
                            html.Div(
                                className="pretty_container_fig",
                                children=[
                                    html.H4("Sales Performance"),
                                    vm_map(),
                                ]
                            )
                        ]
                    ),
                ]
            )                       
        ]
    )


def date_picker():
    return dcc.DatePickerRange(
                id='date-picker-range',
                min_date_allowed=dt(2019, 8, 1),
                # max_date_allowed=dt(2017, 9, 19),
                initial_visible_month=dt(2019, 8, 1),
                # start_date=dt(2019, 8, 1),
                end_date=dt.now(),
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
                            html.P("Select party:", className="label"),
                            dcc.RadioItems(
                                id="party-selector",
                                options=[
                                    {"label": "All ", "value": "all"},
                                    {"label": "Operators", "value": "operator"},
                                    {"label": "Manufacturers ", "value": "manufacturer"},
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
                                id="party-options",
                                options=party_options,
                                multi=False,
                                value='',
                            ),
                            html.P("Select date range:", className="label"),
                            date_picker()
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
                            html.Div(id='selector_output'),
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
                    value='tab-2', 
                    children=[
                        dcc.Tab(
                            label='Market Analytics', 
                            value='tab-1', 
                        ),
                        dcc.Tab(
                            label='Ledger Platform', 
                            value='tab-2',
                        ),
                    ],
                    colors={
                        "border": "white",
                        "primary": 'rgb(79, 129, 102)', 
                        "background": '#9fb3a9',
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
    labels = []
    for k in [*prop_dict]:
        labels.append(moniker_name_converter(k))
    return {
            "data": [{
                "labels":labels,
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
                "textinfo": "label",
            }],
            "layout": {
                "margin": dict(l=30, r=30, t=30, b=10),
                "paper_bgcolor": "#f9f9f9",
                "autosize": True,
                "showlegend":True,
            },
        }


# Heatmap -> update
@app.callback(Output('vm_map', 'figure'), [Input('interval-component', 'n_intervals')])
def update_map(n):
    y, a_text, z = heatmap_helper()

    hover = []
    for i in range(len(y)):
        y_elem = y[i]
        z_elems = z[i]
        t_elems = a_text[i]
        tmp = []
        for z_elem, t_elem in zip(z_elems, t_elems):
            tmp.append("VM: {} <br>Operator: {} <br>Tx number: {}".format(str(t_elem), y_elem, str(z_elem)))
        hover.append(tmp)

    colorscale = [[0, '#e8dd9b'], [1, 'rgb(79, 129, 102)']]
    fig = ff.create_annotated_heatmap(z, y=y, annotation_text=a_text, colorscale=colorscale, text=hover, 
                                        hoverinfo='text', showscale=True)

    fig.update_layout(
        xaxis=dict(title='Vending Machines', showgrid=False, title_font=dict(color='rgb(33, 75, 99)', size=18), zeroline=False),
        yaxis=dict(title='Operators', title_font=dict(color='rgb(33, 75, 99)', size=18), zeroline=False),
        plot_bgcolor=('white'),
        paper_bgcolor="#f9f9f9",
        # margin=dict(l=20, r=20, t=20, b=30),
    )

    return fig


# DataTable(best sell) -> update, click 
@app.callback(Output('item-table', 'children'), [Input('vm_map', 'clickData'), Input('interval-component', 'n_intervals')])
def display_table(data, n):

    # if a vending machine is selected
    if data is not None:
        clean_data = data['points'][0]['text'].split(": ")[1]
        vm_id = clean_data.split(" <br>")[0]
        entities = sorted(get_value_prop_with_conditions('item', 'vm_id', vm_id).items(), key=operator.itemgetter(1), reverse=True)
        etype = 'select'

        # selected vending machine has no item sold yet
        if entities == []:
            entities = sorted(get_value_prop('item').items(), key=operator.itemgetter(1), reverse=True)
            etype = 'reselect'

    else: # no vending machine is selected
        entities = sorted(get_value_prop('item').items(), key=operator.itemgetter(1), reverse=True)
        etype = 'notselect'

    # clean up entities
    length = len(entities) 
    if length >= 5:
        rank = [1, 2, 3, 4, 5]
        entities = entities[:5]
    
    else:
        rank = list(range(1, length + 1))

    # generate table
    df_table = pd.DataFrame(entities, columns=['Item', 'Sales Volume'])    
    df_table['Ranking'] = rank
    column_order = ['Ranking', 'Item', 'Sales Volume']
    table = dash_table.DataTable(
                columns=[{'id': c, 'name': c} for c in column_order],
                data=df_table.to_dict('records'),
                style_as_list_view=True,
                style_cell= {'textAlign': 'center', 'padding': '10px', 'font-size': '15px'},
                style_cell_conditional=[{
                    'if': {'column_id': 'Item'},
                    'textAlign': 'left'    
                }],
                style_data = {'border': '5px #f9f9f9 solid'},
                style_data_conditional=[{
                    "if": {"row_index": 0},
                    'color': 'rgb(175, 49, 35)',
                    'font-size': '18px',
                    'fontWeight': 'bold',
                }],
                style_header= {"backgroundColor": 'rgb(79, 129, 102)', 'color': 'white'},
                style_table = {'border': '10px #f9f9f9 solid'}
            )  
    
    # generate layout
    if etype == 'select':
        info = html.P("For vending machine " + vm_id + ", operated by " + data['points'][0]['y'], 
            style={'padding-left':'30px', 'padding-top':'5px', 'color':'rgb(33, 75, 99)'})

    elif etype == 'reselect':
        info = html.P("Vending machine " + vm_id + ", operated by " + data['points'][0]['y'] + ", has not sold any item yet. Please click on another one.",
            style={'padding-left':'30px', 'padding-top':'5px','color':'rgb(175, 49, 35)'})

    elif etype == 'notselect':
        info = html.Br()

    children = [
        html.H4("5 Top Selling Items"),
        info,
        table,
    ]

    return children
'''
Tab2 Callback
'''
# Radio -> dropdown options
@app.callback(Output("party-options", "options"), [Input("party-selector", "value")])
def display_type(selector):
    if selector == "all":
        return party_options 
    return [party for party in party_options if selector in party['value']]


# Dropdown -> selector output
@app.callback(
    Output('selector_output', 'children'),
    [Input('party-options', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('interval-component', 'n_intervals')])
def update_output(value, start, end, n):
    logger.debug(f"option's value is {value}")
    if value == "" or value == None:
        return 'Please choose the ledger you want to view'

    logger.info("updating df...")

    # wallet's state info
    df_account_states = pd.DataFrame(get_parties_states(PARTY_LIST))
    output = df_account_states[df_account_states['moniker'] == value]
    party_name = moniker_name_converter(output['moniker'].values[0])

    # txs info
    ptype = difflib.get_close_matches(value, ['operator', 'manufacturer', 'location', 'supplier'])[0]
    addr_value = get_wallet_address(ptype, value)
    column = get_column(ptype)
    # get related txs by searching addresses
    df_txs = query_rows(column, addr_value).sort_values(by=['time'], ascending=False)

    # filter txs by time
    if start is None:
        df_txs = df_txs[df_txs['time'] <= end]
    else:
        start = start + " 00:00:00"
        end = end + " 23:59:59"
        df_txs = df_txs[(df_txs['time'] >= start) & (df_txs['time'] <= end)]

    df_txs.price = df_txs.price.astype(float)/(10**16)
    shown_columns = ['item', 'price', 'time', 'vm_id', 'hash']
    table = dash_table.DataTable(                
                columns=[{'id': c, 'name': c} for c in shown_columns], 
                data=df_txs.to_dict('records'),   
                page_size= 20,           
                style_as_list_view=True,
                 style_header={'fontWeight': 'bold'},
                style_cell={'textAlign': 'center', 'margin': '10px', 'minWidth':'80px'},
                style_cell_conditional=[
                    {'if': {'column_id': 'item'},
                    'textAlign': 'left'},
                ],
                style_table={'overflowX': 'scroll'},
                
            )  

    ratio = share[ptype]

    total_balance = float(output['balance'].values[0].item()/(10**16))
    total_share = '%.2f' % (total_balance * ratio)
    total_balance = '%.2f' % total_balance

    selected_balance = df_txs['price'].sum()
    selected_share = '%.2f' % (selected_balance * ratio)
    selected_balance = '%.2f' % selected_balance

    ratio = str(int(ratio * 100))
    selected_num = df_txs.shape[0]


    layout = html.Div(
                children=[
                    html.Div(
                        className="row",
                        children=[
                            html.Div(
                                className='col', 
                                children=[
                                    html.H4(party_name, style={'color':'rgb(79, 129, 102)', 'fontWeight':'bold', 'marginBottom':'12px'}),
                                    html.P(f"Address: {output['address'].values[0]}", style={'marginBottom':'5px'}),
                                    html.P(f"Ratio: {ratio}"),
                                ],
                            ),
                            html.Div(
                                className='col',
                                children=[
                                    html.H4(f"{total_share}/{total_balance}", style={'textAlign': 'right'}),
                                    html.H5("Total Profits/Turnover", style={'textAlign': 'right'}),
                                    html.P(f"Total number of bills: {output['num_txs'].values[0]}", style={'textAlign': 'right'}),
                                ]
                            ),
                        ]
                    ),
                    html.Div(
                        style={'textAlign': 'right'},
                        children=[
                            html.A("check hash on the chain", href='http://localhost:8211/node/explorer/txs', target="_blank",
                                style = {'backgroundColor': 'rgb(79, 129, 102)', 'borderRadius': '10px', 'color':'white', 'fontWeight': 'bold', 'padding':'10px'})
                        ]        
                    ),
                    html.Br(),
                    table,
                    html.P(f"number: {selected_num} ; turnover: {selected_balance}", style={'textAlign': 'right'}),
                ]
            )
            
    return layout


if __name__ == '__main__':
    app.run_server(debug=True)
