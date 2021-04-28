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
app = dash.Dash(__name__)
app.title = "My Golf Progress"

app.layout = html.Div(children=[

    ###### NAVBAR
    html.Div(className="navbar flex", children=[
        html.Div(className="start", children=[
            html.Div(className="flex", children=[
                html.Img(src=app.get_asset_url('dash-logo.jpeg'), height='50px'),
            ])
        ]),
        html.Div(className="nav-header", children=[html.H1("My Golf Progress")]),       
        html.Nav(className="navitems", children=[
            html.Ul(className="flex", children=[
                html.Li([html.P("Club details")]),
                html.Li([html.P("Log shots")]),
                html.Li([html.P("Page3")]),
            ])
        ])
    ]),

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
            html.Div(className="left-top", children=[
                html.Div(className="controls card", children=[
                    
                    html.H3("Controls"),
                    # Mean/Median
                    html.Div(className="radio-group", children=[
                        dcc.RadioItems(
                            id='radio-mean-median',
                            options=[
                                {'label': 'Median', 'value': 'median'},
                                {'label': 'Mean', 'value': 'mean'},
                            ],
                            value='median',
                            labelStyle={'display': 'inline-block'}
                        ) 
                    ]),
                    # Mean/Median
                    html.Div(className="radio-group", children=[
                        dcc.RadioItems(
                            id='radio-total-carry',
                            options=[
                                {'label': 'Total distance', 'value': 'total'},
                                {'label': 'Carry distance', 'value': 'carry'},
                            ],
                            value='total',
                            labelStyle={'display': 'inline-block'}
                        ) 
                    ]),
                ]),
                html.Div(className="table card", children=[
                    html.H3("Statistics"),
                    html.Div(create_table(df))
                ]),
            ]),
            html.Div(className="dist-plots card", children=[
                html.H3("Length distribution"),
                html.Div(id="dist-plot"),
                dcc.RangeSlider(
                    id='dist-plot-range',
                    marks={i: f"{i} m" for i in range(min(0, int(df.carry_distance.min()-20)), int(df.total_distance.max()+60), 50)},
                    value=[max(0, int(df.carry_distance.min()-10)), int(df.total_distance.max()+10)],
                    step=10,
                    min=0,
                    max=df.total_distance.max()+20,
                ),
                html.Div(className="flex dist-plot-bottom", children=[
                    html.Div(id="slider-range-text"),
                    html.Div(
                        dcc.Checklist(
                            id="show-bars-option",
                            options=[{"label": "Show bars", "value": 'show'}],
                            value=[]
                        )
                    ),
                ])

            ])
        ]),
    ])
])



""" Callback functions below """
@app.callback(
    Output('dist-plot', 'children'),
    Input('radio-total-carry', 'value'),
    Input('dist-plot-range', 'value'),
    Input('show-bars-option', 'value'))
def plot_distribution(distance, range, show):
    show_hist = True if show else False
    fig = my_dist_plot(df, distance=distance, range=range, show_hist=show_hist)
    return dcc.Graph(figure=fig)

@app.callback(
    Output('slider-range-text', 'children'),
    Input('dist-plot-range', 'value'))
def output_dummy(val):
    a, b = val
    return f"Showing range {a} - {b} m"




if __name__ == '__main__':
    app.run_server(debug=True)