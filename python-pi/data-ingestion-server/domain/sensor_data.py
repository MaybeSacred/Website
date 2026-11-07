from typing import Literal
from datetime import datetime
from pydantic import Field
from uuid import UUID
from dataclasses import dataclass

@dataclass
class HeartbeatDataDto:
    case: Literal['HEARTBEAT']
    mac_address: str
    ip_address: str
    source_date: datetime | int

@dataclass
class EnvironmentSensorDataDto:
    case: Literal['ENVIRONMENT_SENSOR']
    mac_address: str
    source_date: datetime | int
    # celsius
    cpu_temperature: float | None = None
    # celsius
    temperature: float | None = None
    # centimeters
    distance: float | None = None
    # percentage
    humidity: float | None = None
    # lumens?
    lux: float | None = None
    # hPa
    pressure: float | None = None

    uv: int | None = None
    gas: float | None = None
    # centimeters
    water_depth_raw: int | None = None
    # percentage
    moisture_percent: float | None = None
    #temperatureRaw: int

@dataclass
class Envelope:
    id: UUID
    date: datetime
    data: EnvironmentSensorDataDto | HeartbeatDataDto = Field(discriminator='case')