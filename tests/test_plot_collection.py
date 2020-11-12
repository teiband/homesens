import os
#os.environ['PYTHONPATH'] = '$PYTHONPATH:/home/pi/workspace/homesens-devel/'
os.chdir('../')
import homesens.plot_collection as plot_collection
import pickle
from homesens.homesens import *
import pytest


@pytest.fixture
def db_entries():
	with app.app_context():
		db = get_db()
		cur = db.execute('select datetime (timestamp,\'localtime\'), temperature, pressure, humidity from entries order by id desc')
		entries = cur.fetchall()
		return entries

def test_sqlite_query():
	with app.app_context():
		db = get_db()
		cur = db.execute('select datetime (timestamp,\'localtime\'), temperature, pressure, humidity from entries order by id desc')
		global entries
		entries = cur.fetchall()
		
	try:
		os.system('rm ' + plot_collection.TMP_FILENAME_PREFIX + '*') # delete old files
	except:
		print("no files to delete")
	
	
def test_plot_collection(db_entries):
	#spans = ['day', 'week', 'month', 'year']
	spans = ['year']
	for span in spans:
		plot_mult_in_one(entries, span)


if __name__ == '__main__':

	test_sqlite_query()
	entries = db_entries()
	test_plot_collection(entries)
