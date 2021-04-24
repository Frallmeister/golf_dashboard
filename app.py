import os
import datetime

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

import sqlalchemy as db
from models import Shots

db_pw = os.environ.get('MYSQLPW')
db_uri = f"mysql+pymysql://root:{db_pw}@localhost:3306/golf_progress"
engine = db.create_engine(db_uri, echo=True)

Session = db.orm.sessionmaker(bind=engine)
session = Session()

# Instantiate Dash app
app = dash.Dash(__name__)

app.layout = html.Div(
    html.H1('Hello world')
)

if __name__ == '__main__':
    app.run_server(debug=True)
