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