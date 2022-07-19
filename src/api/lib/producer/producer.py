from datetime import datetime
import json
from kafka import KafkaProducer
import pika
from paho.mqtt import client as mqtt_client
from threading import Thread
import time
from lib.generate import generate
from lib.helpers.guid import guid
from models.models import Device, KafkaDestination, MqttDestination, RabbitMQDestination
import jsons

running_devices = {}

class Producer(Thread):

    def __init__(self, device:Device, metadata, publish_action):
        Thread.__init__(self)
        self.stop = False
        self.name = device['name']
        self.device = device
        self.metadata = jsons.dump(metadata)
        self.publish_action = publish_action

    def run(self):
        try:
            running_devices[self.name] = self
            loop = range(self.device['messages'])
            for m in loop:
                if not self.stop:
                    self.metadata[self.device['timestamp_label']] = str(datetime.utcnow())
                    template = generate(self.metadata)
                    self.publish_action(template)
                    print(template)
                    time.sleep(self.device['frequency_s'])
            print(f"Device {self.name} stopped.")
        except Exception as e:
            self.stop = True
            print(e)

class Kafka(Producer):
    def __init__(self, device:Device, destination, metadata):

        self.destination = destination
        self.producer = KafkaProducer(
        bootstrap_servers=f"{destination['server']}:{destination['port']}",
        value_serializer=lambda v: json.dumps(v).encode("utf-8"))
        super().__init__(device,metadata,self.publish)

    def publish(self, payload):
        self.producer.send(self.destination['topic'],payload)

class RabbitMQ(Producer):

    def __init__(self, device:Device, destination, metadata):

        self.destination = destination
        credentials = pika.PlainCredentials(destination['username'], destination['password'])
        parameters = pika.ConnectionParameters(destination['server'],destination['port'],'/',credentials)
        connection = pika.BlockingConnection(parameters)
        self.channel = connection.channel()
        if destination['queue'] != None:
            self.channel.queue_declare(queue=destination['queue'])
        super().__init__(device,metadata,self.publish)

    def publish(self, payload):
        self.channel.basic_publish(exchange=self.destination['exchange'],
                    routing_key=self.destination['routing_key'],
                    body=payload)


class MQTT(Producer):

    def __init__(self, device:Device, destination, metadata):

        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("Connected to MQTT Broker!")
            else:
                print("Failed to connect, return code %d\n", rc)

        self.destination = destination
        self.client = mqtt_client.Client(guid())
        if destination['username']!=None and destination['password']!=None:
            self.client.username_pw_set(destination['username'], destination['password'])
        self.client.on_connect = on_connect
        self.client.connect(destination['server'], destination['port'])
        super().__init__(device,metadata,self.publish)


    def publish(self, payload):
        result = self.client.publish(self.destination['topic'], payload)
        status = result[0]
        if status == 0:
            print(f"Send '{payload}' to topic '{self.destination['topic']}")
        else:
            print(f"Failed to send message to topic {self.destination['topic']}")