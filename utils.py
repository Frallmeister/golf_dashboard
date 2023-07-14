import base64
import datetime
import io

import numpy as np
import pandas as pd
from dash import html, dash_table
from models import Shots

club_enum = {
    '1W': '1 Wood',
    '3W': '3 Wood',
    '4': '4 Iron',
    '5': '5 Iron',
    '6': '6 Iron',
    '7': '7 Iron',
    '8': '8 Iron',
    '9': '9 Iron',
    'P': 'P Wedge',
    '52': '52 Wedge',
    '56': '56 Wedge',
}


def get_db_pw():
    with open("/run/secrets/db-password", "r") as fp:
        db_pw = fp.read()
    return db_pw


def get_rolling_values(df, club, column='total_distance', window_size=20, stat='stddev'):
    """
    Return list with statistic over rolling value
    """
    roll = df.groupby('club').get_group(club)[column].dropna().rolling(window_size)
    if stat == 'stddev':
        vals = roll.std().dropna().to_list()
    elif stat == 'mean':
        vals = roll.mean().dropna().to_list()
    elif stat == 'median':
        vals = roll.median().dropna().to_list()
    else:
        return None

    date = df.groupby('club').get_group(club).loc[window_size+1:, 'date'].to_list()
    return (vals, roll, date)


def floor(val, n):
    return n*int(val/n)


def big_rainbow(n):
    return ['hsl('+str(h)+',60%'+',60%)' for h in np.linspace(0, 300, n)]


def small_rainbow(df, clubs):
    all_clubs = df.club.unique()
    n = len(all_clubs)
    all_colors = big_rainbow(n)
    colors = [all_colors[i] for i in range(n) if all_clubs[i] in clubs]
    return colors



def get_values(array, nvals):
    """
    Returns the last nvals values of array
    """
    if nvals == 'all':
        n = len(array)
    elif nvals == 'last100':
        n = min(len(array), 100)
    else:
        n = min(len(array), 50)

    return array[-n:]


def get_clubs(df):
    # Get an ordered list of clubs, excluding clubs with no data
    clubs = [club for club in club_enum.keys() if club in df.club.unique()]
    clubs.reverse()

    clubmin = df.carry_distance.min() - 10
    clubmax = df.total_distance.max() + 10
    return (clubs, clubmin, clubmax)


def longest_shot(df, d=0):

    distance = 'total_distance' if d==0 else 'carry_distance'

    series = df.groupby('club').describe()[distance]['max']
    club = series.idxmax()
    dist = int(series.max())
    return html.Div([
        html.H3(f"{club_enum[club]}"),
        html.H3(f"{dist} m"),
    ])

def most_shots(df):
    """
    Get which golf club that have most logged shots.
    Return the string: <club_enum> (<num>)
    """
    club = df.club.value_counts().idxmax()
    freq = df.club.value_counts().max()
    return html.Div([
        html.H3(club_enum[club]),
        html.H3(f"#{freq}")
    ])

def fewest_shots(df):
    """
    Get which golf club that have most logged shots.
    Return the string: <club_enum> (<num>)
    """
    club = df.club.value_counts().idxmin()
    freq = df.club.value_counts().min()
    return html.Div([
        html.H3(club_enum[club]),
        html.H3(f"#{freq}")
    ])

def biggest_var(df, d=0):
    """
    Get which clubs that has the greatest variance.
    d=0: Return variance of total_distance
    d=1: Return variance of carry_distance
    """

    distance = 'total_distance' if d==0 else 'carry_distance'

    std = df.groupby('club').describe()[distance]['std']
    club = std.idxmax()
    num = std.max()
    return html.Div([
        html.H3(club_enum[club]),
        html.H3(f"\u03C3 = {num:.2f}", style={'color': '#EA0600'})
    ])

def smallest_var(df, d=0):
    """
    Get which clubs that has the smallest variance.
    d=0: Return variance of total_distance
    d=1: Return variance of carry_distance
    """

    distance = 'total_distance' if d==0 else 'carry_distance'

    std = df.groupby('club').describe()[distance]['std']
    club = std.idxmin()
    num = std.min()

    return html.Div([
        html.H3(club_enum[club]),
        html.H3(f"\u03C3 = {num:.2f}", style={'color': '#0034B8'})
    ])

def create_table(df, distance='total_distance'):
    table_df = df.groupby('club').describe()[distance].reset_index().round(decimals=2)
    table_df = table_df.astype({'mean': int, '25%': int, '50%': int, '75%': int})

    return dash_table.DataTable(
        id = "stat-table",
        columns = [{'name': i.capitalize(), 'id': i, 'deletable': False} for i in table_df.columns],
        data = table_df.to_dict("records"),
        sort_action='native',
        style_cell = {'textAlign': 'center'},
        style_header = {
            'fontWeight': 'bold',
            'padding': '5px',
            'backgroundColor': '#444444',
            'color': '#ffffff'
            },
        style_as_list_view=True,
    )


