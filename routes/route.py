"""
route.py

Route definitions for the API.

This module contains the route handlers for the API endpoints, including station queries and price lookups. Each route is documented with its purpose, parameters, and return values.
"""

from typing import Optional, List
from pymongo.errors import PyMongoError
from fastapi import HTTPException, status, Depends
from fastapi import Query
from fastapi import APIRouter
from models.stations import Station
from config.database import collection_name
from schemas.schema import list_serial, individual_serial
from auth import get_current_active_user

router = APIRouter()


@router.get("/stations", tags=["Stations"], response_model=List[Station])
async def get_stations(
    province: Optional[str] = Query(None, description="Filtrar por provincia"),
    town: Optional[str] = Query(None, description="Filtrar por localidad"),
    flag: Optional[str] = Query(
        None, description="Filtrar por nombre de bandera (ej: YPF, Shell, Axion)"
    ),
    flag_id: Optional[int] = Query(None, description="Filtrar por ID de bandera"),
    product: Optional[str] = Query(
        None, description="Filtrar por nombre de producto (ej: Nafta, GNC, Gasoil)"
    ),
    product_id: Optional[int] = Query(None, description="Filtrar por ID de producto"),
    limit: int = Query(20, ge=1, le=100, description="Límite de resultados (máx. 100)"),
    current_user: dict = Depends(get_current_active_user),
):
    """
    Retrieve a list of stations filtered by optional parameters.

    Parameters:
        province (str, optional): Filter by province name (case-insensitive).
        town (str, optional): Filter by town/locality name (case-insensitive).
        flag (str, optional): Filter by flag/brand name (e.g., YPF, Shell, Axion).
        flag_id (int, optional): Filter by flag/brand ID.
        product (str, optional): Filter by product name (e.g., Nafta, GNC, Gasoil).
        product_id (int, optional): Filter by product ID.
        limit (int): Maximum number of results to return (default: 20, max: 100).
        current_user (dict): The authenticated user (injected by dependency).

    Returns:
        List[Station]: A list of stations matching the filters.
    Raises:
        HTTPException: If there is a database error or unexpected error.
    """

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

        # Limitar la cantidad de estaciones antes de descomponer productos
        pipeline.append({"$limit": limit})

        # Descomponer los productos
        pipeline.append({"$unwind": "$products"})

        # Añadir filtros de productos si existen
        product_match = {}
        if product:
            product_match["products.productName"] = {"$regex": product, "$options": "i"}
        if product_id is not None:
            product_match["products.productId"] = product_id

        if product_match:
            pipeline.append({"$match": product_match})

        # Agrupar para mantener la estructura de la estación
        pipeline.append(
            {
                "$group": {
                    "_id": "$_id",
                    "stationId": {"$first": "$stationId"},
                    "stationName": {"$first": "$stationName"},
                    "address": {"$first": "$address"},
                    "town": {"$first": "$town"},
                    "province": {"$first": "$province"},
                    "flag": {"$first": "$flag"},
                    "flagId": {"$first": "$flagId"},
                    "geometry": {"$first": "$geometry"},
                    "products": {"$push": "$products"},
                }
            }
        )

        # Ejecutar la agregación
        cursor = collection_name.aggregate(
            pipeline,
            allowDiskUse=True,
            maxTimeMS=30000,
            batchSize=100,
        )

        return list_serial(cursor)

    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al acceder a la base de datos: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}",
        ) from e


