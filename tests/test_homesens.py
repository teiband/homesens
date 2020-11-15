import pytest
import os
from homesens.homesens import create_plots, show_entries, get_db, app, connect_db


def test_db(client):

    with app.app_context():
        db = get_db()
        # timestamp is in UTC, convert to CET
        cur = db.execute(
            'select datetime (timestamp,\'localtime\'), temperature, pressure, humidity from entries order by id desc')
        entries = cur.fetchmany(20)
        print(entries)


def test_create_plots():
    create_plots(['day'])

os.chdir('../.')

test_create_plots()