def individual_serial(station) -> dict:
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
    return [individual_serial(station) for station in stations]
