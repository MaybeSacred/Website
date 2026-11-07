from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import Field


@dataclass
class ProvisioningDataDto:
    mac_address: str
    home_object_id: UUID


@dataclass
class UnprovisionedDevice:
    case: Literal['UNPROVISIONED']


@dataclass
class ProvisionedDevice:
    case: Literal['PROVISIONED']
    mac_address: str
    home_object_id: UUID


@dataclass
class Device:
    id: UUID
    name: str
    creation_date: datetime
    device_status: UnprovisionedDevice | ProvisionedDevice = Field(discriminator='case')
