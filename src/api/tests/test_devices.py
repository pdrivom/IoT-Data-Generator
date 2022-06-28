from fastapi.testclient import TestClient
import json
import uuid
import sys
sys.path.insert(0,".")
from api import v1, table_devices, running_devices, table_templates

client = TestClient(v1)
device = str(uuid.uuid4())
config = {
"name": f"{device}",
"kafka_server": "kafka:9092",
"kafka_topic": "usage",
"frequency_s": 1,
"messages":100,
"timestamp_label": "date",
"auto_start": True
}

metadata = {
"name": "{{name()}}",
"isActive": "{{bool()}}",
"latitude": "{{floating(-90.000001, 90)}}",
"longitude": "{{floating(-180.000001, 180)}}"
}


def test_device_sequence():
    """ Runs testing sequence """

    delete_devices()
    get_metadata_sample()
    add_device_bad_body()
    add_device()
    get_device()
    get_devices()
    add_metadata()
    get_metadata()
    generate_from_metadata()
    start_device()
    start_all_devices()
    get_running_devices()
    stop_device()
    stop_all_devices()
    delete_metadata()
    get_inexistent_metadata()
    delete_inexistent_metadata()
    delete_device()
    delete_devices()
    get_inexistent_device()
    delete_inexistent_device()


def get_devices():
    """ Tests GET all devices endpoint """

    response = client.get("/api/v1/devices")
    assert response.status_code == 200
    resp = response.json()
    assert len(resp["items"]) == resp["total"]

def delete_devices():
    """ Tests DELETE all devices endpoint """

    response = client.delete("/api/v1/devices")
    assert response.status_code == 200
    assert  response.json()["total"] == 0
    assert len(table_devices.all()) == 0

def get_running_devices():
    response = client.get("/api/v1/devices/running")
    assert response.status_code == 200
    assert response.json()['items'][0] == config

def start_all_devices():
    response = client.put("/api/v1/devices/start")
    assert response.status_code == 202
    assert response.json()["total"] == 1

def stop_all_devices():
    response = client.put("/api/v1/devices/stop")
    assert response.status_code == 202
    assert response.json()["total"] == 0

def add_device():
    """ Tests Add device """

    response = client.post("/api/v1/device", json=config)
    assert response.status_code == 201
    assert response.json() == config

def add_device_bad_body():
    """ Tests Add device with bad body"""

    response = client.post("/api/v1/device", json={})
    assert response.status_code == 422

def get_device():
    """ Tests Get device """

    response = client.get(f"/api/v1/device/{device}")
    assert response.status_code == 200
    assert response.json() == config

def delete_device():
    """ Tests Delete device """

    response = client.delete(f"/api/v1/device/{device}")
    assert response.status_code == 200
    response.json() == device

def start_device():
    """ Tests start device """

    response = client.put(f"/api/v1/device/{device}/start")
    assert response.status_code == 202
    assert  response.json()["total"] == 1
    assert device in running_devices

def stop_device():
    """ Tests Stop device """

    response = client.put(f"/api/v1/device/{device}/stop")
    assert response.status_code == 202
    assert  response.json()["total"] == 0
    assert device not in running_devices

def get_inexistent_device():
    """ Tests Get inexistent device """

    response = client.get(f"/api/v1/device/{device}")
    assert response.status_code == 404

def delete_inexistent_device():
    """ Tests Delete inexistent device """

    response = client.delete(f"/api/v1/device/{device}")
    assert response.status_code == 404

def add_metadata():
    """ Tests Add metadata to device """

    response = client.put(f"/api/v1/device/{device}/metadata", json=metadata)
    assert response.status_code == 201
    assert response.json() == metadata

def get_metadata():
    """ Tests Get metadata of device """

    response = client.get(f"/api/v1/device/{device}/metadata")
    assert response.status_code == 200
    assert response.json() == metadata

def delete_metadata():
    """ Tests Delete metadata to device """

    response = client.delete(f"/api/v1/device/{device}/metadata")
    assert response.status_code == 200

def get_inexistent_metadata():
    """ Tests Get inexistent metadata of device """

    response = client.get(f"/api/v1/device/{device}/metadata")
    assert response.status_code == 404

def delete_inexistent_metadata():
    """ Tests Delete inexistent metadata of device """

    response = client.delete(f"/api/v1/device/{device}/metadata")
    assert response.status_code == 404

def generate_from_metadata():
    """ Tests Generate metadata of device """

    response = client.get(f"/api/v1/device/{device}/metadata/generate")
    assert response.status_code == 200
    assert response.json() != metadata

def get_metadata_sample():
    """ Tests Get metadata sample """

    with open('./samples/sample.json', 'r') as f:
            s = f.read()
            response = client.get("/api/v1/metadata/sample")
            assert response.status_code == 200
            assert response.json() == json.loads(s)