# IoT JSON Data Generator API




This is a fork from [gtavasoli](https://github.com/gtavasoli)/**[JSON-Generator](https://github.com/gtavasoli/JSON-Generator)** with the objective of containerize his JSON Generator for IoT Data and access it using a API.

**This means that all JSON generated has a timestamp property, so can be simulated IoT *Devices* that published JSON data to a Kafka, RabbitMQ or MQTT Client.**


The **IoT Data Generator** a REST API where ***Devices*** can be created and then add it's metadata, allowing users to generate fake data based on a template.




## Usage


 On a Linux machine or WSL with **Docker installed**, navigate to a proper folder  than run the command below:

    wget https://raw.githubusercontent.com/pdrivom/IoT-Data-Generator/master/release/docker-compose.yml

After downloading the file, just run the command (on the same folder):

    docker-compose up

> If needed, edit the compose file in order to properly set the Docker networks.

In order to use the **API**, different endpoints are implemented and can be found on the **API documentation** `http://localhost:8000/docs`


> **The API can be tested using Postman or a Web Browser.**

## Example

### Data Destination

**`[POST] http://localhost:8000/api/v1/destination`**

`
{
    "name": "kafka-temperature",
    "server": "kafka",
    "port": 9092,
    "topic": "temperature"
}
`

### Device

**`[POST] http://localhost:8000/api/v1/device`**

`
{
    "name": "temperature-sensor",
    "frequency_s": 1,
    "messages": 100,
    "timestamp_label": "date",
    "auto_start": true,
    "data_destination":"kafka-temperature"
}
`

- `frequency_s` sets the frequency for the publish of messages in seconds,
- `messages` is number of messages published until the device stops,
- `timestamp_label` sets the name of the property that contains the timestamp (`datetime.utcnow()`),
- `auto_start = true` , the device will start publishing as soon as the container starts. Needs to be started after added.
- `data_destination` , the data destination to publishing the messages.

### Metadata
**`[POST] http://localhost:8000/api/v1/temperature-sensor/metadata`**

`
{
  "_id": "{{object_id()}}",
  "temperature": "{{integer(-180, 180)}}"
}
`

### Start/Stop
 >To start device `temperature-sensor` to publish messages.

**`[PUT]  http://localhost:8000/api/v1/device/temperature-sensor/start`**

>To stop device `temperature-sensor` from publishing messages.

**`[PUT]  http://localhost:8000/api/v1/device/temperature-sensor/stop`**


### Start/Stop All

 >To start all devices to publish messages:
 >
**`[PUT]  http://localhost:8000/api/v1/devices/start`**

 >To stop all devices from publishing messages:

**`[PUT]  http://localhost:8000/api/v1/devices/stop`**

## Template

A more extended template can be found calling the **API** endpoint `[GET] http://localhost:8000/api/v1/metadata/sample`.

    {
	"_id": "{{object_id()}}",
	"name": "{{name()}}",
	"guid": "{{guid()}}",
	"isActive": "{{bool()}}",
	"eyeColor": "{{choice([\"blue\", \"brown\", \"green\"])}}",
	"balance": "{{floating(1000, 4000, 2)}}",
	"picture": "http://placehold.it/32x32",
	"age": "{{integer(20, 30)}}",
	"city": "{{city()}}",
	"state": "{{state()}}",
	"gender": "{{gender()}}",
	"company": "{{company().upper()}}",
	"email": "{{email()}}",
	"phone": "{{phone()}}",
	"latitude": "{{floating(-90.000001, 90)}}",
	"longitude": "{{floating(-180.000001, 180)}}"
	}


## ToDo

- Better Unit Tests


## Developer's Notes

To Run API in development:
`
docker-compose -f docker-compose.yml run --rm --service-ports api sh -c "uvicorn api:v1 --host 0.0.0.0 --port 8000 --reload"
`

To Run API Tests in development:
`
docker-compose -f docker-compose.yml run --rm api sh -c "pytest"
`