@router.get("/stations/{station_id}", tags=["Stations"], response_model=Station)
async def get_station(
    station_id: int,
    product: Optional[str] = Query(
        None, description="Filtrar por nombre de producto (ej: Nafta, GNC, Gasoil)"
    ),
    product_id: Optional[int] = Query(None, description="Filtrar por ID de producto"),
    current_user: dict = Depends(get_current_active_user),
):
    """
    Retrieve a single station by its ID, with optional product filtering.

    Parameters:
        station_id (int): The unique ID of the station.
        product (str, optional): Filter by product name (e.g., Nafta, GNC, Gasoil).
        product_id (int, optional): Filter by product ID.
        current_user (dict): The authenticated user (injected by dependency).

    Returns:
        Station: The station matching the ID and filters.
    Raises:
        HTTPException: If the station is not found or a database/unexpected error occurs.
    """

    try:
        # Construir el pipeline de agregación
        pipeline = [
            # Filtrar por station_id
            {"$match": {"stationId": station_id}},
            # Descomponer los productos
            {"$unwind": "$products"},
        ]

        # Añadir filtros de productos si existen
        product_match = {}
        if product:
            product_match["products.productName"] = {"$regex": product, "$options": "i"}
        if product_id is not None:
            product_match["products.productId"] = product_id

        if product_match:
            pipeline.append({"$match": product_match})

        # Agrupar para mantener la estructura de la estación
        pipeline.extend(
            [
                {
                    "$group": {
                        "_id": "$_id",
                        "stationId": {"$first": "$stationId"},
                        "stationName": {"$first": "$stationName"},
                        "address": {"$first": "$address"},
                        "town": {"$first": "$town"},
                        "province": {"$first": "$province"},
                        "flag": {"$first": "$flag"},
                        "flagId": {"$first": "$flagId"},
                        "geometry": {"$first": "$geometry"},
                        "products": {"$push": "$products"},
                    }
                },
                {"$limit": 1},  # Solo debería haber un resultado
            ]
        )

        # Ejecutar la agregación
        result = list(collection_name.aggregate(pipeline))

        if not result:
            # Si no hay resultados, verificar si la estación existe sin filtros
            station = collection_name.find_one({"stationId": station_id})
            if not station:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Estación con ID {station_id} no encontrada",
                )

            # Si la estación existe pero no tiene productos que coincidan con los filtros
            if product or product_id is not None:
                station["products"] = []
                return individual_serial(station)

            return individual_serial(station)

        return individual_serial(result[0])

    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al acceder a la base de datos: {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {str(e)}",
        ) from e


@router.get("/last-prices", tags=["Last prices"], response_model=List[Station])
async def get_stations_last_prices(
    province: Optional[str] = Query(None, description="Filtrar por provincia"),
    town: Optional[str] = Query(None, description="Filtrar por localidad"),
    flag: Optional[str] = Query(
        None, description="Filtrar por nombre de bandera (ej: YPF, Shell, Axion)"
    ),
    flag_id: Optional[int] = Query(None, description="Filtrar por ID de bandera"),
    product: Optional[str] = Query(
        None, description="Filtrar por nombre de producto (ej: Nafta, GNC, Gasoil)"
    ),
    product_id: Optional[int] = Query(None, description="Filtrar por ID de producto"),
    limit: int = Query(20, ge=1, le=100, description="Límite de resultados (máx. 100)"),
    current_user: dict = Depends(get_current_active_user),
):
    """
    Retrieve the most recent prices for all stations filtered by optional parameters.

    Parameters:
        province (str, optional): Filter by province name.
        town (str, optional): Filter by town/locality name.
        flag (str, optional): Filter by flag/brand name.
        flag_id (int, optional): Filter by flag/brand ID.
        product (str, optional): Filter by product name.
        product_id (int, optional): Filter by product ID.
        limit (int): Maximum number of results to return (default: 20, max: 100).
        current_user (dict): The authenticated user (injected by dependency).

    Returns:
        List[Station]: A list of stations with their most recent prices.
    Raises:
        HTTPException: If there is a database error or unexpected error.
    """

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

        # Obtener solo el precio más reciente para cada producto en cada
        # estación
        pipeline.extend(
            [
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
                                                            None,
                                                        ]
                                                    },
                                                }
                                            },
                                            "as": "price",
                                            "cond": {"$ne": ["$$price", None]},
                                        }
                                    }
                                },
                                "in": {
                                    "$cond": [
                                        {"$gt": [{"$size": "$$sorted"}, 0]},
                                        [
                                            {"$arrayElemAt": ["$$sorted", -1]}
                                        ],  # Tomar el más reciente
                                        [],
                                    ]
                                },
                            }
                        }
                    }
                },
                # Filtrar productos que no tienen precios
                {"$match": {"products.prices.0": {"$exists": True}}},
                # Agrupar por estación y producto
                {
                    "$group": {
                        "_id": {"stationId": "$stationId", "productId": "$products.productId"},
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
                                "productName": "$products.productName",
                            }
                        },
                    }
                },
                # Reconstruir la estructura de productos con el precio más
                # reciente
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
                            "prices": ["$latestPrice"],
                        },
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
                        "products": {"$push": "$product"},
                    }
                },
                # Ordenar por ID de estación para consistencia
                {"$sort": {"stationId": 1}},
                # Limitar los resultados
                {"$limit": limit},
            ]
        )

        # Ejecutar la agregación con opciones de rendimiento
        cursor = collection_name.aggregate(
            pipeline,
            allowDiskUse=True,
            maxTimeMS=30000,  # 30 segundos de tiempo máximo
            batchSize=100,  # Tamaño de lote para la paginación
        )

        return list_serial(cursor)

    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al acceder a la base de datos: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {
                str(e)}",
        )


