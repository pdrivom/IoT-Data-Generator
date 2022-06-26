from fastapi.testclient import TestClient
import uuid
import sys
sys.path.insert(0,".")
from api import app
from api import app

client = TestClient(app)
device = str(uuid.uuid4())
data = {
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

def test_get_devices():
    """ Tests GET all devices endpoint """

    response = client.get("/api/v1/devices")
    assert response.status_code == 200
    resp = response.json()
    assert len(resp["items"]) == resp["total"]

def test_device_sequence():
    """ Runs testing sequence """

    add_device_bad_body()
    add_device()
    get_device()
    add_metadata()
    get_metadata()
    delete_metadata()
    get_inexistent_metadata()
    delete_inexistent_metadata()
    delete_device()
    get_inexistent_device()
    delete_inexistent_device()


def add_device():
    """ Tests Add device """

    response = client.post("/api/v1/device", json=data)
    assert response.status_code == 201
    assert response.json() == data

def add_device_bad_body():
    """ Tests Add device with bad body"""

    response = client.post("/api/v1/device", json={})
    assert response.status_code == 422

def get_device():
    """ Tests Get device """

    response = client.get(f"/api/v1/device/{device}")
    assert response.status_code == 200
    assert response.json() == data

def delete_device():
    """ Tests Delete device """

    response = client.delete(f"/api/v1/device/{device}")
    assert response.status_code == 200
    response.json() == device

def get_inexistent_device():
    """ Tests Get inexistent device """

    response = client.get(f"/api/v1/device/{device}")
    assert response.status_code == 404

def delete_inexistent_device():
    """ Tests Delete inexistent device """

    response = client.delete(f"/api/v1/device/{device}")
    assert response.status_code == 404

def add_metadata():
    response = client.put(f"/api/v1/device/{device}/metadata", json=metadata)
    assert response.status_code == 201
    assert response.json() == metadata

def get_metadata():
    response = client.get(f"/api/v1/device/{device}/metadata")
    assert response.status_code == 200
    assert response.json() == metadata

def delete_metadata():
    response = client.delete(f"/api/v1/device/{device}/metadata")
    assert response.status_code == 200

def get_inexistent_metadata():
    response = client.get(f"/api/v1/device/{device}/metadata")
    assert response.status_code == 404

def delete_inexistent_metadata():
    response = client.delete(f"/api/v1/device/{device}/metadata")
    assert response.status_code == 404