import os

import requests
import json
import user_defines

os.chdir('../')


def test_add_measurement():
    url = "http://localhost:5000/post-measurement"
    test_sensor_name = 'esp32-bme280-1'
    payload = dict(api_key=user_defines.EXTENSION_API_KEY, sensor=test_sensor_name, temperature=1.0, pressure=2.0, humidity=3.0)
    print(payload)
    response = requests.post(url, json=payload)
    assert response.status_code == 200


def test_get_updated_status():
    url = "http://localhost:5000/get-status-update"
    test_sensor_name = 'esp32-bme280-1'
    payload = dict(api_key=user_defines.EXTENSION_API_KEY, sensor=test_sensor_name)
    response = requests.get(url, params=payload)
    data = response.json()
    assert isinstance(data, dict)
    assert response.status_code == 200