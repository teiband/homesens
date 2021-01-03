import os

import requests
import json

os.chdir('../')


def test_add_measurement():
    url = "http://localhost:5000/add-measurement"
    payload = dict(temperature=1.0, pressure=2.0, humidity=3.0)
    print(payload)
    response = requests.post(url, json=json.dumps(payload))

    assert response.status_code == 200


def test_get_updated_status():
    url = "http://localhost:5000/get-status-update"
    payload = dict()
    response = requests.get(url, json=json.dumps(payload))
    print(response.json())
    assert response.status_code == 200