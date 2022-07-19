import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi_pagination import Page, add_pagination, paginate
import jsons
import json
from tinydb import TinyDB, Query
from tinydb.table import Document
from models.models import Device, KafkaDestination, RabbitMQDestination, MqttDestination
from lib.generate import generate
from lib.producer.producer import Kafka, RabbitMQ, MQTT, running_devices



db = TinyDB('./database/devices.json')
table_destinations = db.table('destinations')
table_devices = db.table('devices')
table_templates = db.table('metadata')
devices = Query()
destinations = Query()
templates = Query()
v1 = FastAPI()

logger = logging.getLogger("v1")



@v1.on_event("startup")
async def startup():
    autostart = table_devices.search(devices.auto_start == True)
    for device in autostart:
        try:
            await __start_device(device['name'])
        except Exception as e:
            logger.error(e)


@v1.on_event("shutdown")
async def shutdown():
    for device in running_devices.copy():
        await __stop_device(device)

#region Data Destination

@v1.get("/api/v1/destinations", tags=["Data Destinations"], response_model=Page)
async def get_destinations(page: int = 1, size: int = 50):
    """Gets all saved destinations"""
    return paginate(table_destinations.all())

@v1.delete("/api/v1/destinations", tags=["Data Destinations"])
async def delete_destinations():
    """Delete all devices and metadata"""
    db.drop_table('destinations')
    return table_destinations.all()

@v1.get("/api/v1/destination/{name}", tags=["Data Destination"])
async def get_destination(name: str):
    """Gets saved destination by name"""

    destination = table_destinations.get(destinations.name == name)
    if destination != None:
        return destination
    else:
        raise HTTPException(status_code=404, detail= f"The data destination '{name}' does not exists")

@v1.delete("/api/v1/destination/{name}", tags=["Data Destination"])
async def delete_destination(name: str):
    """Deletes a destination"""

    device = await get_destination(name)
    table_destinations.remove(doc_ids=[device.doc_id])
    return table_destinations.all()


#region Kafka
@v1.post("/api/v1/destination/kafka", tags=["Data Destination","Kafka"], response_model=KafkaDestination, status_code=201)
async def add_kafka_destination(destination: KafkaDestination):
    """Saves a kafka data destination"""

    exists = table_destinations.get(destinations.name == destination.name)
    if exists == None:
        kafka = destination.dict()
        kafka['type'] = 'kafka'
        table_destinations.insert(kafka)
        return table_destinations.get(devices.name == destination.name)
    else:
        raise HTTPException(status_code=409, detail= f"The data destination with name '{destination.name}' already exists")


@v1.put("/api/v1/destination/kafka", tags=["Data Destination", "Kafka"], response_model=KafkaDestination)
async def update_kafka_destination(destination: KafkaDestination):
    """Updates a kafka data destination"""

    exists = table_destinations.get(destinations.name == destination.name)
    if exists != None:
        table_destinations.update(destination.dict(), doc_ids=[exists.doc_id])
        return table_destinations.get(destinations.name == destination.name)
    else:
        return await add_kafka_destination(destination)

#endregion

#region RabbitMQ
@v1.post("/api/v1/destination/rabbitmq", tags=["Data Destination","RabbitMQ"], response_model=RabbitMQDestination, status_code=201)
async def add_rabbitmq_destination(destination: RabbitMQDestination):
    """Saves a rabbitmq data destination"""

    exists = table_destinations.get(destinations.name == destination.name)
    if exists == None:
        rabbitmq = destination.dict()
        rabbitmq['type'] = 'rabbitmq'
        table_destinations.insert(rabbitmq)
        return table_destinations.get(devices.name == destination.name)
    else:
        raise HTTPException(status_code=409, detail= f"The data destination with name '{destination.name}' already exists")


@v1.put("/api/v1/destination/rabbitmq", tags=["Data Destination", "RabbitMQ"], response_model=RabbitMQDestination)
async def update_rabbitmq_destination(destination: RabbitMQDestination):
    """Updates a rabbitmq data destination"""

    exists = table_destinations.get(destinations.name == destination.name)
    if exists != None:
        table_destinations.update(destination.dict(), doc_ids=[exists.doc_id])
        return table_destinations.get(destinations.name == destination.name)
    else:
        return await add_rabbitmq_destination(destination)

