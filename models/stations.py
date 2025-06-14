from pydantic import BaseModel, Field
from typing import Optional, List, Any


class Geometry(BaseModel):
    type: str
    coordinates: List[float]


class Price(BaseModel):
    price: float
    date: Any


class Product(BaseModel):
    productId: int
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
