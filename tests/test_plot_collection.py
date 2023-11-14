import os
#os.environ['PYTHONPATH'] = '$PYTHONPATH:/home/pi/workspace/homesens-devel/'
os.chdir('../')
import plot_collection as plot_collection
import pickle
from homesens import *
import pytest


@pytest.fixture
def db_entries():
	with app.app_context():
		db = get_db()
		cur = db.execute("select datetime (timestamp,\'localtime\'), temperature, pressure, humidity from entries order by id desc")
		entries = cur.fetchall()
		return entries


@pytest.fixture
def db_entries_esp32_1():
	with app.app_context():
		db = get_db()
		cur = db.execute("select datetime (timestamp,\'localtime\'), temperature, pressure, humidity from 'homesens-extension-esp32-1' order by id desc")
		entries = cur.fetchall()
		return entries

def test_sqlite_query():
	with app.app_context():
		db = get_db()
		cur = db.execute('select datetime (timestamp,\'localtime\'), temperature, pressure, humidity from entries order by id desc')
		global entries
		entries = cur.fetchall()
	
	
def test_plot_collection(db_entries):
	#spans = ['day', 'week', 'month', 'year']
	spans = ['day']
	for span in spans:
		plot_plotly(db_entries, span)


if __name__ == '__main__':

	test_sqlite_query()
	entries = db_entries()
	test_plot_collection(entries)
