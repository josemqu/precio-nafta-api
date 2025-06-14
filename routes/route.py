from fastapi import APIRouter
from models.stations import Station
from config.database import collection_name
from schemas.schema import list_serial, individual_serial

router = APIRouter()

from typing import Optional, List
from fastapi import Query

@router.get("/stations", tags=["stations"], response_model=List[Station])
async def get_stations(
    province: Optional[str] = Query(None, description="Filtrar por provincia"),
    town: Optional[str] = Query(None, description="Filtrar por localidad"),
    flag: Optional[str] = Query(None, description="Filtrar por nombre de bandera (ej: YPF, Shell, Axion)"),
    flag_id: Optional[str] = Query(None, description="Filtrar por ID de bandera"),
    product: Optional[str] = Query(None, description="Filtrar por nombre de producto (ej: Nafta, GNC, Gasoil)"),
    product_id: Optional[str] = Query(None, description="Filtrar por ID de producto"),
    limit: int = Query(20, ge=1, le=100, description="Límite de resultados (máx. 100)")
):
    # Construir el filtro de consulta
    query_filter = {}
    
    # Filtros básicos
    if province:
        query_filter["province"] = {"$regex": province, "$options": "i"}  # Búsqueda case insensitive
    if town:
        query_filter["town"] = {"$regex": town, "$options": "i"}
    if flag:
        query_filter["flag"] = {"$regex": flag, "$options": "i"}
    if flag_id:
        query_filter["flagId"] = flag_id
    
    # Filtros de productos
    product_filters = {}
    if product:
        product_filters["products.productName"] = {"$regex": product, "$options": "i"}
    if product_id:
        product_filters["products.productId"] = product_id
    
    # Combinar filtros de productos con AND
    if product_filters:
        query_filter["$and"] = [product_filters]
    
    stations = collection_name.find(query_filter).limit(limit)
    return list_serial(stations)

@router.get("/stations/{stationId}", tags=["stations"], response_model=Station)
async def get_station(stationId: int):
    station = collection_name.find_one({"stationId": stationId})
    return individual_serial(station)

@router.get("/last-prices", tags=["last prices"], response_model=List[Station])
async def get_stations_last_prices(
    province: Optional[str] = Query(None, description="Filtrar por provincia"),
    town: Optional[str] = Query(None, description="Filtrar por localidad"),
    flag: Optional[str] = Query(None, description="Filtrar por nombre de bandera (ej: YPF, Shell, Axion)"),
    flag_id: Optional[str] = Query(None, description="Filtrar por ID de bandera"),
    product: Optional[str] = Query(None, description="Filtrar por nombre de producto (ej: Nafta, GNC, Gasoil)"),
    product_id: Optional[str] = Query(None, description="Filtrar por ID de producto"),
    limit: int = Query(20, ge=1, le=100, description="Límite de resultados (máx. 100)")
):
    try:
        # Construir el pipeline de agregación
        pipeline = []
        
        # Etapa de match con los filtros iniciales
        match_stage = {}
        
        # Filtros básicos
        if province:
            match_stage["province"] = {"$regex": province, "$options": "i"}
        if town:
            match_stage["town"] = {"$regex": town, "$options": "i"}
        if flag:
            match_stage["flag"] = {"$regex": flag, "$options": "i"}
        if flag_id:
            match_stage["flagId"] = flag_id
        
        # Añadir la etapa de match inicial si hay filtros
        if match_stage:
            pipeline.append({"$match": match_stage})
        
        # Descomponer los productos
        pipeline.append({"$unwind": "$products"})
        
        # Añadir filtros de productos si existen
        product_match = {}
        if product:
            product_match["products.productName"] = {"$regex": product, "$options": "i"}
        if product_id:
            product_match["products.productId"] = product_id
        
        if product_match:
            pipeline.append({"$match": product_match})
        
        # Obtener solo el precio más reciente para cada producto en cada estación
        pipeline.extend([
            # Primero, obtener el precio más reciente para cada producto
            {
                "$addFields": {
                    "products.prices": {
                        "$let": {
                            "vars": {
                                "sorted": {
                                    "$filter": {
                                        "input": {
                                            "$map": {
                                                "input": "$products.prices",
                                                "as": "price",
                                                "in": {
                                                    "$cond": [
                                                        {"$gt": ["$$price.date", None]},
                                                        "$$price",
                                                        None
                                                    ]
                                                }
                                            }
                                        },
                                        "as": "price",
                                        "cond": {"$ne": ["$$price", None]}
                                    }
                                }
                            },
                            "in": {
                                "$cond": [
                                    {"$gt": [{"$size": "$$sorted"}, 0]},
                                    [{"$arrayElemAt": ["$$sorted", -1]}],  # Tomar el más reciente
                                    []
                                ]
                            }
                        }
                    }
                }
            },
            
            # Filtrar productos que no tienen precios
            {"$match": {"products.prices.0": {"$exists": True}}},
            
            # Agrupar por estación y producto
            {
                "$group": {
                    "_id": {
                        "stationId": "$stationId",
                        "productId": "$products.productId"
                    },
                    "stationId": {"$first": "$stationId"},
                    "stationName": {"$first": "$stationName"},
                    "address": {"$first": "$address"},
                    "town": {"$first": "$town"},
                    "province": {"$first": "$province"},
                    "flag": {"$first": "$flag"},
                    "flagId": {"$first": "$flagId"},
                    "geometry": {"$first": "$geometry"},
                    "latestPrice": {"$first": {"$arrayElemAt": ["$products.prices", 0]}},
                    "productInfo": {
                        "$first": {
                            "productId": "$products.productId",
                            "productName": "$products.productName"
                        }
                    }
                }
            },
            
            # Reconstruir la estructura de productos con el precio más reciente
            {
                "$project": {
                    "_id": 0,
                    "stationId": 1,
                    "stationName": 1,
                    "address": 1,
                    "town": 1,
                    "province": 1,
                    "flag": 1,
                    "flagId": 1,
                    "geometry": 1,
                    "product": {
                        "productId": "$productInfo.productId",
                        "productName": "$productInfo.productName",
                        "prices": ["$latestPrice"]
                    }
                }
            },
            
            # Agrupar por estación para tener todos los productos juntos
            {
                "$group": {
                    "_id": "$stationId",
                    "stationId": {"$first": "$stationId"},
                    "stationName": {"$first": "$stationName"},
                    "address": {"$first": "$address"},
                    "town": {"$first": "$town"},
                    "province": {"$first": "$province"},
                    "flag": {"$first": "$flag"},
                    "flagId": {"$first": "$flagId"},
                    "geometry": {"$first": "$geometry"},
                    "products": {"$push": "$product"}
                }
            },
            
            # Ordenar por ID de estación para consistencia
            {"$sort": {"stationId": 1}},
            
            # Limitar los resultados
            {"$limit": limit}
        ])
        
        # Ejecutar la agregación con opciones de rendimiento
        cursor = collection_name.aggregate(
            pipeline,
            allowDiskUse=True,
            maxTimeMS=30000,  # 30 segundos de tiempo máximo
            batchSize=100     # Tamaño de lote para la paginación
        )
        
        return list_serial(cursor)
        
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al acceder a la base de datos: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )

