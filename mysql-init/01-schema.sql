-- Esquema inicial del videoclub.

CREATE DATABASE IF NOT EXISTS videoclub
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE videoclub;

CREATE TABLE IF NOT EXISTS peliculas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    director VARCHAR(255),
    anio INT,
    genero VARCHAR(100),
    stock INT NOT NULL DEFAULT 1,
    descripcion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO peliculas (titulo, director, anio, genero, stock, descripcion) VALUES
    ('El Padrino', 'Francis Ford Coppola', 1972, 'Drama', 3,
     'Historia de la familia Corleone, una de las cinco familias mas poderosas de la mafia de Nueva York.'),
    ('Pulp Fiction', 'Quentin Tarantino', 1994, 'Crimen', 2,
     'Varias historias entrelazadas de gangsters, un boxeador y dos ladrones.'),
    ('El Senor de los Anillos: La Comunidad del Anillo', 'Peter Jackson', 2001, 'Fantasia', 4,
     'Un hobbit de la Comarca emprende un viaje para destruir el Anillo Unico.'),
    ('Matrix', 'Lana y Lilly Wachowski', 1999, 'Ciencia Ficcion', 2,
     'Un hacker descubre la verdadera naturaleza de la realidad.'),
    ('Forrest Gump', 'Robert Zemeckis', 1994, 'Drama', 1,
     'Un hombre con limitaciones vive momentos clave de la historia de EEUU.'),
    ('Interstellar', 'Christopher Nolan', 2014, 'Ciencia Ficcion', 3,
     'Un grupo de exploradores viaja a traves de un agujero de gusano en busca de un nuevo hogar para la humanidad.');
