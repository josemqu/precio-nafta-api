from typing import List, Literal, Optional, Dict, Any
from pydantic import BaseModel, Field, conlist
from datetime import datetime

class Price(BaseModel):
    price: float
    date: str
    _id: Optional[str] = None

class Product(BaseModel):
    productId: str
    productName: str
    prices: List[Price] = []
    _id: Optional[str] = None

class Geometry(BaseModel):
    type: Literal["Point"] = "Point"  # Asumiendo que siempre es un punto
    coordinates: conlist(float, min_length=2, max_length=2)  # [longitud, latitud]

class Station(BaseModel):
    id: Optional[str] = Field(alias="_id", default=None)
    stationId: str
    stationName: str
    address: str
    town: str
    province: str
    flag: str
    flagId: str
    geometry: Geometry
    products: List[Product] = []
    updatedAt: Optional[datetime] = None
    __v: Optional[int] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True

def individual_serial(station: Dict[str, Any]) -> Dict[str, Any]:
    """Convierte un documento de MongoDB a un diccionario Python."""
    if not station:
        return {}
    
    # Asegurarse de que los campos requeridos estén presentes
    station_data = {
        **station,
        "_id": str(station.get("_id", "")),
        "geometry": {
            "type": station.get("geometry", {}).get("type", "Point"),
            "coordinates": station.get("geometry", {}).get("coordinates", [0.0, 0.0])
        },
        "products": [
            {
                **product,
                "_id": str(product.get("_id", "")),
                "prices": [
                    {
                        **price,
                        "_id": str(price.get("_id", "")) if "_id" in price else None
                    }
                    for price in product.get("prices", [])
                ]
            }
            for product in station.get("products", [])
        ]
    }
    
    return Station(**station_data).model_dump(exclude_none=True, by_alias=True)

def list_serial(stations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convierte una lista de documentos de MongoDB a una lista de diccionarios."""
    return [individual_serial(station) for station in stations] if stations else []
