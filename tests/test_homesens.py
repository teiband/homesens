import pytest
import os
from homesens.homesens import create_plots, get_db, app, connect_db


def test_db(client):

    with app.app_context():
        db = get_db()
        # timestamp is in UTC, convert to CET
        cur = db.execute(
            'select datetime (timestamp,\'localtime\'), temperature, pressure, humidity from entries order by id asc')
        entries = cur.fetchmany(20)
        print(entries)


def test_create_plots():
    html_figs = dict(day=None, week=None, month=None, year=None)
    create_plots(['day'], html_figs)

os.chdir('../.')

test_create_plots()