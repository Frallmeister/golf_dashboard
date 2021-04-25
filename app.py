import os
import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd

import sqlalchemy as db
from models import Shots

from utils import *

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
                html.Li([html.P("Page1")]),
                html.Li([html.P("Page2")]),
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

    html.Div(className="container grid grid-6", children=[
        html.Div(className="dist-plots card", children=[
            html.H3("Length distribution"),
            html.P("Some graph here")
        ])
    ])


])


if __name__ == '__main__':
    app.run_server(debug=True)