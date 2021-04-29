import os
import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd

import sqlalchemy as db
from models import Shots

from utils import *
from graphs import *

db_pw = os.environ.get('MYSQLPW')
db_uri = f"mysql+pymysql://root:{db_pw}@localhost:3306/golf_progress"
engine = db.create_engine(db_uri, echo=True)

Session = db.orm.sessionmaker(bind=engine)
session = Session()

df = pd.read_sql_table(
    'shots',
    engine,
    index_col='id',
    parse_dates=['date'])


# Instantiate Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
app.title = "My Golf Progress"

app.layout = html.Div(children=[
    dcc.Location(id='url', refresh=False),

    ###### NAVBAR
    html.Div(className="navbar flex", children=[
        html.Div(className="start", children=[
            html.Div(className="flex", children=[
                html.Img(src=app.get_asset_url('dash-logo.jpeg'), height='50px'),
            ])
        ]),
        html.Div(className="nav-header", children=[
            html.A(href="/", children=[
                html.H1("My Golf Progress")
            ])
        ]),
        html.Nav(className="navitems", children=[
            html.Ul(className="flex", children=[
                html.Li([dcc.Link("Home", id="home_id", href="/")]),
                html.Li([dcc.Link("Club details", id="club_details_id", href="/club-details")]),
                html.Li([dcc.Link("Data", id="data_id", href="/data")]),
            ])
        ])
    ]),

    html.Div(id="page-content")
])

# LAYOUT: Home
home_layout = html.Div([
    ###### HEADER
    html.Div(className="container", children=[
        html.Div(className="grid grid-6 header", children=[
            html.Div(className="card", children=[
                html.P("Total shots"),
                html.H1(f"{len(df)}"),
            ]),
            html.Div(className="card", children=[
                html.P("Longest shot"),
                longest_shot(df),
            ]),
            html.Div(className="card", children=[
                html.P("Most shots with"),
                most_shots(df),
            ]),
            html.Div(className="card", children=[
                html.P("Fewest shots with"),
                fewest_shots(df),
            ]),
            html.Div(className="card", children=[
                html.P("Biggest variance"),
                biggest_var(df, d=0),
            ]),
            html.Div(className="card", children=[
                html.P("Smallest variance"),
                smallest_var(df),
            ]),
        ])
    ]),

    ###### MAIN
    html.Div(className="container main", children=[
        html.Div(className="grid grid-6", children=[
            html.Div(className="stat-table", children=[
                # Table
                html.Div(className="table card", children=[
                    html.H3("Statistics"),
                    html.Div(id="table_id"),
                    dcc.RadioItems(
                        id="table-total-carry",
                        options=[
                            {'label': 'Total distance', 'value': 'total'},
                            {'label': 'Carry distance', 'value': 'carry'},
                        ],
                        value='total',
                        labelStyle={'display': 'inline-block'}
                    )
                ]),
            ]),
            # DIST PLOT
            html.Div(className="dist-plots card", children=[
                html.H3("Length distribution"),
                html.Div(id="dist-plot"), # <--- Plot div
                dcc.RangeSlider(
                    id='dist-plot-range',
                    step=10,
                    min=0,
                ),
                # Options below plot
                html.Div(className="flex dist-plot-bottom", children=[
                    html.Div(id="slider-range-text"),
                    html.Div(
                        dcc.Checklist(
                            id="show-bars-option",
                            options=[{"label": "Show bars", "value": 'show'}],
                            value=[]
                        )
                    ),
                    html.Div(
                        dcc.RadioItems(
                            id='dist-total-carry-option',
                            options=[
                                {'label': 'Total distance', 'value': 'total'},
                                {'label': 'Carry distance', 'value': 'carry'},
                            ],
                            value='total',
                            labelStyle={'display': 'block'}
                        ) 
                    )
                ])

            ])
        ]),
    ])
])


# LAYOUT: Data
data_layout = html.Div([
    html.H3("Data page")
])


# LAYOUT: Club details
details_layout = html.Div([
    html.H3("Club details")
    # Tabs and stuff here
])



""" Callback functions below """
@app.callback(
    Output('table_id', 'children'),
    Input('table-total-carry', 'value'))
def table_component(distance):
    distance += "_distance"
    table = create_table(df, distance=distance)
    return table

@app.callback(
    Output('dist-plot', 'children'),
    Input('dist-total-carry-option', 'value'),
    Input('dist-plot-range', 'value'),
    Input('show-bars-option', 'value'))
def plot_distribution(distance, range, show):
    """
    Plot the distribution plot in the upper right part of the dashboard.
    """
    show_hist = True if show else False
    fig = my_dist_plot(df, range=range, distance=distance, show_hist=show_hist)
    return dcc.Graph(figure=fig)


@app.callback(
    Output('dist-plot-range', 'marks'),
    Output('dist-plot-range', 'value'),
    Output('dist-plot-range', 'max'),
    Input('dist-total-carry-option', 'value'))
def slider_config(distance):
    """
    """
    dff = df[['total_distance', 'carry_distance']].describe()
    min_ = dff.loc['min',:].min()
    max_ = dff.loc['max',:].max()
    marks = {i: f"{i} m" for i in range(0, 25*int(max_/25) + 26, 25)}
    value = [max(0, int(min_ - 10)), int(max_ + 10)]
    max_ = 25*int(max_/25)+25
    return marks, value, max_

@app.callback(
    Output('slider-range-text', 'children'),
    Input('dist-plot-range', 'value'))
def print_range(val):
    """
    """
    a, b = val
    return f"Selected range {a}-{b} m"


""" Helper functions """
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname'))
def display_page(pathname):
    if pathname == "/":
        return home_layout
    elif pathname == "/home":
        return home_layout
    elif pathname == "/data":
        return data_layout
    elif pathname == "/club-details":
        return details_layout


if __name__ == '__main__':
    app.run_server(debug=True)