from fastapi import HTTPException, status
from pymongo.errors import PyMongoError

@router.get("/last-prices/{stationId}", tags=["last prices"], response_model=Station)
async def get_station_last_prices(
    stationId: int,
    product: Optional[str] = Query(None, description="Filtrar por nombre de producto (ej: Nafta, GNC, Gasoil)"),
    product_id: Optional[str] = Query(None, description="Filtrar por ID de producto")
):
    try:
        # Construir el pipeline de agregación
        pipeline = [
            {
                "$match": {"stationId": stationId}
            }
        ]
        
        # Filtros de productos
        product_match = {}
        if product:
            product_match["products.productName"] = {"$regex": product, "$options": "i"}
        if product_id:
            product_match["products.productId"] = product_id
        
        # Si hay filtros de productos, añadirlos al match
        if product_match:
            if "$and" not in pipeline[0]["$match"]:
                pipeline[0]["$match"]["$and"] = []
            pipeline[0]["$match"]["$and"].append(product_match)
        
        # Etapa de descomponer los productos para poder ordenar los precios
        pipeline.extend([
            {"$unwind": "$products"},
            # Filtrar productos si es necesario
            {
                "$match": {
                    "products.prices": {"$exists": True, "$ne": []}
                }
            },
            # Ordenar los precios por fecha descendente (más reciente primero)
            {
                "$addFields": {
                    "products.prices": {
                        "$sortArray": {
                            "input": "$products.prices",
                            "sortBy": {"date": -1}  # Ordenar por fecha descendente
                        }
                    }
                }
            },
            # Tomar solo el precio más reciente
            {
                "$addFields": {
                    "products.prices": {"$slice": ["$products.prices", 1]}
                }
            },
            # Volver a agrupar por estación usando solo el stationId como _id
            {
                "$group": {
                    "_id": "$stationId",
                    "stationId": {"$first": "$stationId"},
                    "stationName": {"$first": "$stationName"},
                    "address": {"$first": "$address"},
                    "town": {"$first": "$town"},
                    "province": {"$first": "$province"},
                    "flag": {"$first": "$flag"},
                    "flagId": {"$first": "$flagId"},
                    "geometry": {"$first": "$geometry"},
                    "products": {"$push": "$products"}
                }
            },
            # Proyectar los campos finales
            {
                "$project": {
                    "stationId": 1,
                    "stationName": 1,
                    "address": 1,
                    "town": 1,
                    "province": 1,
                    "flag": 1,
                    "flagId": 1,
                    "geometry": 1,
                    "products": 1
                }
            }
        ])
        
        # Ejecutar la agregación
        result = list(collection_name.aggregate(pipeline))
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró la estación con ID {stationId} o no tiene productos que coincidan con los filtros"
            )
            
        return individual_serial(result[0])
        
    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al acceder a la base de datos: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}"
        )

