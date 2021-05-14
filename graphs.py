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

    fig = ff.create_distplot(hist_data, group_labels, show_hist=show_hist, show_rug=False)
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
        margin=dict(t=0, r=10, b=10, l=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1 
        ),
        showlegend=False,
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
        margin=dict(t=0, r=10, b=10, l=10),
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

def get_heatplot_fig(df, stat, window_size):
    clubs = [club for club in utils.club_enum if club in df.club.unique()]

    # Create df with rolling stddev
    dff = df.groupby('club')

    z = []
    for club in clubs:
        # Get values for each club and replace nan with None
        vals = dff.get_group(club).total_distance.dropna().rolling(window_size)
        if stat == 'stddev':
            vals = vals.std().to_list()
        elif stat == 'mean':
            vals = vals.mean().to_list()
        else:
            vals = vals.median().to_list()

        z.append(vals)

    n_y = max([len(i) for i in z])
    y = list(range(window_size, n_y+1))
    y = list(range(n_y+1))

    # Plot heatmap
    fig = go.Figure(data = go.Heatmap(
        z = z,
        y=y,
        x=clubs,
        hoverongaps=False,
        showscale=True,
        transpose=True,
        # colorscale='Plasma',
        # colorscale='Bluered',
        # colorscale='Jet',
        colorscale='Turbo',
        # colorscale='Portland',
        
    ))

    fig.update_layout(
        height=300,
        autosize=True,
        yaxis=dict(
            range=[window_size, n_y],
        ),
        margin=dict(t=0, r=10, b=10, l=10),
        xaxis_zeroline=False,
        showlegend=False,
        xaxis_title="<b>Club</b>",
        yaxis_title="Number of shots",
    )

    return fig


def get_errorband_fig(df, club, column, window_size):
    
    roll = df.groupby('club').get_group(club)[column].dropna().rolling(window_size)
    quant25 = roll.quantile(0.25)
    quant50 = roll.quantile(0.5)
    quant75 = roll.quantile(0.75)
    n_shots = len(quant50)

    ymax = df['total_distance'].max()
    ymin = df['carry_distance'].min()
    # range = [ymin-10, ymax+10]

    dates = df.groupby('club').get_group(club).loc[window_size+1:, 'date']

    fig = go.Figure([
        go.Scatter(
            name="Median",
            x=list(range(n_shots)),
            y=quant50,
            mode='lines',
            line=dict(color='rgb(31,119,180)'),
            showlegend=False,
        ),
        go.Scatter(
            name="75%",
            x=list(range(n_shots)),
            y=quant75,
            mode='lines',
            line=dict(width=0),
            marker=dict(color='#444'),
            showlegend=False,
        ),
        go.Scatter(
            name="25%",
            x=list(range(1, n_shots+1)),
            y=quant25,
            mode='lines',
            line=dict(width=0),
            marker=dict(color='#444'),
            fillcolor='rgba(68, 68, 68, 0.2)',
            fill='tonexty',
            showlegend=False,
        ),
    ])

    fig.update_layout(
        yaxis_title="Median (m)",
        xaxis_title="# Shots",
        hovermode="x",
        margin=dict(t=30, r=10, b=10, l=10),
        xaxis=dict(
            range=[window_size, n_shots],
            # tickmode='linear',
            # tick0=0,
            # dtick=1,
        ),
        yaxis=dict(range=[ymin-10, ymax+10]),
    )

    return fig
