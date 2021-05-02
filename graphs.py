import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.graph_objects as go
from plotly.colors import n_colors
import utils

def my_dist_plot(df, range, distance='total', show_hist=False):

    d = 'total_distance' if distance=='total' else 'carry_distance'

    clubs = df.club.unique()
    groups = df.groupby('club')

    hist_data = [groups.get_group(club)[d].dropna().values for club in clubs]
    group_labels = [utils.club_enum[club] for club in clubs]

    fig = ff.create_distplot(hist_data, group_labels, show_hist=show_hist)
    fig.update_layout(
        xaxis=dict(
            range=range,
            tickmode='linear',
            tick0=0,
            dtick=5),
        height=300,
        margin=dict(t=30, r=50, b=50, l=50),
        # hovermode="x",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1 
        )
    )
    return fig


def get_boxplot_fig(df, distance='total_distance', axis='yaxis', nvals='all'):

    colors = utils.rainbow_colors(len(df.club.unique()))

    # Get an ordered list of clubs, excluding clubs with no data
    clubs = [club for club in utils.club_enum.keys() if club in df.club.unique()]
    clubs.reverse()

    xmin = df.carry_distance.min() - 10
    xmax = df.total_distance.max() + 10

    # clubs, xmin, xmax = utils.get_clubs(df)

    fig = go.Figure()
    for club, color in zip(clubs, colors):
        values = df.groupby('club').get_group(club)[distance].values
        values = utils.get_values(values, nvals)
        name = utils.club_enum[club]
        if axis == 'yaxis':
            fig.add_trace(go.Box(y=values, name=name, marker_color=color))
        else:
            fig.add_trace(go.Box(x=values, name=name, marker_color=color))

    fig.update_layout(
        # height=300,
        margin=dict(t=60, r=10, b=10, l=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1 
        )
    )

    # Set properties to selected axis
    axis_kwargs = {'range': [xmin, xmax], 'tickmode': 'linear', 'tick0': 0, 'dtick': 10}
    if axis == 'yaxis':
        fig.update_layout(yaxis=axis_kwargs)
    else:
        fig.update_layout(xaxis=axis_kwargs)

    return fig


def get_ridgeplot_fig(df, distance='total_distance', nvals='all'):

    clubs, xmin, xmax = utils.get_clubs(df)
    colors = n_colors('rgb(242, 139, 0)', 'rgb(206, 0, 0)', 12, colortype='rgb')
    fig = go.Figure()
    for club, color in zip(clubs, colors):
        name = utils.club_enum[club]
        array = df.groupby('club').get_group(club)[distance].values
        data = utils.get_values(array, nvals)
        fig.add_trace(go.Violin(x=data, name=name, line_color=color))

    fig.update_traces(
        orientation='h',
        side='positive',
        width=3,
        points=False,
    )

    fig.update_layout(
        margin=dict(t=60, r=10, b=10, l=10),
        xaxis_showgrid=True,
        xaxis_zeroline=False,
        showlegend=False,
        xaxis=dict(
            range=[xmin-10, xmax+20],
            tickmode='linear',
            tick0=0,
            dtick=10,
        )
    )

    return fig

    return