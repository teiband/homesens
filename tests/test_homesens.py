import pytest
from homesens.homesens import create_plots, show_entries


def test_db(client):
    db = client.get_db()
    # timestamp is in UTC, convert to CET
    cur = db.execute(
        'select datetime (timestamp,\'localtime\'), temperature, pressure, humidity from entries order by id desc')
    entries = cur.fetchmany(20)

#create_plots()