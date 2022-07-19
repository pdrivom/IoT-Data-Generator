from pydantic import BaseModel


class Device(BaseModel):

    name: str
    frequency_s: int
    messages:int
    timestamp_label: str = 'timestamp'
    auto_start: bool
    data_destination: str

class DataDestination(BaseModel):
    name:str
    server:str
    port:int

class PubSubDestination(DataDestination):
    topic:str

class KafkaDestination(PubSubDestination):
    port:int = 9092

class RabbitMQDestination(DataDestination):
    exchange:str = ''
    routing_key:str
    queue:str = None
    port:int = 5672
    username:str = 'guest'
    password:str = 'guest'

class MqttDestination(PubSubDestination):
    port:int = 1883
    username:str = None
    password:str = None