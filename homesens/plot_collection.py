#import matplotlib
#matplotlib.use('Agg')  # run matplotlib headless (for virtualenv)
import numpy as np
import plotly.graph_objects as go
import pandas
import base64
from datetime import datetime, timedelta

from utils import *


def select_data_span(df, span):
    if span == 'day':
        delta = timedelta(days=1)
    elif span == 'week':
        delta = timedelta(days=7)
    elif span == 'month':
        delta = timedelta(days=31)
    elif span == 'year':
        delta = timedelta(days=365)

    earliest_date = str(datetime.now() - delta)
    #print("df.index > earliest_date", (df.index > earliest_date))
    df = df[df.index > earliest_date]
    #print('span:', span, 'earliest date:', earliest_date, 'count:', len(df), 'earliest:', df.index[0], 'last:', df.index[-1])
    return df


def plot_plotly(data_list, span):
    DEBUG("plotting for span: " + span)
    data_frames = []
    for data in data_list:
        #data = select_data_span(data, span)
        data = np.array(data)
        if data.ndim == 1:
            data = data[np.newaxis, ...]
        #data = np.flipud(data)  # entries come in reversed order

        df = pandas.DataFrame(data[:, 1:], index=data[:, 0], columns=['temp', 'press', 'humid'])
        df = select_data_span(df, span)

        df.temp.label = "Temp. in C°"
        df.press.label = "Press. in hPa"
        df.humid.label = "Humid. in % rel."

        def get_ref_plot_values(df, ref_value):
            refs = [[df.index[0], df.index[-1]], [ref_value, ref_value]]
            return refs

        df.temp.ref = 20.0
        df.press.ref = 950.0
        df.humid.ref = 60.0
        data_frames.append(df)

    data_frames[0].name = ''
    data_frames[1].name = ' (ESP32-1)'

    html_fig = {}  # contains three plots for all variables


    # iterate over data columns (temp, press, humid)
    for label in data_frames[0].keys():
        fig = go.Figure()
        # create plot for each dataframe
        # iterate over sensors
        has_ref_values = False
        for df in data_frames:
            content = getattr(df, label)
            if len(df) > 0 and not has_ref_values:
                # create one reference line from first dataframe
                ref_values = get_ref_plot_values(df, content.ref)
                fig.add_trace(go.Scatter(x=ref_values[0], y=ref_values[1], name='ref.', line_color='grey'))  # fill to trace0 y
                has_ref_values = True
            fig.add_trace(
                go.Scatter(x=df.index, y=df[label], name=content.label + df.name ))

        set_plotly_fig_style(fig)
        # fig.show()
        html_fig[label] = fig.to_html(include_plotlyjs=False)

    DEBUG("html figure size (Mb): " + str(len(html_fig[label]) * 16 / 1024 ** 2))
    return html_fig


def set_plotly_fig_style(fig):
    fig.update_layout(
        autosize=False,
        width=800,
        height=300,
        margin=dict(
            l=0,
            r=0,
            b=50,
            t=50,
            pad=4
        ),
        # paper_bgcolor="LightSteelBlue",
    )


def fig_to_base64(img):
    """
    Converts a figure to a base64 string
    :param: img: file descriptor/ byte stream of a png file
    """
    img.seek(0)
    base64_str = base64.b64encode(img.getvalue()).decode()
    return base64_str


def base64_to_html_fig(base64_str):
    """
    Returns a html image tag from a base64 string
    """
    return '<img src="data:image/png;base64,{}">'.format(base64_str)
