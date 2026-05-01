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

El contenedor `db` monta un volumen Docker nombrado (`db_data`) sobre `/var/lib/mysql`. Los datos sobreviven a reinicios y a `docker compose down`.

### Puertos

- **Puerto principal:** `8080` — acceso a la aplicación a través de Nginx.
- Puertos internos (no requieren acceso directo):
  - `5000` — Flask/Gunicorn (solo accesible dentro de la red Docker).
  - `3306` — MySQL (solo accesible dentro de la red Docker).

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


