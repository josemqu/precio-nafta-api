"""
stations.py

Defines Pydantic models for geometry, price, product, and station entities used in the API.
"""

from datetime import datetime  # Standard library
from typing import List
from pydantic import BaseModel  # Third-party


class Geometry(BaseModel):
    """
    Represents a GeoJSON geometry object with a type and coordinates.

    Attributes:
        type (str): The geometry type (e.g., 'Point').
        coordinates (List[float]): The coordinates of the geometry.
    """
    type: str
    coordinates: List[float]


class Price(BaseModel):
    """
    Represents a price entry for a product at a specific date.

    Attributes:
        price (float): The price value.
        date (datetime): The date and time the price was recorded.
    """
    price: float
    date: datetime


class Product(BaseModel):
    """
    Represents a fuel product offered at a station.

    Attributes:
        productId (int): The product's unique ID (e.g., 2, 3, 6, 19, 21).
        productName (str): The name of the product (e.g., Nafta, GNC).
        prices (List[Price]): A list of price entries for this product.
    """
    productId: int  # enum (2, 3, 6, 19, 21)
    productName: str
    prices: List[Price]


class Station(BaseModel):
    """
    Represents a fuel station and its main identifying information.

    Attributes:
        stationId (int): The station's unique ID.
        stationName (str): The name of the station.
        address (str): The address of the station.
        town (str): The town or locality where the station is located.
        province (str): The province where the station is located.
    """
    stationId: int
    stationName: str
    address: str
    town: str
    province: str
    flag: str
    flagId: int
    geometry: Geometry
    products: List[Product]
