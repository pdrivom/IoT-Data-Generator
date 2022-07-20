from fastapi.testclient import TestClient
import json
import os
import sys
from glob import glob
sys.path.insert(0,".")
from api import v1, table_devices, running_devices, table_destinations


client = TestClient(v1)
destinations = glob("./templates/*/", recursive = True)



def test_device_sequence():
    """ Runs testing sequence """

    for dest in destinations:
        path = os.path.normpath(dest)
        producer = path.split(os.sep)[1]
        destination = json.load(open(f"./templates/{producer}/destination.json"))
        device = json.load(open(f"./templates/{producer}/device.json"))
        metadata = json.load(open(f"./templates/{producer}/metadata.json"))

        delete_destinations()
        delete_devices()
        get_metadata_sample()
        add_device_no_destination(device)
        add_data_destination(producer,destination)
        get_data_destination(producer,destination)
        add_device_bad_body()
        add_device(device)
        get_device(device)
        get_devices()
        add_metadata(device,metadata)
        get_metadata(device,metadata)
        generate_from_metadata(device,metadata)
        start_device(device)
        start_all_devices()
        get_running_devices()
        stop_device(device)
        stop_all_devices()
        delete_metadata(device)
        get_inexistent_metadata(device)
        delete_inexistent_metadata(device)
        delete_device(device)
        delete_devices()
        get_inexistent_device(device)
        delete_inexistent_device(device)
        delete_data_destination(destination)
        delete_inexistent_data_destination(destination)
        delete_destinations()


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
    assert len(table_devices.all()) == 0

def get_running_devices():
    response = client.get("/api/v1/devices/running")
    assert response.status_code == 200
    #assert response.json()['items'][0] == config

def start_all_devices():
    response = client.put("/api/v1/devices/start")
    assert response.status_code == 202
    assert len(running_devices) > 0

def stop_all_devices():
    response = client.put("/api/v1/devices/stop")
    assert response.status_code == 202
    assert len(running_devices) == 0

def delete_destinations():
    """ Tests DELETE all destinations """

    response = client.delete("/api/v1/destinations")
    assert response.status_code == 200
    assert len(table_destinations.all()) == 0

def get_data_destination(name, destination):

    response = client.get(f"/api/v1/destination/{destination['name']}")
    destination['type'] = name
    assert response.status_code == 200
    assert response.json()['name'] == destination['name']

def add_data_destination(name, destination):
    """ Tests Add destination """

    response = client.post(f"/api/v1/destination/{name}", json=destination)
    assert response.status_code == 201
    assert response.json()['name'] == destination['name']

def delete_data_destination(destination):

    response = client.delete(f"/api/v1/destination/{destination['name']}")
    assert response.status_code == 200
    #assert not any(item for item in response.json() if item['name'] == name)

def delete_inexistent_data_destination(destination):

    response = client.delete(f"/api/v1/destination/{destination['name']}")
    assert response.status_code == 404
    #assert not any(item for item in response.json() if item['name'] == name)

def add_device(device):
    """ Tests Add device """

    response = client.post("/api/v1/device", json=device)
    assert response.status_code == 201
    assert response.json() == device

def add_device_no_destination(device):
    """ Tests Add device with no destination"""

    response = client.post("/api/v1/device", json=device)
    assert response.status_code == 404
    assert response.json() == {"detail":f"The data destination {device['name']} does not exists."}


def add_device_bad_body():
    """ Tests Add device with bad body"""

    response = client.post("/api/v1/device", json={})
    assert response.status_code == 422

def get_device(device):
    """ Tests Get device """

    response = client.get(f"/api/v1/device/{device['name']}")
    assert response.status_code == 200
    assert response.json() == device

def delete_device(device):
    """ Tests Delete device """

    response = client.delete(f"/api/v1/device/{device['name']}")
    assert response.status_code == 200
    #assert not any(item for item in response.json() if item['items']['name'] == name)

def start_device(device):
    """ Tests start device """

    response = client.put(f"/api/v1/device/{device['name']}/start")
    assert response.status_code == 202
    assert device['name'] in running_devices

def stop_device(device):
    """ Tests Stop device """

    response = client.put(f"/api/v1/device/{device['name']}/stop")
    assert response.status_code == 202
    assert device['name'] not in running_devices

def get_inexistent_device(device):
    """ Tests Get inexistent device """

    response = client.get(f"/api/v1/device/{device['name']}")
    assert response.status_code == 404

def delete_inexistent_device(device):
    """ Tests Delete inexistent device """

    response = client.delete(f"/api/v1/device/{device['name']}")
    assert response.status_code == 404

def add_metadata(device, metadata):
    """ Tests Add metadata to device """

    response = client.put(f"/api/v1/device/{device['name']}/metadata", json=metadata)
    assert response.status_code == 201
    assert response.json() == metadata

def get_metadata(device, metadata):
    """ Tests Get metadata of device """

    response = client.get(f"/api/v1/device/{device['name']}/metadata")
    assert response.status_code == 200
    assert response.json() == metadata

def delete_metadata(device):
    """ Tests Delete metadata to device """

    response = client.delete(f"/api/v1/device/{device['name']}/metadata")
    assert response.status_code == 200

def get_inexistent_metadata(device):
    """ Tests Get inexistent metadata of device """

    response = client.get(f"/api/v1/device/{device['name']}/metadata")
    assert response.status_code == 404

def delete_inexistent_metadata(device):
    """ Tests Delete inexistent metadata of device """

    response = client.delete(f"/api/v1/device/{device['name']}/metadata")
    assert response.status_code == 404

def generate_from_metadata(device,metadata):
    """ Tests Generate metadata of device """

    response = client.get(f"/api/v1/device/{device['name']}/metadata/generate")
    assert response.status_code == 200
    assert response.json() != metadata

def get_metadata_sample():
    """ Tests Get metadata sample """

    with open('./samples/sample.json', 'r') as f:
            s = f.read()
            response = client.get("/api/v1/metadata/sample")
            assert response.status_code == 200
            assert response.json() == json.loads(s)