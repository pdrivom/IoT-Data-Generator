from fastapi import FastAPI, HTTPException, Request
from fastapi_pagination import Page, add_pagination, paginate
import jsons
import json
from tinydb import TinyDB, Query
from tinydb.table import Document
from models.models import Device
from lib.generate import generate
from lib.producer.producer import Producer, running_devices



db = TinyDB('./database/devices.json')
table_devices = db.table('devices')
table_templates = db.table('metadata')
devices = Query()
templates = Query()
v1 = FastAPI()

@v1.get("/api/v1/devices", tags=["Devices"], response_model=Page[Device])
async def get_devices(page: int = 1, size: int = 50):
    """Gets all saved devices"""
    return paginate(table_devices.all())

@v1.delete("/api/v1/devices", tags=["Devices"], response_model=Page[Device])
async def delete_devices():
    """Delete all devices and metadata"""
    db.drop_tables()
    return paginate(table_devices.all())

@v1.get("/api/v1/devices/running", tags=["Devices"], response_model=Page[Device])
async def get_running_devices():
    """Gets all running devices"""

    running = table_devices.search(devices.name.one_of(list(running_devices.keys())))
    return paginate(running)

@v1.put("/api/v1/devices/start", tags=["Devices"], response_model=Page[Device], status_code=202)
async def start_all_devices():
    """Start all devices"""

    for device in table_devices.all():
        d = device['name']
        if d not in running_devices:
            await start_device(d)
    return await get_running_devices()

@v1.put("/api/v1/devices/stop", tags=["Devices"], response_model=Page[Device], status_code=202)
async def stop_all_devices():
    """Stop all running devices"""

    running = running_devices.copy()
    for device in running:
        await stop_device(device)
    return await get_running_devices()

@v1.post("/api/v1/device", tags=["Device"], response_model=Device, status_code=201)
async def add_device(device: Device):
    """Saves a device"""

    exists = table_devices.get(devices.name == device.name)
    if exists == None:
        table_devices.insert(device.dict())
        return table_devices.get(devices.name == device.name)
    else:
        raise HTTPException(status_code=409, detail= f"The device {device.name} already exists")

@v1.get("/api/v1/device/{name}", tags=["Device"], response_model=Device)
async def get_device(name: str):
    """Gets saved device by name"""

    device = table_devices.get(devices.name == name)
    if device != None:
        return device
    else:
        raise HTTPException(status_code=404, detail= f"The device {name} does not exists")

@v1.put("/api/v1/device", tags=["Device"], response_model=Device)
async def update_device(device: Device):
    """Updates a device"""

    exists = table_devices.get(devices.name == device.name)
    if exists != None:
        table_devices.update(device.dict(), doc_ids=[exists.doc_id])
        return table_devices.get(devices.name == device.name)
    else:
        return await add_device(device)

@v1.delete("/api/v1/device/{name}", tags=["Device"], response_model=Page[Device])
async def delete_device(name: str):
    """Deletes a device"""

    device = await get_device(name)
    table_devices.remove(doc_ids=[device.doc_id])
    return paginate(table_devices.all())

@v1.put("/api/v1/device/{name}/metadata",tags=["Metadata"], status_code=201)
async def add_metadata(name: str, request: Request):
    """Saves the metadata of the device"""

    device = await get_device(name)
    template = await request.json()
    metadata = table_templates.get(doc_id=device.doc_id)
    if metadata != None:
        await delete_metadata(name)
    table_templates.insert(Document(template, device.doc_id))
    return table_templates.get(doc_id=device.doc_id)

@v1.put("/api/v1/device/{name}/start", tags=["Device"], response_model=Page[Device], status_code=202)
async def start_device(name: str):
    """Starts the device publication routine"""

    if name in running_devices:
        raise HTTPException(status_code=403, detail= f"The device {name} is already running.")
    else:
        device = await get_device(name)
        metadata = await get_metadata(name)
        producer = Producer(device, metadata)
        producer.start()
        return await get_running_devices()

@v1.put("/api/v1/device/{name}/stop", tags=["Device"], response_model=Page[Device], status_code=202)
async def stop_device(name: str):
    """Stops the device publication routine"""

    if not name in running_devices:
        raise HTTPException(status_code=403, detail= f"The device {name} is not running.")
    else:
        device = await get_device(name)
        producer = running_devices[device['name']]
        producer.stop = True
        producer.join()
        return await get_running_devices()

@v1.get("/api/v1/metadata/sample", tags=["Metadata"])
async def get_metadata_sample():
    """Gets the metadata sample"""
    try:
        with open('./samples/sample.json', 'r') as f:
            s = f.read()
            return json.loads(s)
    except:
        raise HTTPException(status_code=404, detail= f"No sample found.")

@v1.get("/api/v1/device/{name}/metadata", tags=["Metadata"])
async def get_metadata(name: str):
    """Gets the metadata of the device"""

    device = await get_device(name)
    metadata = table_templates.get(doc_id=device.doc_id)
    if metadata != None:
        return metadata
    else:
        raise HTTPException(status_code=404, detail= f"The device {name} does not have any metadata created.")

@v1.get("/api/v1/device/{name}/metadata/generate", tags=["Metadata"])
async def generate_from_metadata(name: str):
    """Gets the metadata of the device"""
    return generate(jsons.dump(await get_metadata(name)))

@v1.delete("/api/v1/device/{name}/metadata", tags=["Metadata"])
async def delete_metadata(name: str):
    """Deletes the metadata of the device"""

    metadata = await get_metadata(name)
    table_templates.remove(doc_ids=[metadata.doc_id])
    return table_templates.all()


add_pagination(v1)
