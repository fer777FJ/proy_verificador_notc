create database db_verifica_bolivia;
use db_verifica_bolivia;
-- Tabla para contenidos
create table verificacion_texto(
	id int auto_increment primary key,
    titulo varchar(255),
    contenido text,
    veredicto enum('Falso','Verdadero', 'Verificado Pero En Desarrollo', 'Contradictorio'),
    confianza float,
    fecha datetime default current_timestamp
);
-- Tabla para Links
CREATE TABLE verificacion_link (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255),
    url_link TEXT, -- Contenido del link
    veredicto ENUM('Falso','Verdadero', 'Engañoso', 'No determinado'),
    confianza FLOAT,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para Imágenes
CREATE TABLE verificacion_imagen (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ruta_img VARCHAR(255), -- Donde se guarda el archivo físico
    descripcion TEXT,
    veredicto ENUM('Falso','Verdadero', 'Engañoso', 'No determinado'),
    confianza FLOAT,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP
);