"""Backend del videoclub: catalogo de peliculas y gestion de stock."""
import os
import time
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
import pymysql
import pymysql.cursors

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-change-me')

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'db'),
    'port': int(os.environ.get('DB_PORT', 3306)),
    'user': os.environ.get('DB_USER', 'videoclub'),
    'password': os.environ.get('DB_PASSWORD', 'videoclub123'),
    'database': os.environ.get('DB_NAME', 'videoclub'),
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
    'autocommit': False,
}


def get_db(retries=15, delay=2):
    """Obtiene una conexion con reintentos para gestionar el arranque de MySQL."""
    last_err = None
    for attempt in range(retries):
        try:
            return pymysql.connect(**DB_CONFIG)
        except pymysql.err.OperationalError as exc:
            last_err = exc
            app.logger.warning("Esperando a MySQL (intento %s/%s)...", attempt + 1, retries)
            time.sleep(delay)
    raise last_err


# ---------- Rutas de la aplicacion ----------

@app.route('/')
def index():
    """Listado de peliculas."""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'SELECT id, titulo, director, anio, genero, stock '
                'FROM peliculas ORDER BY id DESC'
            )
            peliculas = cur.fetchall()
    finally:
        conn.close()
    return render_template('index.html', peliculas=peliculas)


@app.route('/pelicula/new', methods=['GET'])
def nueva_pelicula():
    """Formulario para crear una pelicula."""
    return render_template('form.html', pelicula=None, accion='Crear')


@app.route('/pelicula', methods=['POST'])
def crear_pelicula():
    """Procesa la creacion de una pelicula."""
    titulo = request.form.get('titulo', '').strip()
    director = request.form.get('director', '').strip()
    anio = request.form.get('anio', '').strip()
    genero = request.form.get('genero', '').strip()
    stock = request.form.get('stock', '1').strip()
    descripcion = request.form.get('descripcion', '').strip()

    if not titulo:
        flash('El titulo es obligatorio', 'error')
        return redirect(url_for('nueva_pelicula'))

    try:
        anio_val = int(anio) if anio else None
        stock_val = int(stock) if stock else 1
    except ValueError:
        flash('Anio y stock deben ser numericos', 'error')
        return redirect(url_for('nueva_pelicula'))

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO peliculas (titulo, director, anio, genero, stock, descripcion) '
                'VALUES (%s, %s, %s, %s, %s, %s)',
                (titulo, director or None, anio_val, genero or None, stock_val, descripcion or None)
            )
        conn.commit()
        flash(f'Pelicula "{titulo}" creada correctamente', 'ok')
    finally:
        conn.close()

    return redirect(url_for('index'))


@app.route('/pelicula/<int:pelicula_id>')
def detalle_pelicula(pelicula_id):
    """Detalle de una pelicula concreta."""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM peliculas WHERE id = %s', (pelicula_id,))
            pelicula = cur.fetchone()
    finally:
        conn.close()

    if pelicula is None:
        abort(404)
    return render_template('detalle.html', pelicula=pelicula)


@app.route('/pelicula/<int:pelicula_id>/edit', methods=['GET'])
def editar_pelicula_form(pelicula_id):
    """Formulario para editar."""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM peliculas WHERE id = %s', (pelicula_id,))
            pelicula = cur.fetchone()
    finally:
        conn.close()

    if pelicula is None:
        abort(404)
    return render_template('form.html', pelicula=pelicula, accion='Actualizar')


@app.route('/pelicula/<int:pelicula_id>/edit', methods=['POST'])
def editar_pelicula(pelicula_id):
    """Procesa la actualizacion."""
    titulo = request.form.get('titulo', '').strip()
    director = request.form.get('director', '').strip()
    anio = request.form.get('anio', '').strip()
    genero = request.form.get('genero', '').strip()
    stock = request.form.get('stock', '1').strip()
    descripcion = request.form.get('descripcion', '').strip()

    if not titulo:
        flash('El titulo es obligatorio', 'error')
        return redirect(url_for('editar_pelicula_form', pelicula_id=pelicula_id))

    try:
        anio_val = int(anio) if anio else None
        stock_val = int(stock) if stock else 1
    except ValueError:
        flash('Anio y stock deben ser numericos', 'error')
        return redirect(url_for('editar_pelicula_form', pelicula_id=pelicula_id))

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                'UPDATE peliculas SET titulo=%s, director=%s, anio=%s, '
                'genero=%s, stock=%s, descripcion=%s WHERE id=%s',
                (titulo, director or None, anio_val, genero or None,
                 stock_val, descripcion or None, pelicula_id)
            )
        conn.commit()
        flash(f'Pelicula "{titulo}" actualizada', 'ok')
    finally:
        conn.close()

    return redirect(url_for('detalle_pelicula', pelicula_id=pelicula_id))


@app.route('/pelicula/<int:pelicula_id>/delete', methods=['POST'])
def borrar_pelicula(pelicula_id):
    """Borrar una pelicula."""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT titulo FROM peliculas WHERE id=%s', (pelicula_id,))
            row = cur.fetchone()
            if row is None:
                abort(404)
            cur.execute('DELETE FROM peliculas WHERE id=%s', (pelicula_id,))
        conn.commit()
        flash(f'Pelicula "{row["titulo"]}" borrada', 'ok')
    finally:
        conn.close()

    return redirect(url_for('index'))


@app.route('/pelicula/<int:pelicula_id>/alquilar', methods=['POST'])
def alquilar_pelicula(pelicula_id):
    """Decrementa el stock (alquilar un ejemplar)."""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT stock, titulo FROM peliculas WHERE id=%s', (pelicula_id,))
            row = cur.fetchone()
            if row is None:
                abort(404)
            if row['stock'] <= 0:
                flash(f'No quedan ejemplares de "{row["titulo"]}"', 'error')
            else:
                cur.execute('UPDATE peliculas SET stock = stock - 1 WHERE id=%s', (pelicula_id,))
                conn.commit()
                flash(f'Alquilado un ejemplar de "{row["titulo"]}"', 'ok')
    finally:
        conn.close()

    return redirect(url_for('detalle_pelicula', pelicula_id=pelicula_id))


@app.route('/pelicula/<int:pelicula_id>/devolver', methods=['POST'])
def devolver_pelicula(pelicula_id):
    """Incrementa el stock (devolver un ejemplar)."""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT titulo FROM peliculas WHERE id=%s', (pelicula_id,))
            row = cur.fetchone()
            if row is None:
                abort(404)
            cur.execute('UPDATE peliculas SET stock = stock + 1 WHERE id=%s', (pelicula_id,))
        conn.commit()
        flash(f'Devuelto un ejemplar de "{row["titulo"]}"', 'ok')
    finally:
        conn.close()

    return redirect(url_for('detalle_pelicula', pelicula_id=pelicula_id))


@app.route('/healthz')
def healthz():
    """Endpoint de health check. Comprueba la conexion con MySQL."""
    try:
        conn = get_db(retries=1, delay=0)
        with conn.cursor() as cur:
            cur.execute('SELECT 1')
            cur.fetchone()
        conn.close()
        return jsonify(status='ok'), 200
    except Exception as exc:
        return jsonify(status='error', detail=str(exc)), 503


@app.errorhandler(404)
def not_found(_):
    return render_template('index.html', peliculas=[], error='Pelicula no encontrada'), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
