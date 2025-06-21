"""
schema.py

Contains serialization functions to convert MongoDB documents into API-friendly formats.
"""

def individual_serial(station) -> dict:
    """
    Convert a single station document from MongoDB into a serialized dictionary.

    This function handles the conversion of MongoDB's ObjectId to string and
    structures the station data in a consistent format for API responses.

    Args:
        station (dict): A MongoDB document representing a fuel station.

    Returns:
        dict: A dictionary with the station data in a serialized format, including:
            - Basic station info (id, name, address, etc.)
            - Geometry data (type and coordinates)
            - List of products with their prices
            - Additional metadata (updatedAt, __v)
    """
    return {
        "id": str(station["_id"]),
        "stationId": station["stationId"],
        "stationName": station["stationName"],
        "address": station["address"],
        "town": station["town"],
        "province": station["province"],
        "flag": station["flag"],
        "flagId": station["flagId"],
        "geometry": {
            "type": station["geometry"]["type"],
            "coordinates": station["geometry"]["coordinates"],
        },
        "products": [
            {
                "productId": product["productId"],
                "productName": product["productName"],
                "prices": [
                    {
                        "price": price["price"],
                        "date": price["date"],
                        "_id": str(price["_id"]) if "_id" in price else None,
                    }
                    for price in product["prices"]
                ],
                "_id": str(product["_id"]) if "_id" in product else None,
            }
            for product in station["products"]
        ],
        "updatedAt": station.get("updatedAt"),
        "__v": station.get("__v"),
    }


def list_serial(stations) -> list:
    """
    Convert a list of station documents into a list of serialized station dictionaries.

    Args:
        stations (list): A list of MongoDB documents, each representing a fuel station.

    Returns:
        list: A list of serialized station dictionaries.
    """
    return [individual_serial(station) for station in stations]
