from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class Geometry(BaseModel):
    type: str
    coordinates: List[float]


class Price(BaseModel):
    price: float
    date: datetime


class Product(BaseModel):
    productId: int  # enum (2, 3, 6, 19, 21)
    productName: str
    prices: List[Price]


class Station(BaseModel):
    stationId: int
    stationName: str
    address: str
    town: str
    province: str
    flag: str
    flagId: int
    geometry: Geometry
    products: List[Product]
