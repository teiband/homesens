import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
	 render_template, flash
import homesens.plot_collection as plot_collection
import time
from multiprocessing import Process # create plots in background


app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file
#app.run(host='0.0.0.0') # run puplic availabe over the network, this is unsecure!!!

plot_background_process = None # This process is created later and shut down when the app crashes

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
	cur = db.execute('select datetime (timestamp,\'localtime\'), temperature, pressure, humidity from entries order by id desc')
	entries = cur.fetchmany(20)

	plot_filenames_unsorted = [filename for filename in os.listdir('homesens/static/images') if filename.startswith('tmp_plot_collection')]
	plot_filenames = []
	spans = ['day', 'week', 'month', 'year']
	for span in spans:
		if plot_filenames_unsorted:
			plot_filenames.append( 'images/' + [f for f in plot_filenames_unsorted if span in f][0] )
	
	return render_template('show_entries.html', entries=entries, plot_filenames=plot_filenames)


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

def create_plots(spans):
	with app.app_context():
		db = get_db()
		# timestamp is in UTC, convert to CET
		cur = db.execute('select datetime (timestamp,\'localtime\'), temperature, pressure, humidity from entries order by id desc')
		entries = cur.fetchall()
	
	os.system('rm ' + plot_collection.TMP_FILENAME_PREFIX + '*') # delete old files
	for span in spans:
		plot_collection.plot_mult_in_one(entries, span)
	
	plot_filenames_unsorted = [filename for filename in os.listdir('homesens/static/images') if filename.startswith('tmp_plot_collection')]
	plot_filenames = []
	
	for span in spans:
		plot_filenames.append( 'images/' + [f for f in plot_filenames_unsorted if span in f][0] )
	
	entries = entries[1:20] # show only last 20 elements in table

def create_plots_routine(spans):
	print("Started 'create_plots_routine'")
	while True:
		create_plots(spans)
		time.sleep(60*5) # 5 minutes

def spawn_background_threads():
	spans = ['day', 'week', 'month', 'year']
	plot_background_process = Process(target=create_plots_routine, args=(spans,))
	plot_background_process.start()
	#plot_background_process.join()

#spawn_background_threads()
