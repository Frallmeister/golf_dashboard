import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table

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

def create_table(df, d=0):
    distance = 'total_distance' if d==0 else 'carry_distance'
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