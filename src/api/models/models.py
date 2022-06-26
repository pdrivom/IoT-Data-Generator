from datetime import datetime
from re import template
from pydantic import BaseModel


class Device(BaseModel):

    name: str
    kafka_server:str
    kafka_topic:str
    frequency_s: int
    messages:int
    timestamp_label: str
    auto_start: bool


class Metadata(BaseModel):

    device_name: str
    template: str