#endregion

#region MQTT
@v1.post("/api/v1/destination/mqtt", tags=["Data Destination","MQTT"], response_model=MqttDestination, status_code=201)
async def add_mqtt_destination(destination: MqttDestination):
    """Saves a mqtt data destination"""

    exists = table_destinations.get(destinations.name == destination.name)
    if exists == None:
        mqtt = destination.dict()
        mqtt['type'] = 'mqtt'
        table_destinations.insert(mqtt)
        return table_destinations.get(devices.name == destination.name)
    else:
        raise HTTPException(status_code=409, detail= f"The data destination with name '{destination.name}' already exists")


@v1.put("/api/v1/destination/mqtt", tags=["Data Destination", "MQTT"], response_model=MqttDestination)
async def update_mqtt_destination(destination: MqttDestination):
    """Updates a mqtt data destination"""

    exists = table_destinations.get(destinations.name == destination.name)
    if exists != None:
        table_destinations.update(destination.dict(), doc_ids=[exists.doc_id])
        return table_destinations.get(destinations.name == destination.name)
    else:
        return await add_mqtt_destination(destination)

#endregion

#endregion

#region Devices
@v1.get("/api/v1/devices", tags=["Devices"], response_model=Page[Device])
async def get_devices(page: int = 1, size: int = 50):
    """Gets all saved devices"""
    return paginate(table_devices.all())

@v1.delete("/api/v1/devices", tags=["Devices"])
async def delete_devices():
    """Delete all devices and metadata"""
    db.drop_table('metadata')
    db.drop_table('devices')
    return table_devices.all()

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
        if table_destinations.get(destinations.name == device.data_destination) != None:
            table_devices.insert(device.dict())
            return table_devices.get(devices.name == device.name)
        else:
            raise HTTPException(status_code=404, detail= f"The data destination {device.name} does not exists.")
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
        if table_destinations.get(destinations.name == device.data_destination) != None:
            table_devices.update(device.dict(), doc_ids=[exists.doc_id])
            return table_devices.get(devices.name == device.name)
        else:
            raise HTTPException(status_code=404, detail= f"The data destination {device.name} does not exists.")
    else:
        return await add_device(device)

@v1.delete("/api/v1/device/{name}", tags=["Device"])
async def delete_device(name: str):
    """Deletes a device"""

    device = await get_device(name)
    table_devices.remove(doc_ids=[device.doc_id])
    return table_devices.all()

@v1.put("/api/v1/device/{name}/metadata",tags=["Metadata"], status_code=201)
async def add_metadata(name: str, template: dict):
    """Saves the metadata of the device"""

    device = await get_device(name)
    #template = await request.json()
    metadata = table_templates.get(doc_id=device.doc_id)
    if metadata != None:
        await delete_metadata(name)
    table_templates.insert(Document(template, device.doc_id))
    return table_templates.get(doc_id=device.doc_id)

async def __start_device(name: str):
    if name in running_devices:
        raise HTTPException(status_code=403, detail= f"The device {name} is already running.")
    else:
        device = await get_device(name)
        metadata = await get_metadata(name)
        destination = await get_destination(device['data_destination'])
        if destination['type'] == 'kafka':
            producer = Kafka(device, destination, metadata)
        elif destination['type'] == 'rabbitmq':
            producer = RabbitMQ(device, destination, metadata)
        elif destination['type'] == 'mqtt':
            producer = MQTT(device, destination, metadata)
        producer.start()

@v1.put("/api/v1/device/{name}/start", tags=["Device"], response_model=Device, status_code=202)
async def start_device(name: str):
    """Starts the device publication routine"""

    await __start_device(name)
    return await get_device(name)

async def __stop_device(name: str):
        device = await get_device(name)
        producer = running_devices[device['name']]
        producer.stop = True
        producer.join()
        running_devices.pop(device['name'])


@v1.put("/api/v1/device/{name}/stop", tags=["Device"], response_model=Page[Device], status_code=202)
async def stop_device(name: str):
    """Stops the device publication routine"""

    if not name in running_devices:
        raise HTTPException(status_code=403, detail= f"The device {name} is not running.")
    else:
        await __stop_device(name)
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

#endregion

add_pagination(v1)
