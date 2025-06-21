# 🚀 Precio Nafta API

API RESTful desarrollada con FastAPI para consultar estaciones de servicio, productos y precios de combustibles en Argentina.

## Características

- Consulta de estaciones de servicio por ubicación y bandera
- Precios actualizados de combustibles
- Autenticación JWT
- Documentación interactiva con Swagger UI
- Versionado de API (v1)
- Filtros avanzados por provincia, localidad y tipo de combustible

## Requisitos Previos

- Python 3.8+
- MongoDB
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio:

   ```bash
   git clone https://github.com/tu-usuario/precio-nafta-api.git
   cd precio-nafta-api
   ```

2. Crear y activar un entorno virtual:

   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

4. Configurar variables de entorno:

   Crear un archivo `.env` en la raíz del proyecto con las siguientes variables:

   ```env
   DB_USER=tu_usuario
   DB_PASS=tu_contraseña
   DB_HOST=tu_host_mongodb
   DB_NAME=precio_nafta
   SECRET_KEY=tu_clave_secreta_jwt
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. Iniciar el servidor:

   ```bash
   uvicorn main:app --reload
   ```

La API estará disponible en `http://localhost:8000`

## Documentación Interactiva

- **Swagger UI:** `http://localhost:8000/api/v1/docs`
- **ReDoc:** `http://localhost:8000/api/v1/redoc`

---

## 📚 Documentación de la API v1

Todas las rutas de la API están prefijadas con `/api/v1`

### 🔐 Autenticación

La mayoría de los endpoints requieren autenticación mediante JWT. Para autenticarse:

1. Obtén un token de acceso con tus credenciales:

   ```http
   POST /api/v1/token
   Content-Type: application/x-www-form-urlencoded
   
   username=tu_usuario&password=tu_contraseña
   ```

2. Usa el token en las cabeceras de las peticiones:

   ```http
   Authorization: Bearer <tu_token>
   ```

---

### 1. Obtener listado de estaciones

- **Método:** `GET`
- **Ruta:** `/api/v1/stations`
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
GET /api/v1/stations?province=Buenos%20Aires&flag=YPF&limit=10
```

---

### 2. Obtener detalle de una estación

- **Método:** `GET`
- **Ruta:** `/api/v1/stations/{station_id}`
- **Descripción:** Devuelve el detalle de una estación de servicio y sus productos.
- **Parámetros Path:**
  - `station_id` (int, requerido): ID de la estación
- **Parámetros Query:**
  - `product` (str, opcional): Filtrar por nombre de producto
  - `product_id` (int, opcional): Filtrar por ID de producto
- **Respuesta:** `Station`

**Ejemplo:**
```http
GET /api/v1/stations/1234?product=Nafta
```

---

### 3. Obtener listado de estaciones con precios más recientes

- **Método:** `GET`
- **Ruta:** `/api/v1/last-prices`
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
GET /api/v1/last-prices?province=Córdoba&product=GNC
```

---

### 4. Obtener precios más recientes de una estación

- **Método:** `GET`
- **Ruta:** `/api/v1/last-prices/{station_id}`
- **Descripción:** Devuelve los precios más recientes de una estación de servicio para cada producto.
- **Parámetros Path:**
  - `station_id` (int, requerido): ID de la estación
- **Parámetros Query:**
  - `product` (str, opcional): Filtrar por nombre de producto
  - `product_id` (int, opcional): Filtrar por ID de producto
- **Respuesta:** `Station`

**Ejemplo:**
```http
GET /api/v1/last-prices/1234?product=Gasoil
```

---

## Modelos de Respuesta

### Station

Modelo que representa una estación de servicio.
- `stationId` (int): ID de la estación
- `stationName` (str): Nombre de la estación
- `address` (str): Dirección
- `town` (str): Localidad
- `province` (str): Provincia
- `flag` (str): Nombre de la bandera
- `flagId` (int): ID de la bandera
- `geometry` (dict): Información geográfica (lat/lon)
- `products` (list): Lista de productos

### Geometry

Modelo que representa las coordenadas geográficas de una estación.

### Product

Modelo que representa un producto de combustible.

- `productId` (int): ID del producto
- `productName` (str): Nombre del producto
- `prices` (list): Lista de precios (histórico)

### Price

Modelo que representa el precio de un producto en una estación.

- `date` (datetime): Fecha del precio
- `price` (float): Valor del precio

## Errores comunes
- `404 NOT FOUND`: No se encontró la estación o no hay productos que coincidan con los filtros.
- `500 INTERNAL SERVER ERROR`: Error inesperado o problema de conexión con la base de datos.

---

## Notas
- Todos los endpoints devuelven datos en formato JSON.
- **Autenticación:** La mayoría de los endpoints requieren autenticación mediante JWT (token Bearer). Solo el endpoint de creación de usuario es público.
- Para autenticarte, primero debes crear un usuario y luego obtener un token de acceso usando el endpoint `/token`.
- Los filtros son opcionales salvo que se indique lo contrario.

---

## Autenticación y flujo de uso

### 1. Crear un usuario

Realiza un POST a `/users/` con un JSON como:

```json
{
  "username": "usuario",
  "email": "usuario@example.com",
  "full_name": "Usuario Demo",
  "password": "secret"
}
```

### 2. Obtener un token de acceso

Haz un POST a `/token` con `username` y `password` en formato `application/x-www-form-urlencoded`:

```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=usuario&password=secret"
```

Respuesta:
```json
{
  "access_token": "<TOKEN_AQUI>",
  "token_type": "bearer"
}
```

### 3. Acceder a endpoints protegidos

Incluye el token en el header `Authorization`:

```
Authorization: Bearer <TOKEN_AQUI>
```

Ejemplo con curl:

```bash
curl -H "Authorization: Bearer <TOKEN_AQUI>" http://localhost:8000/stations
```

---

### 🛠️ Desarrollo

### Estructura del Proyecto

```text
precio-nafta-api/
├── .env.example           # Plantilla de variables de entorno
├── main.py                # Punto de entrada de la aplicación
├── requirements.txt       # Dependencias del proyecto
├── README.md              # Este archivo
├── api/
│   ├── __init__.py
│   ├── deps.py            # Dependencias de la API
│   └── v1/                # API v1
│       ├── __init__.py
│       ├── api.py         # Rutas principales de la API
│       ├── endpoints/     # Módulos de endpoints
│       └── models/        # Modelos Pydantic
├── core/
│   ├── config.py         # Configuración de la aplicación
│   └── security.py       # Utilidades de seguridad
└── tests/                 # Pruebas automatizadas
```

### Ejecutar Pruebas

```bash
pytest
```

### Formateo de Código

```bash
black .
```

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## ✉️ Contacto

- **Desarrollador:** José María Quintana
- **Email:** mailjmq@gmail.com
- **GitHub:** [@tu-usuario](https://github.com/tu-usuario)

---

*Creado con ❤️ para simplificar la búsqueda de precios de combustibles*

---

¿Dudas o sugerencias? Contactar al desarrollador.
