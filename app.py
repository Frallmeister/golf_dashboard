import datetime

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import sqlalchemy as db

from models import Shots
from utils import *
from graphs import *

#db_pw = os.environ.get("MYSQL_ROOT_PASSWORD")
db_pw = get_db_pw()
db_uri = f"mysql+pymysql://root:{db_pw}@database:3306/golf_progress"

engine = db.create_engine(db_uri, echo=True)

Session = db.orm.sessionmaker(bind=engine)
session = Session()

df = pd.read_sql_table(
    'shots',
    engine,
    index_col='id',
    parse_dates=['date'])

def update_df(engine):
    global df
    df = pd.read_sql_table(
        'shots',
        engine,
        index_col='id',
        parse_dates=['date'])

# Instantiate Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

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

            # CONFIDENCE REGIONS
            html.Div(className="regions card", children=[
                html.H3("Confidence regions"),
                dcc.Graph(id="region_graph_id", figure=plot_conf_ellipse(df)),
                html.Div(className="flex", children=[
                    dcc.Checklist(
                        id="show-scatter-option",
                        options=[{"label": "Show data", "value": 'show'}],
                        value=[]
                    ),
                    html.Div(className="club-options", children=[
                        dcc.Checklist(
                            id="region_clubs_options",
                            options=[
                                {"label": utils.club_enum[club], "value": club} for club in df.loc[~df.side.isna(), 'club'].unique()
                                ],
                            value=list(df.loc[~df.side.isna(), 'club'].unique()),
                        ),
                    ])
                ]),
                html.Div(className="nvals", children=[
                    html.Div(className="flex", children=[
                        dcc.RadioItems(
                            id="region_nvals_options",
                            options=[
                                {"label": "All", "value": 0},
                                {"label": "Last 100", "value": 100},
                                {"label": "Last 50", "value": 50},
                                {"label": "Last 20", "value": 20},
                                ],
                            value=0,
                            labelStyle={'display': 'inline-block'},
                        ),
                    ])
                ]),
            ]),

            # Table
            html.Div(className="stat-table", children=[
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
                        labelStyle={'display': 'block'}
                    )
                ]),
            ]),
            
            # BOX PLOT
            html.Div(className="box-plot card", children=[
                html.H3("Box plot"),
                dcc.Graph(id="box-plot-graph"),
                html.Div(className="boxplot-options flex", children=[
                    dcc.RadioItems(
                        id='box_radio_distance_id',
                        options=[
                            {'label': 'Total distance', 'value': 'total_distance'},
                            {'label': 'Carry distance', 'value': 'carry_distance'},
                        ],
                        value='total_distance',
                        labelStyle={'display': 'block'}
                    ),
                    dcc.RadioItems(
                        id='box_radio_axis_id',
                        options=[
                            {'label': 'Distance on x-axis', 'value': 'xaxis'},
                            {'label': 'Distance on y-axis', 'value': 'yaxis'},
                        ],
                        value='xaxis',
                        labelStyle={'display': 'block'}
                    ),
                    dcc.RadioItems(
                        id='box_radio_nvals_id',
                        options=[
                            {'label': 'All shots', 'value': 'all'},
                            {'label': 'Last 100 shots', 'value': 'last100'},
                            {'label': 'Last 50 shots', 'value': 'last50'},
                        ],
                        value='all',
                        labelStyle={'display': 'block'}
                    ),
                ]),
            ]),
            
            # RIDGE PLOT
            html.Div(className="ridge-plot card", children=[
                html.H3("Ridge plot"),
                dcc.Graph(id="ridgeplot-graph"),
                html.Div(className="ridgeplot-options flex", children=[
                    dcc.RadioItems(
                        id='ridge_radio_distance_id',
                        options=[
                            {'label': 'Total distance', 'value': 'total_distance'},
                            {'label': 'Carry distance', 'value': 'carry_distance'},
                        ],
                        value='total_distance',
                        labelStyle={'display': 'block'}
                    ),
                    dcc.RadioItems(
                        id='ridge_radio_nvals_id',
                        options=[
                            {'label': 'All shots', 'value': 'all'},
                            {'label': 'Last 100 shots', 'value': 'last100'},
                            {'label': 'Last 50 shots', 'value': 'last50'},
                        ],
                        value='all',
                        labelStyle={'display': 'block'}
                    ),
                ]),
            ]),
            
            # HEATMAP
            html.Div(className="heatplot card", children=[
                html.H3("Heatmap"),
                dcc.Graph(id="heatplot-graph"),
                html.Div([
                    dcc.RadioItems(
                        id='heat-data-option',
                        options=[
                            {'label': 'Std. Dev', 'value': 'stddev'},
                            {'label': 'Median', 'value': 'median'},
                            {'label': 'Mean', 'value': 'mean'},
                        ],
                        value='stddev',
                        labelStyle={'display': 'block'}
                    ),
                    dcc.Slider(
                        id="heat-slider",
                        min=1,
                        max=df.groupby('club').count().total_distance.max(),
                        marks={i: str(i) for i in range(0, 101, 5)},
                        value=20,
                        step=None,
                    ),
                ])
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
                ]),
            ]),
        ]),
    ]),
])


