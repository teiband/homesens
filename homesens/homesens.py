import copy
import datetime
import os
import sqlite3
import time
from copy import deepcopy
from multiprocessing import Process, Manager  # create plots in background

import schedule as schedule
from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash, jsonify

from asist_tools import convert_currency_page

print(os.getcwd())

import user_defines
from plot_collection import *
from utils import *

# from flask_socketio import SocketIO, send, emit

EXTENSION_ESP32_1_TABLE_NAME = "'homesens-extension-esp32-1'"


def create_app():
    return Flask(__name__)


# app = create_app()

app = Flask(__name__)
app.register_blueprint(convert_currency_page)

app.config.from_object(__name__)  # load config from this file
# app.run(host='0.0.0.s0') # run puplic availabe over the network, this is unsecure!!!

background_process_list = []
# plot_background_process = None  # This process is created later and shut down when the app crashes

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'homesens.db'),
    SECRET_KEY='development-key',
    USERNAME='admin',
    PASSWORD='default',
    PLOT_CYCLE_TIME=60 * 5
))
app.config.from_envvar('HOMESENS_SETTINGS', silent=True)


# socketio = SocketIO(app)
# if __name__ == "__main__":
# socketio.run(app)


# @socketio.on('message')
# def handle_message(data):
#    print('received message: ' + data)
#    send("greetings from homesens")


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


# @app.teardown_appcontext
def terminate_background_processes(error):
    for p in background_process_list:
        print(f"Terminating process: {p.name}...")
        p.terminate()
        p.join()


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


def UTC2CET(utc_timestamp):
    hour = int(utc_timestamp[-8:-6])
    if time.localtime().tm_isdst:
        hour = hour + 2
    else:
        hour = hour + 1
    if hour > 24:
        hour = hour - 24

    cet_timestamp = utc_timestamp[1:-9] + str(hour) + utc_timestamp[-6:]
    return cet_timestamp


@app.route('/')
def index():
    db = get_db()
    # timestamp is in UTC, convert to CET
    cur = db.execute(
        "select datetime (timestamp,\'localtime\'), temperature, pressure, humidity from entries order by id desc")
    entries = cur.fetchmany(20)
    spans = ['day', 'week', 'month', 'year']

    cur = db.execute(
        "select datetime (timestamp,\'localtime\'), temperature, pressure, humidity from 'homesens-extension-esp32-1' order by id desc")
    esp_32_1_entries = cur.fetchmany(20)

    DEBUG("Content of html_figs " + str(namespace.html_figs.keys()))
    # DEBUG(html_figs)
    # print(namespace.html_figs)
    return render_template('show_entries.html', entries=entries, html_figs=namespace.html_figs,
                           esp_32_1_entries=esp_32_1_entries)


@app.route('/post-measurement', methods=['POST'])
def add_measurement():
    DEBUG(request.json)
    if request.json['api_key'] != user_defines.EXTENSION_API_KEY:
        return 'ERR_INVALID_API_KEY'
    # insert value only at specific times
    now = datetime.now()
    sel_minutes = [10 * x for x in range(6)]
    if now.minute in sel_minutes and now.second >= 0.0 and now.second < 10.0:
        DEBUG("posting values to db...")
        db = get_db()
        temperature = float(request.json['temperature'])
        pressure = float(request.json['pressure'])
        humidity = float(request.json['humidity'])
        insert_measurement_into_db(db, EXTENSION_ESP32_1_TABLE_NAME, temperature, pressure, humidity)
    else:
        DEBUG("ignoring measurements " + str(now) + str(now.second))
    return 'OK'


def insert_measurement_into_db(db, table_name, temperature, pressure, humidity):
    db.execute(
        'insert into {table_name} (temperature, pressure, humidity) values (?, ?, ?)'.format(table_name=table_name),
        [temperature, pressure, humidity])
    db.commit()
    print('New entry was successfully posted\n'
          'values are (temp, press, humid): %.2f, %.2f, %.2f' % (temperature, pressure, humidity))


@app.route('/get-status-update', methods=['GET'])
def get_updated_status():
    # DEBUG("request params: " + str(request.args))
    if request.args.get('api_key') != user_defines.EXTENSION_API_KEY:
        return 'ERR_INVALID_API_KEY'
    status = jsonify(command_1=1.0, command_2=2.0)
    # DEBUG('response: ' + str(status.data))
    return status


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
               [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


def create_plots(spans, html_figs):
    with app.app_context():
        db = get_db()
        # timestamp is in UTC, convert to CET
        cur = db.execute(
            'select datetime (timestamp,\'localtime\'), temperature, pressure, humidity from entries order by id asc')
        entries = cur.fetchall()  # TODO fetch only max 1 year back
        if len(entries) == 0:
            raise ValueError("Table has no entries: " + "entries")

        cur = db.execute(
            "select datetime (timestamp,\'localtime\'), temperature, pressure, humidity from {table_name} order by id asc".format(
                table_name=EXTENSION_ESP32_1_TABLE_NAME))
        esp32_1_entries = cur.fetchall()  # TODO fetch only max 1 year back
        if len(esp32_1_entries) == 0:
            # raise ValueError("Table has no entries: " + EXTENSION_ESP32_1_TABLE_NAME)
            # add single dummy entry for bootstrapping
            esp32_1_entries = copy.copy(entries)

    for span in spans:
        # DEBUG("assign html_figs to span")
        data_list = [entries, esp32_1_entries]
        html_figs[span] = deepcopy(plot_plotly(data_list, span))


def create_plots_routine(spans, interval, html_figs):
    DEBUG("started.")
    while True:
        DEBUG(f"Creating plots for {spans} ...")
        create_plots(spans, html_figs)
        DEBUG("sleeping...")
        time.sleep(interval)


def create_plots_time_scheduled(spans, daytime, html_figs):
    """
    Runs a job at the specified daytime
    :param spans: list of time spans, e.g. ['day', 'week', 'month', 'year']
    :param daytime: string for daytime, e.g. "06:00"
    :param html_figs: list holding html figures
    """
    # Create plots once on startup, then only at scheduled time
    create_plots(spans, html_figs)
    schedule.every().day.at(daytime).do(create_plots, spans, html_figs)
    while True:
        schedule.run_pending()
        time.sleep(60)  # wait one minute


def spawn_background_threads(html_figs):
    spans = ['day', 'week', 'month', 'year']
    interval = float(app.config['PLOT_CYCLE_TIME'])
    p_all = Process(target=create_plots_routine, args=(spans, interval, html_figs))
    # p_day = Process(target=create_plots_routine, args=(['day'], interval, html_figs))
    # p_week = Process(target=create_plots_time_scheduled, args=(['week', 'month', 'year'], "06:00", html_figs))
    background_process_list.append(p_all)
    # background_process_list.append(p_day)
    # background_process_list.append(p_week)

    for p in background_process_list:
        print(f"Starting background process: {p.name} ...")
        p.start()


background_plot_manager = Manager()
namespace = background_plot_manager.Namespace()
namespace.html_figs = background_plot_manager.dict()
spawn_background_threads(namespace.html_figs)

# INFO: this module is loaded twice in debug mode.
