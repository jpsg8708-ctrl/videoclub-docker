# Videoclub

Aplicacion web multicontenedor para gestionar el catalogo de peliculas de un videoclub. Implementa un CRUD completo sobre peliculas con persistencia en MySQL y un proxy inverso Nginx como punto de entrada.

---

## Arranque rapido

```bash
chmod +x start.sh
./start.sh
```

- **Tiempo del primer arranque:** ~2-3 minutos (descarga de imagenes, build y primera inicializacion de MySQL).
- **URL de la aplicacion:** http://localhost:8080

Cuando el script termina de mostrar el mensaje de exito, abre esa URL en el navegador y veras el listado del videoclub con peliculas de ejemplo.

---

## Arquitectura

Tres contenedores coordinados mediante Docker Compose:

```
Usuario -> Nginx (8080) -> Flask/Gunicorn (5000) -> MySQL (3306)
```

| Servicio | Imagen                  | Puerto interno | Papel                                       |
| -------- | ----------------------- | -------------- | ------------------------------------------- |
| `nginx`  | `nginx:1.27-alpine`     | 8080           | Proxy inverso. Unica puerta de entrada.     |
| `app`    | `python:3.11-slim`      | 5000           | Backend Flask + Gunicorn.                   |
| `db`     | `mysql:8.0`             | 3306           | Base de datos con volumen persistente.      |

Los tres servicios comparten una red interna (`videoclub-net`) y se comunican por DNS (`nginx` -> `app` -> `db`).

### Persistencia

El contenedor `db` monta un volumen Docker nombrado (`db_data`) sobre `/var/lib/mysql`. Los datos sobreviven a reinicios y a `docker compose down`. Para borrarlos explicitamente:

```bash
docker compose down -v
```

---

## Funcionalidades (CRUD)

La entidad principal es **pelicula**, con los campos: id, titulo, director, anio, genero, stock, descripcion.

| Metodo | Ruta                                 | Operacion                      |
| ------ | ------------------------------------ | ------------------------------ |
| GET    | `/`                                  | Listado de peliculas           |
| GET    | `/pelicula/new`                      | Formulario de creacion         |
| POST   | `/pelicula`                          | Crear pelicula                 |
| GET    | `/pelicula/<id>`                     | Detalle                        |
| GET    | `/pelicula/<id>/edit`                | Formulario de edicion          |
| POST   | `/pelicula/<id>/edit`                | Actualizar pelicula            |
| POST   | `/pelicula/<id>/delete`              | Borrar pelicula                |
| POST   | `/pelicula/<id>/alquilar`            | Decrementar stock (alquilar)   |
| POST   | `/pelicula/<id>/devolver`            | Incrementar stock (devolver)   |
| GET    | `/healthz`                           | Health check (JSON)            |

MySQL se inicializa con el esquema y 6 peliculas de ejemplo la primera vez que arranca, leyendo el script de `mysql-init/01-schema.sql`.

---

## Estructura del proyecto

```
videoclub-docker/
|-- app/
|   |-- Dockerfile
|   |-- requirements.txt
|   |-- app.py
|   |-- templates/
|       |-- base.html
|       |-- index.html
|       |-- detalle.html
|       |-- form.html
|-- nginx/
|   |-- Dockerfile
|   |-- default.conf
|-- mysql-init/
|   |-- 01-schema.sql
|-- docker-compose.yml
|-- start.sh
|-- .gitignore
|-- README.md
```

---

## Comandos utiles

```bash
# Ver logs en tiempo real
docker compose logs -f

# Logs solo de la app
docker compose logs -f app

# Parar (contenedores paran; datos de MySQL se conservan)
docker compose down

# Parar y borrar datos (resetea MySQL)
docker compose down -v

# Reconstruir tras cambios de codigo
docker compose up -d --build

# Entrar a la base de datos
docker compose exec db mysql -uvideoclub -pvideoclub123 videoclub
```