# LAYOUT: Data
data_layout = html.Div([
    html.Div(className="data-container", children=[

        # HEADER CARD
        html.Div(className="upload-head", children=[
            html.Div(className="card", children=[
                html.H1("Save New Shots"),
                html.Div(id="upload-head-text", children=[
                    html.P("New golf shot data can be saved below, either by inputing them one at a time or by uploading a file with multiple shots."),
                    html.P("Press the download button to get a spreadsheet for logging shots in.")
                ]),

                # Download button
                html.Div(className="flex", children=[
                    html.Button("Download PDF", id="download_btn_id", className="btn"),
                    dcc.Download(id='download_id'),
                    html.Button("Refresh Data", id="refresh_btn_id", className="btn"),
                ])
            ])
        ]),

        html.Div(className="data-upload grid grid-2", children=[
        
            # UPLOAD BOX
            html.Div(className="upload-box", children=[
                html.Div(className="card", children=[
                    html.H3("Save multiple data"),
                    html.P("Several shots can be saved by uploading a csv file in the box below."),
                    html.P("The following columns with allowed values can be uploaded. Columns with an asterisk are required."),
                    html.Ul([
                        html.Li(["*club: 1W, 3W, 4, 5, 6, 7, 8, 9, P, 52, 56"]),
                        html.Li(["*total_distance: Integer"]),
                        html.Li(["*carry_distance: Integer"]),
                        html.Li(["*date: yyyy-mm-dd"]),
                        html.Li(["missed: 0, 1"]),
                        html.Li(["ball_speed: Integer"]),
                        html.Li(["launch_angle: Integer"]),
                        html.Li(["height: Integer"]),
                        html.Li(["impact_angle: Integer"]),
                        html.Li(["hang_time: Float"]),
                        html.Li(["curve: Integer"]),
                        html.Li(["side: Integer"]),
                    ]),
                    dcc.Upload(
                        id="data_upload_id",
                        children=html.Div([
                            'Drag and Drop or ',
                            html.A(className="upload_link", children=['Select Files'])
                        ]),
                        # Allow multiple files to be uploaded
                        multiple=True,
                    ),
                ]),
            ]),

            # UPLOAD FORM
            html.Div(className="upload-form", children=[
                html.Div(className="card", children=[
                    html.H3("Save single shots"),
                    html.P("You can enter single shots in this form. All fields must be filled."),
                    html.Div(className="form grid grid-4", children=[
                        html.Div([
                            html.H4("*Club"),
                            dcc.Dropdown(
                                id="club_dropdown_id",
                                className="upload-form-element",
                                options=[
                                    {'label': '1 Wood', 'value': '1W'},
                                    {'label': '3 Wood', 'value': '3W'},
                                    {'label': '4 Iron', 'value': '4'},
                                    {'label': '5 Iron', 'value': '5'},
                                    {'label': '6 Iron', 'value': '6'},
                                    {'label': '7 Iron', 'value': '7'},
                                    {'label': '8 Iron', 'value': '8'},
                                    {'label': '9 Iron', 'value': '9'},
                                    {'label': 'P', 'value': 'P'},
                                    {'label': '52', 'value': '52'},
                                    {'label': '56', 'value': '56'},
                                ],
                                style={
                                    'fontSize': '15px',
                                    'height': '10px',
                                    'width': '100px',
                                    'borderColor': '#000000',
                                    }
                            )
                        ]),
                        html.Div([
                            html.H4("*Total distance"),
                            dcc.Input(
                                id='total_distance_input_id',
                                className="upload-form-element number",
                                type='number',
                                min=0,
                                max=300,
                                step=1,
                                placeholder="Meters",
                            )
                        ]),
                        html.Div([
                            html.H4("*Carry distance"),
                            dcc.Input(
                                id='carry_distance_input_id',
                                className="upload-form-element number",
                                type='number',
                                min=0,
                                max=300,
                                step=1,
                                placeholder="Meters",
                            )
                        ]),
                        html.Div([
                            html.H4("*Date"),
                            dcc.DatePickerSingle(
                                id="upload_form_date_id",
                                className="upload-form-element",
                                first_day_of_week=1,
                                initial_visible_month=datetime.datetime.now().date(),
                                placeholder=f"{datetime.datetime.now().date()}",
                                display_format="YYYY-MM-DD",
                            )
                        ]),
                        html.Div([
                            html.H4("Missed"),
                            dcc.RadioItems(
                                id="missed_radio_id",
                                options=[
                                    {'label': 'Yes', 'value': 1},
                                    {'label': 'No', 'value': 0},
                                ],
                                value=0,
                            )
                        ]),
                        html.Div([
                            html.H4("Ball speed"),
                            dcc.Input(
                                id='ball_speed_input_id',
                                className="upload-form-element number",
                                type='number',
                                min=0,
                                max=1000,
                                step=1,
                                placeholder="m/s",
                            )
                        ]),
                        html.Div([
                            html.H4("Launch angle"),
                            dcc.Input(
                                id='launch_angle_input_id',
                                className="upload-form-element number",
                                type='number',
                                min=0,
                                max=100,
                                step=1,
                                placeholder="Degree",
                            )
                        ]),
                        html.Div([
                            html.H4("Height"),
                            dcc.Input(
                                id='height_input_id',
                                className="upload-form-element number",
                                type='number',
                                min=0,
                                max=300,
                                step=1,
                                placeholder="Meters",
                            )
                        ]),
                        html.Div([
                            html.H4("Impact angle"),
                            dcc.Input(
                                id='impact_angle_input_id',
                                className="upload-form-element number",
                                type='number',
                                min=0,
                                max=100,
                                step=1,
                                placeholder="Degree",
                            )
                        ]),
                        html.Div([
                            html.H4("Hang time"),
                            dcc.Input(
                                id='hang_time_input_id',
                                className="upload-form-element number",
                                type='number',
                                min=0,
                                max=100,
                                step=0.1,
                                placeholder="Seconds",
                            )
                        ]),
                        html.Div([
                            html.H4("Curve"),
                            dcc.Input(
                                id='curve_input_id',
                                className="upload-form-element number",
                                type='number',
                                min=-100,
                                max=100,
                                step=1,
                                placeholder="Meters",
                            )
                        ]),
                        html.Div([
                            html.H4("Side"),
                            dcc.Input(
                                id='side_input_id',
                                className="upload-form-element number",
                                type='number',
                                min=-1000,
                                max=100,
                                step=1,
                                placeholder="Meters",
                            )
                        ]),
                    ]),
                    html.Div([
                        html.Button("Save", className="btn", id="save_upload_form_btn"),
                    ]),
                    html.Div(id="upload_form_response"),
                ]),
            ]),

        # Display a table with uploaded CSV data
        html.Div(id="output-data-upload"),
        ]),
    ])
])


