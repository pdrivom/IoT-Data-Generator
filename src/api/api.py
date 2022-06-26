from importlib.metadata import metadata
from fastapi import FastAPI, HTTPException, Request
from fastapi_pagination import Page, add_pagination, paginate
import json
from tinydb import TinyDB, Query
from tinydb.table import Document
from models.models import Device
from models.models import Metadata





db = TinyDB('./database/devices.json')
table_devices = db.table('devices')
table_templates = db.table('metadata')
devices = Query()
templates = Query()
app = FastAPI()


@app.get("/api/v1/devices", response_model=Page[Device])
async def get_devices(page: int = 1, size: int = 50):
    """Gets all saved devices"""
    return paginate(table_devices.all())

@app.post("/api/v1/device", response_model=Device, status_code=201)
async def add_device(device: Device):
    """Saves a device"""

    exists = table_devices.get(devices.name == device.name)
    if exists == None:
        table_devices.insert(device.dict())
        return table_devices.get(devices.name == device.name)
    else:
        raise HTTPException(status_code=409, detail= f"The device {device.name} already exists")

@app.get("/api/v1/device/{name}", response_model=Device)
async def get_device(name: str):
    """Gets saved device by name"""

    device = table_devices.get(devices.name == name)
    if device != None:
        return device
    else:
        raise HTTPException(status_code=404, detail= f"The device {name} does not exists")

@app.put("/api/v1/device", response_model=Device)
async def update_device(device: Device):
    """Updates a device"""

    exists = table_devices.get(devices.name == device.name)
    if exists != None:
        table_devices.update(device.dict(), doc_ids=[exists.doc_id])
        return table_devices.get(devices.name == device.name)
    else:
        return await add_device(device)

@app.delete("/api/v1/device/{name}", response_model=Page[Device])
async def delete_device(name: str):
    """Deletes a device"""

    device = await get_device(name)
    table_devices.remove(doc_ids=[device.doc_id])
    return paginate(table_devices.all())

@app.put("/api/v1/device/{name}/metadata", status_code=201)
async def add_metadata(name: str, request: Request):
    """Saves the metadata of the device"""

    device = await get_device(name)
    template = await request.json()
    metadata = table_templates.get(doc_id=device.doc_id)
    if metadata != None:
        await delete_metadata(name)
    table_templates.insert(Document(template, device.doc_id))
    return table_templates.get(doc_id=device.doc_id)

@app.get("/api/v1/device/{name}/metadata")
async def get_metadata(name: str):
    """Gets the metadata of the device"""

    device = await get_device(name)
    metadata = table_templates.get(doc_id=device.doc_id)
    if metadata != None:
        return metadata
    else:
        raise HTTPException(status_code=404, detail= f"The device {name} does not have any metadata created.")

@app.delete("/api/v1/device/{name}/metadata")
async def delete_metadata(name: str):
    """Deletes the metadata of the device"""

    device = await get_device(name)
    metadata = await get_metadata(name)
    table_templates.remove(doc_ids=[metadata.doc_id])
    return table_templates.all()

add_pagination(app)
