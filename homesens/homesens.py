import os
import sqlite3
import time
from copy import deepcopy
from multiprocessing import Process, Manager  # create plots in background

from flask import Flask, request, session, g, redirect, url_for, abort, \
    render_template, flash

import homesens.plot_collection as plot_collection
from homesens.utils import *


app = Flask(__name__)  # create the application instance :)
app.config.from_object(__name__)  # load config from this file
# app.run(host='0.0.0.0') # run puplic availabe over the network, this is unsecure!!!

plot_background_process = None  # This process is created later and shut down when the app crashes

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'homesens.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('HOMESENS_SETTINGS', silent=True)


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

    if plot_background_process:
        plot_background_process.terminate()
        plot_background_process.join()


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
def show_entries():
    db = get_db()
    # timestamp is in UTC, convert to CET
    cur = db.execute(
        'select datetime (timestamp,\'localtime\'), temperature, pressure, humidity from entries order by id desc')
    entries = cur.fetchmany(20)
    spans = ['day', 'week', 'month', 'year']

    # if not 'day' in namespace.html_figs.keys():
    #	create_plots(['day'], namespace.html_figs)
    # with open('debug.html', 'w') as f:
    #	f.write(html_figs['day'])

    DEBUG("Content of html_figs " + str(namespace.html_figs.keys()))
    # DEBUG(html_figs)
    # print(namespace.html_figs)
    return render_template('show_entries.html', entries=entries, html_figs=namespace.html_figs)


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
            'select datetime (timestamp,\'localtime\'), temperature, pressure, humidity from entries order by id desc')
        entries = cur.fetchall()

    for span in spans:
        # DEBUG("assign html_figs to span")
        html_figs[span] = deepcopy(plot_collection.plot_plotly(entries, span))


# html_figs[span] = 1
# DEBUG("keys: " + str(html_figs.keys()))


# DEBUG("html_figs keys: " + str(html_figs.keys()))


def create_plots_routine(spans, interval, html_figs):
    DEBUG("started.")
    while True:
        DEBUG("Creating all plots...")
        create_plots(spans, html_figs)
        DEBUG("sleeping...")
        time.sleep(interval)


# print(html_figs)


def spawn_background_threads(html_figs):
    spans = ['day', 'week', 'month', 'year']
    interval = 30  # in seconds: 30 minutes
    plot_background_process = Process(target=create_plots_routine, args=(spans, interval, html_figs))
    plot_background_process.start()


# plot_background_process.join()


background_plot_manager = Manager()
namespace = background_plot_manager.Namespace()
namespace.html_figs = background_plot_manager.dict()
spawn_background_threads(namespace.html_figs)

# INFO: this module is loaded twice in debug mode.