# LAYOUT: Club details
details_layout = html.Div(className="container", children=[
    # Tabs and stuff here
    dcc.Tabs(id="club_tabs_id", value="1W", children=[
        dcc.Tab(label=val, value=key) for key, val in club_enum.items() if key in df.club.unique()
    ]),
    html.Div(className="club-details", children=[
        html.Div(className="grid grid-6", children=[
            html.Div(className="error-band card", children=[
                html.H3("Error band"),
                dcc.Graph(id="error_band_graph_id"),
                html.P("Window size"),
                dcc.Slider(
                    id="errorband_slider_id",
                    min=1,
                    max=df.groupby('club').count().total_distance.max(),
                    marks={i: str(i) for i in range(0, 101, 5)},
                    value=20,
                    step=None,
                ),
                dcc.RadioItems(
                    id='errband-total-carry-option',
                    options=[
                        {'label': 'Total distance', 'value': 'total_distance'},
                        {'label': 'Carry distance', 'value': 'carry_distance'},
                    ],
                    value='total_distance',
                    labelStyle={'display': 'inline-block'}
                )
            ]),
        ]),
    ])
])

@app.callback(
    Output('error_band_graph_id', 'figure'),
    Input('club_tabs_id', 'value'),
    Input('errband-total-carry-option', 'value'),
    Input('errorband_slider_id', 'value'),
    )