def parse_file_upload(contents, filename, engine, session):

    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    # Only accept csv and xls files
    if filename.split('.')[-1] == 'csv':
        pass
    elif 'xls' in filename.split('.')[-1] and False:
        # Excel not supported yet
        pass
    else:
        return html.Div(
            "Only csv are accepted",
            className="upload-error-message",
            )

    # Check that the file have the expected columns
    list_content = decoded.decode('utf-8').split('\n')
    column_names = list_content[0].strip()
    expected_columns = ['club', 'total_distance', 'carry_distance', 'date']
    if not all([column in column_names for column in expected_columns]) or len(column_names.split(','))<4:
        print([column in column_names for column in expected_columns])
        print(column_names.split(','))
        return html.Div(
            f"The file did not have the expected columns",
            className="upload-error-message",
            )

    # Create table with data to display
    try:
        if filename.split('.')[-1] == 'csv':
            # Assume that the user uploaded a CSV file
            dff = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))

        elif 'xls' in filename.split('.')[-1]:
            # Assume that the user uploaded an excel file
            dff = pd.read_excel(io.BytesIO(decoded))

    except Exception as e:
        print(e)
        return html.Div(
            'There was an error processing this file',
            className="upload-error-message"
            )

    col_dict = dict(enumerate(column_names.split(',')))
    n_columns = len(column_names.split(','))
    for row in decoded.decode('utf-8').split('\n')[1:]:
        print(f"row = {row}")
        cells = row.strip().split(',')
        entry = {col_dict[i]:cells[i] for i in range(n_columns)}

        # Create new record
        new_shot = Shots(
            club = str(entry['club']),
            total_distance = int(float(entry['total_distance'])) if entry['total_distance'] else None,
            carry_distance = int(float(entry['carry_distance'])) if entry['carry_distance'] else None,
            missed = bool(int(entry['missed'])) if entry['missed'] else None,
            date = datetime.datetime.strptime(entry['date'], '%Y-%m-%d'),
            ball_speed = int(float(entry['ball_speed'])) if entry['ball_speed'] else None,
            launch_angle = int(float(entry['launch_angle'])) if entry['launch_angle'] else None,
            height = int(float(entry['height'])) if entry['height'] else None,
            impact_angle = int(float(entry['impact_angle'])) if entry['impact_angle'] else None,
            hang_time = float(entry['hang_time']) if entry['hang_time'] else None,
            curve = int(float(entry['curve'])) if entry['curve'] else None,
            side = int(float(entry['side'])) if entry['side'] else None,
        )
        session.add(new_shot)
    session.commit()


    return html.Div(className="table card", children=[
        html.H2(
        className = "upload-success-message",
        children = ["The following data was saved"],
        ),
        dash_table.DataTable(
            id="upload_table_id",
            data = dff.to_dict('records'),
            columns = [{'name': i.capitalize().replace('_', ' '), 'id': i, 'deletable': False} for i in dff.columns],
            sort_action='native',
            style_cell = {'textAlign': 'center'},
            style_header = {
                'textAlign': 'center',
                'fontWeight': 'bold',
                'padding': '5px',
                'backgroundColor': '#444444',
                'color': '#ffffff'
                },
            style_as_list_view=True,
        )
    ])


def get_cov(df, club):
    dff = df.groupby('club').get_group(club)[['total_distance', 'side']].dropna()
    return dff.cov()


def f_norm(M):
    """
    Return Frobenius norm of matrix m
    """
    m, n = np.shape(M)
    M = np.reshape(M, m*n)
    return np.sqrt(np.sum(M**2))


def get_ellipse(df, club, nvals=None, xcol='total_distance', ycol='side', p=0.95):
    dff = df.groupby('club').get_group(club)[['total_distance', 'side']].dropna()

    if nvals is None:
        nvals = dff.side.count()
    elif isinstance(nvals, int):
        nvals = min(nvals, dff.side.count())
    else:
        nvals = dff.side.count()

    # Scatter data
    y = dff[ycol].to_numpy()[-nvals:]
    x = dff[xcol].to_numpy()[-nvals:]
    x_mean, y_mean = x.mean(), y.mean()

    # Covariance, eigenvalues, eigenvectors
    cov = dff.cov().to_numpy()
    w, v = np.linalg.eigh(cov)

    # Calculate Chi square value
    s = -2*np.log(1-p)

    # Get ellipse points
    t = np.linspace(0, 2*np.pi)
    X = np.sqrt(w[1]*s)*np.cos(t)
    Y = np.sqrt(w[0]*s)*np.sin(t)

    # Rotation matrix
    theta = np.arctan(v[w.argmax(), 1] / v[w.argmax(), 0])
    R = np.array([
        [np.cos(theta), -np.sin(theta)],
        [np.sin(theta), np.cos(theta)]
    ])

    # Rotate elipse data
    X_rot, Y_rot = [], []
    for X_, Y_ in zip(X,Y):
        x_temp, y_temp = np.dot(R, np.array([X_,Y_]))
        X_rot.append(x_temp+x_mean)
        Y_rot.append(y_temp+y_mean)

    return (X_rot, Y_rot, x, y)
