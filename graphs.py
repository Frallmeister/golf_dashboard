import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
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
