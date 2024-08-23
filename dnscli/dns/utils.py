from dataclasses import dataclass
from dateutil import parser

@dataclass
class Domain:
    domain_name: str
    create_time: float
    record_count: int

@dataclass
class Record:
    sub_domain: str
    type: str
    value: str
    line: str
    ttl: int
    record_id: str
    create_timestamp: float
    update_timestamp: float

def date_to_timestamp(date_time_str: str) -> float:
    date_time = parser.parse(date_time_str)
    return date_time.timestamp()



