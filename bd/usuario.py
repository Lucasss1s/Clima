import sqlite3
from sqlite3 import Error
from werkzeug.security import generate_password_hash, check_password_hash

def crear_conexion(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Conectado a la base de datos {db_file}")
        return conn
    except Error as e:
        print(f"Error al conectar con la base de datos: {e}")
    return conn

def crear_tabla_usuario(conn):
    try:
        cursor = conn.cursor()
        sql_crear_tabla_usuarios = """
        CREATE TABLE IF NOT EXISTS Usuarios (
            id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            contraseña TEXT NOT NULL,
            rol TEXT NOT NULL DEFAULT 'usuario'
        );
        """
        cursor.execute(sql_crear_tabla_usuarios)
        print("Tabla 'Usuarios' creada exitosamente.")
    except Error as e:
        print(f"Error al crear la tabla: {e}")

def crear_tabla_busquedas(conn):
    try:
        cursor = conn.cursor()
        sql_crear_tabla_busquedas = """
        CREATE TABLE IF NOT EXISTS busquedas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            ciudad TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES Usuarios (id_usuario)
        );
        """
        cursor.execute(sql_crear_tabla_busquedas)
        print("Tabla 'busquedas' creada exitosamente.")
    except Error as e:
        print(f"Error al crear la tabla de búsquedas: {e}")

def crear_tabla_favoritos(conn):
    try:
        cursor = conn.cursor()
        sql_crear_tabla_favoritos = """
        CREATE TABLE IF NOT EXISTS favoritos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            ciudad TEXT NOT NULL,
            FOREIGN KEY (usuario_id) REFERENCES Usuarios (id_usuario)
        );
        """
        cursor.execute(sql_crear_tabla_favoritos)
        print("Tabla 'favoritos' creada exitosamente.")
    except Error as e:
        print(f"Error al crear la tabla de favoritos: {e}")


def agregar_usuario(conn, nombre, email, contraseña):
    try:
        cursor = conn.cursor()
        contraseña_hash = generate_password_hash(contraseña)  
        sql_insertar_usuario = """
        INSERT INTO Usuarios (nombre, email, contraseña)
        VALUES (?, ?, ?)
        """
        cursor.execute(sql_insertar_usuario, (nombre, email, contraseña_hash))
        conn.commit()
        print("Usuario cargado exitosamente.")
    except Error as e:
        print(f"Error al insertar usuario: {e}")

def obtener_usuario_por_email(conn, email):
    cursor = conn.cursor()
    sql_obtener_usuario = "SELECT * FROM Usuarios WHERE email = ?"
    cursor.execute(sql_obtener_usuario, (email,))
    return cursor.fetchone()

def obtener_todos_los_usuarios(conn):
    cursor = conn.cursor()
    sql_obtener_usuarios = "SELECT id_usuario, nombre, email, rol FROM Usuarios"
    cursor.execute(sql_obtener_usuarios)
    return cursor.fetchall()

def verificar_login(conn, email, contraseña):
    usuario = obtener_usuario_por_email(conn, email)
    if usuario:
        contraseña_hash = usuario[3]  
        if check_password_hash(contraseña_hash, contraseña):
            print("Inicio de sesión exitoso.")
            return usuario
        else:
            print("Contraseña incorrecta.")
            return None
    else:
        print("El usuario no existe.")
        return None

def actualizar_rol_usuario(conn, id_usuario, nuevo_rol):
    try:
        cursor = conn.cursor()
        sql_actualizar_rol = """
        UPDATE Usuarios 
        SET rol = ?
        WHERE id_usuario = ?
        """
        cursor.execute(sql_actualizar_rol, (nuevo_rol, id_usuario))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Rol del usuario con ID {id_usuario} actualizado a {nuevo_rol}.")
        else:
            print(f"No se encontró el usuario con el ID {id_usuario}.")
    except Error as e:
        print(f"Error al actualizar el rol del usuario: {e}")

def eliminar_usuario(conn, id_usuario):
    try:
        cursor = conn.cursor()
        sql_eliminar_usuario = "DELETE FROM Usuarios WHERE id_usuario = ?"
        cursor.execute(sql_eliminar_usuario, (id_usuario,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Usuario con ID {id_usuario} eliminado exitosamente.")
        else:
            print(f"No se encontró el usuario con ID {id_usuario}.")
    except Error as e:
        print(f"Error al eliminar el usuario: {e}")

# Funciones de búsquedas
def guardar_busqueda(conn, usuario_id, ciudad):
    try:
        cursor = conn.cursor()
        sql_guardar_busqueda = "INSERT INTO busquedas (usuario_id, ciudad) VALUES (?, ?)"
        cursor.execute(sql_guardar_busqueda, (usuario_id, ciudad))
        conn.commit()
        print(f"Búsqueda de '{ciudad}' guardada para el usuario con ID {usuario_id}.")
    except Error as e:
        print(f"Error al guardar la búsqueda: {e}")

def obtener_busquedas(conn, usuario_id):
    cursor = conn.cursor()
    sql_obtener_busquedas = "SELECT ciudad FROM busquedas WHERE usuario_id = ? ORDER BY id DESC"
    cursor.execute(sql_obtener_busquedas, (usuario_id,))
    return [fila[0] for fila in cursor.fetchall()]

def guardar_favorito(conn, usuario_id, ciudad):
    try:
        cursor = conn.cursor()
        # Verificamos si la ciudad ya está guardada como favorito
        sql_comprobar_favorito = "SELECT * FROM favoritos WHERE usuario_id = ? AND ciudad = ?"
        cursor.execute(sql_comprobar_favorito, (usuario_id, ciudad))
        if cursor.fetchone() is None:  # Si no existe, la insertamos
            sql_guardar_favorito = "INSERT INTO favoritos (usuario_id, ciudad) VALUES (?, ?)"
            cursor.execute(sql_guardar_favorito, (usuario_id, ciudad))
            conn.commit()
            print(f"Ciudad '{ciudad}' guardada como favorito para el usuario con ID {usuario_id}.")
        else:
            print("La ciudad ya está en tus favoritos.")
    except Error as e:
        print(f"Error al guardar la ciudad como favorito: {e}")

def obtener_favoritos(conn, usuario_id):
    cursor = conn.cursor()
    sql_obtener_favoritos = "SELECT ciudad FROM favoritos WHERE usuario_id = ? ORDER BY id DESC"
    cursor.execute(sql_obtener_favoritos, (usuario_id,))
    return [fila[0] for fila in cursor.fetchall()]

def eliminar_favorito(conn, usuario_id, ciudad):
    try:
        cursor = conn.cursor()
        sql_eliminar_favorito = "DELETE FROM favoritos WHERE usuario_id = ? AND ciudad = ?"
        cursor.execute(sql_eliminar_favorito, (usuario_id, ciudad))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Ciudad '{ciudad}' eliminada de los favoritos del usuario con ID {usuario_id}.")
        else:
            print(f"No se encontró la ciudad '{ciudad}' en los favoritos del usuario.")
    except Error as e:
        print(f"Error al eliminar el favorito: {e}")

# Función para borrar el historial de un usuario
def borrar_historial_usuario(usuario_id):
    conn = crear_conexion('usuarios.db')
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM busquedas WHERE usuario_id = ?", (usuario_id,))
    conn.commit()
    conn.close()


