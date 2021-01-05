import matplotlib

matplotlib.use('Agg')  # run matplotlib headless (for virtualenv)
import numpy as np
import plotly.graph_objects as go
import pandas
import base64

from utils import *


# TMP_FILENAME_PREFIX = 'homesens/static/images/tmp_plot_collection'
# TMP_FILENAME_EXT = '.png'


def select_data_span(data, span):
    spans = np.array([24, 24 * 7, 24 * 30, 24 * 365])  # available time spans for day/week/month/year
    # now we have a measurement every half hour
    spans = 2 * spans

    data_span = []
    end_idx = None

    # print 'selected time span:', span
    if span == 'day':
        end_idx = spans[0]
    elif span == 'week':
        end_idx = spans[1]
    elif span == 'month':
        end_idx = spans[2]
    elif span == 'year':
        end_idx = spans[3]

    if len(data) >= end_idx:
        data_span = (data[:end_idx])
    else:
        data_span = data

    return data_span


def plot_plotly(data_list, span):
    DEBUG("plotting for span: " + span)
    data_frames = []
    for data in data_list:
        data = select_data_span(data, span)
        data = np.array(data)
        data = np.flipud(data)  # entries come in reversed order

        df = pandas.DataFrame(data[:, 1:], index=data[:, 0], columns=['temp', 'press', 'humid'])
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

    for label, content in data_frames[-1].iteritems():
        ref_values = get_ref_plot_values(df, content.ref)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ref_values[0], y=ref_values[1], name='ref.', line_color='grey'))  # fill to trace0 y
        for df in data_frames:
            fig.add_trace(
                go.Scatter(x=df.index, y=content, name=content.label + df.name))  # TODO check:, fill='tonexty'

        set_plotly_fig_style(fig)
        # fig.show()
        html_fig[label] = fig.to_html(include_plotlyjs=False)
        # with open('debug.html', 'w') as f:
        #    f.write(html_fig[label])
        # The following could reduce plot size compared to plotly html strings:
        # img = io.BytesIO()
        # fig.write_image(img)
        # base64_str = fig_to_base64(img)
        # html_fig[label] = base64_to_html_fig(base64_str)
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