@router.get("/last-prices/{station_id}", tags=["Last prices"], response_model=Station)
async def get_station_last_prices(
    station_id: int,
    product: Optional[str] = Query(
        None, description="Filtrar por nombre de producto (ej: Nafta, GNC, Gasoil)"
    ),
    product_id: Optional[int] = Query(None, description="Filtrar por ID de producto"),
    current_user: dict = Depends(get_current_active_user),
):
    """
    Retrieve the most recent prices for a single station by station ID, with optional product filtering.

    Parameters:
        station_id (int): The unique ID of the station.
        product (str, optional): Filter by product name.
        product_id (int, optional): Filter by product ID.
        current_user (dict): The authenticated user (injected by dependency).

    Returns:
        Station: The station with its most recent product prices.
    Raises:
        HTTPException: If the station is not found or a database/unexpected error occurs.
    """

    try:
        # Construir el pipeline de agregación
        pipeline = [
            # Filtrar por station_id
            {"$match": {"stationId": station_id}},
            # Descomponer los productos
            {"$unwind": "$products"},
        ]

        # Añadir filtros de productos si existen
        product_match = {}
        if product:
            product_match["products.productName"] = {"$regex": product, "$options": "i"}
        if product_id is not None:
            product_match["products.productId"] = product_id

        if product_match:
            pipeline.append({"$match": product_match})

        # Etapa de descomponer los productos para poder ordenar los precios
        pipeline.extend(
            [
                {"$unwind": "$products"},
                # Filtrar productos si es necesario
                {"$match": {"products.prices": {"$exists": True, "$ne": []}}},
                # Ordenar los precios por fecha descendente (más reciente
                # primero)
                {
                    "$addFields": {
                        "products.prices": {
                            "$sortArray": {
                                "input": "$products.prices",
                                # Ordenar por fecha descendente
                                "sortBy": {"date": -1},
                            }
                        }
                    }
                },
                # Tomar solo el precio más reciente
                {"$addFields": {"products.prices": {"$slice": ["$products.prices", 1]}}},
                # Volver a agrupar por estación usando solo el stationId como
                # _id
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
                        "products": {"$push": "$products"},
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
                        "products": 1,
                    }
                },
            ]
        )

        # Ejecutar la agregación
        result = list(collection_name.aggregate(pipeline))

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró la estación con ID {station_id} o no tiene productos que coincidan con los filtros",
            )

        return individual_serial(result[0])

    except PyMongoError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al acceder a la base de datos: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error inesperado: {
                str(e)}",
        )
