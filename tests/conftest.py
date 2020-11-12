import pytest
import os
import sqlite3

from homesens import homesens


@pytest.fixture
def client():
    # db_fd, homesens.app.config['DATABASE'] = tempfile.mkstemp()
    homesens.app.config['TESTING'] = True

    with homesens.app.test_client() as client:
        with homesens.app.app_context():
            homesens.init_db()
        yield client

	# os.close(db_fd)
	# os.unlink(flaskr.app.config['DATABASE'])
