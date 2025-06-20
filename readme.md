# Documentación de la API de Precios de Nafta

API desarrollada con FastAPI para consultar estaciones de servicio, productos y precios de combustibles en Argentina.

## Endpoints

---

### 1. Obtener listado de estaciones

- **Método:** `GET`
- **Ruta:** `/stations`
- **Descripción:** Devuelve un listado de estaciones de servicio, pudiendo filtrar por provincia, localidad, bandera y producto.
- **Parámetros Query:**
  - `province` (str, opcional): Filtrar por provincia
  - `town` (str, opcional): Filtrar por localidad
  - `flag` (str, opcional): Filtrar por nombre de bandera (ej: YPF, Shell, Axion)
  - `flag_id` (int, opcional): Filtrar por ID de bandera
  - `product` (str, opcional): Filtrar por nombre de producto (ej: Nafta, GNC, Gasoil)
  - `product_id` (int, opcional): Filtrar por ID de producto
  - `limit` (int, opcional, default=20, max=100): Límite de resultados
- **Respuesta:** `List[Station]`

**Ejemplo:**
```http
GET /stations?province=Buenos Aires&flag=YPF&limit=10
```

---

### 2. Obtener detalle de una estación

- **Método:** `GET`
- **Ruta:** `/stations/{station_id}`
- **Descripción:** Devuelve el detalle de una estación de servicio y sus productos.
- **Parámetros Path:**
  - `station_id` (int, requerido): ID de la estación
- **Parámetros Query:**
  - `product` (str, opcional): Filtrar por nombre de producto
  - `product_id` (int, opcional): Filtrar por ID de producto
- **Respuesta:** `Station`

**Ejemplo:**
```http
GET /stations/1234?product=Nafta
```

---

### 3. Obtener listado de estaciones con precios más recientes

- **Método:** `GET`
- **Ruta:** `/last-prices`
- **Descripción:** Devuelve un listado de estaciones con los precios más recientes para cada producto.
- **Parámetros Query:**
  - `province` (str, opcional): Filtrar por provincia
  - `town` (str, opcional): Filtrar por localidad
  - `flag` (str, opcional): Filtrar por nombre de bandera
  - `flag_id` (int, opcional): Filtrar por ID de bandera
  - `product` (str, opcional): Filtrar por nombre de producto
  - `product_id` (int, opcional): Filtrar por ID de producto
  - `limit` (int, opcional, default=20, max=100): Límite de resultados
- **Respuesta:** `List[Station]`

**Ejemplo:**
```http
GET /last-prices?province=Córdoba&product=GNC
```

---

### 4. Obtener precios más recientes de una estación

- **Método:** `GET`
- **Ruta:** `/last-prices/{station_id}`
- **Descripción:** Devuelve los precios más recientes de una estación de servicio para cada producto.
- **Parámetros Path:**
  - `station_id` (int, requerido): ID de la estación
- **Parámetros Query:**
  - `product` (str, opcional): Filtrar por nombre de producto
  - `product_id` (int, opcional): Filtrar por ID de producto
- **Respuesta:** `Station`

**Ejemplo:**
```http
GET /last-prices/1234?product=Gasoil
```

---

## Modelos de Respuesta

### Station
- `stationId` (int): ID de la estación
- `stationName` (str): Nombre de la estación
- `address` (str): Dirección
- `town` (str): Localidad
- `province` (str): Provincia
- `flag` (str): Nombre de la bandera
- `flagId` (int): ID de la bandera
- `geometry` (dict): Información geográfica (lat/lon)
- `products` (list): Lista de productos con precios

### Product (dentro de Station)
- `productId` (int): ID del producto
- `productName` (str): Nombre del producto
- `prices` (list): Lista de precios (histórico)

### Price (dentro de Product)
- `date` (datetime): Fecha del precio
- `price` (float): Valor del precio

## Errores comunes
- `404 NOT FOUND`: No se encontró la estación o no hay productos que coincidan con los filtros.
- `500 INTERNAL SERVER ERROR`: Error inesperado o problema de conexión con la base de datos.

---

## Notas
- Todos los endpoints devuelven datos en formato JSON.
- No requiere autenticación.
- Los filtros son opcionales salvo que se indique lo contrario.

---

¿Dudas o sugerencias? Contactar al desarrollador.
