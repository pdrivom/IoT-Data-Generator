


# IoT JSON Data Generator API




This is a fork from [gtavasoli](https://github.com/gtavasoli)/**[JSON-Generator](https://github.com/gtavasoli/JSON-Generator)** with the objective of containerize his JSON Generator for IoT Data and access it using a API.

**This means that all JSON generated has a timestamp property, so can be simulated IoT *Devices* that published JSON data to a Kafka Cluster and in the future to a RabbitMQ Cluster.**


The **IoT Data Generator** a REST API where ***Devices*** can be created and then add it's metadata, allowing users to generate fake data based on a template.





## Usage


 On a Linux machine or WSL with **Docker installed**, navigate to a proper folder  than run the command below:

    https://raw.githubusercontent.com/pdrivom/IoT-Data-Generator/master/release/docker-compose.yml

After downloading the file, just run the command (on the same folder):

    docker-compose up

This compose file contains the **API and the Kafka Cluster** containers if you want to deploy **on a existing environment** use the file below:

	version: '3'

	services:
		api:
			hostname: iot-data-generator-api
			image: pdrivom/iot-data-generator:latest
			external_links:
			  - <SERVICE:ALIAS>	#Your Kafka Service
			ports:
				- 8000:8000
			volumes:
				- iot-data-generator:/usr/src/api
			networks:
				- api
				- <kafka>  # your Kafka Network

			volumes:
			# mount volume in order to keep the data persistent
				iot-data-generator:

			networks:
				<kafka>: 		# your Kafka Network
					external:true
				api:
					driver: bridge


In order to use the **API**, different endpoints are implemented and can be found on the **API documentation** `http://localhost:8000/docs`


> **The API can be tested using Postman or a Web Browser.**

## Example
### Device

**`[POST] http://localhost:8000/api/v1/device`**

`
	{
	"name": "gps",
	"kafka_server": "kafka:9092",
	"kafka_topic": "location",
	"frequency_s": 1,
	"messages": 100,
	"timestamp_label": "datetime",
	"auto_start": true
	}
`


- `kafka_server` is the Kafka bootstrap-server,
- `frequency_s` sets the frequency for the publish of messages in seconds,
- `messages` is number of messages published until the device stops,
- `timestamp_label` sets the name of the property that contains the timestamp (`datetime.utcnow()`),
- `auto_start = true` , the device will start publishing as soon as the container starts.

### Metadata
**`[POST] http://localhost:8000/api/v1/gps/metadata`**

`
	{
	"_id": "{{object_id()}}",
	"latitude": "{{floating(-90.000001, 90)}}",
	"longitude": "{{floating(-180.000001, 180)}}"
	}
`

### Start/Stop
 >To start device `gps` to publish messages.

**`[PUT]  http://localhost:8000/api/v1/device/gps/start`**

>To stop device `gps` from publishing messages.

**`[PUT]  http://localhost:8000/api/v1/device/gps/stop`**


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
- Add RabbitMQ compatibility
