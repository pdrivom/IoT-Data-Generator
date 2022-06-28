from datetime import datetime
import json
from kafka import KafkaProducer
from threading import Thread
from time import sleep
from lib.generate import generate
import jsons

running_devices = {}

class Producer(Thread):

    def __init__(self, device, metadata):
        Thread.__init__(self)
        self.stop = False
        self.name = device['name']
        self.device = device
        self.metadata = jsons.dump(metadata)
        self.producer = KafkaProducer(
                bootstrap_servers=device['kafka_server'],
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )

    def run(self):
        try:
            running_devices[self.name] = self
            loop = range(self.device['messages'])
            for m in loop:
                if not self.stop:
                    self.metadata[self.device['timestamp_label']] = str(datetime.utcnow())
                    template = generate(self.metadata)
                    print(template)
                    self.producer.send(self.device['kafka_topic'],template)
                    sleep(self.device['frequency_s'])
            running_devices.pop(self.name)
            print(f"Device {self.name} stopped.")
        except Exception as e:
            self.stop = True
            print(e)