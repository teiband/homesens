# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
     
# my imports
#import plot_collection
#import matplotlib.pyplot as pl

#print(os.getcwd())
import plot_collection
import time
	
app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file
#app.run(host='0.0.0.0') # run puplic availabe over the network, this is unsecure!!!

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
    plot_collection.blub()
    print('after blub')
    db = get_db()
    cur = db.execute('select timestamp, temperature, pressure, humidity from entries order by id desc')
    entries = cur.fetchall()
    # timestamp is in UTC, convert to CET
    for entry in entries:
		entry[0] = UTC2CET(entry[0])
    # generate plot of current data
    plot_collection.plot_mult_in_one(entries,'day')
    return render_template('show_entries.html', entries=entries)
    
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