def plot_error_band(club, column, window_size):
    fig = get_errorband_fig(df, club, column, window_size)
    return fig


"""
CALLBACK: Home page
"""
@app.callback(
    Output('region_graph_id', 'figure'),
    Input('show-scatter-option', 'value'),
    Input('region_clubs_options', 'value'),
    Input('region_nvals_options', 'value'),
    )
def region_plot(show, clubs, nvals):
    nvals = None if nvals==0 else nvals
    fig = plot_conf_ellipse(df, show=show, clubs=clubs, nvals=nvals)
    return fig


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
    return f"Selected range: {a}-{b} m"


@app.callback(
    Output('box-plot-graph', 'figure'),
    Input('box_radio_distance_id', 'value'),
    Input('box_radio_axis_id', 'value'),
    Input('box_radio_nvals_id', 'value'),
)
def generate_box_plot(distance, axis, nvals):
    fig = get_boxplot_fig(df, distance=distance, axis=axis, nvals=nvals)    
    return fig


@app.callback(
    Output('ridgeplot-graph', 'figure'),
    Input('ridge_radio_distance_id', 'value'),
    Input('ridge_radio_nvals_id', 'value'),
)
def generate_ridgeplot(distance, nvals):
    fig = get_ridgeplot_fig(df, distance=distance, nvals=nvals)    
    return fig


@app.callback(
    Output('heatplot-graph', 'figure'),
    Input('heat-data-option', 'value'),
    Input('heat-slider', 'value'),
)
def generate_heatplot(stat, window_size):
    fig = get_heatplot_fig(df, stat, window_size)
    return fig

"""
CALLBACK: Data page
"""
@app.callback(Output('download_id', 'data'),
              Input('download_btn_id', 'n_clicks'),
              prevent_initial_call=True)
def download_pdf(n_clicks):
    return dcc.send_file("./assets/files/golf_logg.pdf")

@app.callback(Output('refresh_id', 'data'),
              Input('refresh_btn_id', 'n_clicks'),
              prevent_initial_call=True)
def refresh_data(n_clicks):
    update_df(engine)

@app.callback(Output('output-data-upload', 'children'),
              Input('data_upload_id', 'contents'),
              State('data_upload_id', 'filename'),
              State('data_upload_id', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [parse_file_upload(contents, filename, engine, session) for contents, filename in zip(list_of_contents, list_of_names)]
        update_df(engine)
        return children

@app.callback(
    Output('upload_form_response', 'children'),
    Input('save_upload_form_btn', 'n_clicks'),
    State('club_dropdown_id', 'value'),
    State('total_distance_input_id', 'value'),
    State('carry_distance_input_id', 'value'),
    State('missed_radio_id', 'value'),
    State('upload_form_date_id', 'date'),
    State('ball_speed_input_id', 'value'),
    State('launch_angle_input_id', 'value'),
    State('height_input_id', 'value'),
    State('impact_angle_input_id', 'value'),
    State('hang_time_input_id', 'value'),
    State('curve_input_id', 'value'),
    State('side_input_id', 'value'),
    prevent_initial_call=True)
def upload_form_to_db(n_clicks, club, total, carry, missed, date, ball_speed, launch_angle, height, impact_angle, hang_time, curve, side):
    
    # Check if all fields are entered correctly
    if any([arg is None for arg in [club, total, carry, date]]):
        return html.H2(className="upload-error-message", children=[
            "Fields with an asterisk are required"
        ])
    
    new_shot = Shots(
        club=club,
        total_distance=total,
        carry_distance=carry,
        missed=bool(missed),
        date=datetime.datetime.strptime(date, '%Y-%m-%d').date(),
    )
    session.add(new_shot)
    session.commit()
    update_df(engine)
    return html.H2(
        className = "upload-success-message",
        children = ["Shot saved"],
        )





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
