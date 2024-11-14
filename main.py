from flask import Flask, render_template, request, redirect, url_for, flash, session
from bd.usuario import (
    crear_conexion, 
    agregar_usuario, 
    verificar_login, 
    obtener_usuario_por_email, 
    obtener_todos_los_usuarios, 
    actualizar_rol_usuario, 
    eliminar_usuario,
    crear_tabla_usuario
)
import requests
from datos import obtener_clima_actual, obtener_pronostico
from graficos import crear_grafico
from werkzeug.security import generate_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta' 

@app.before_request
def inicializar_base_de_datos():
    conn = crear_conexion('usuarios.db')
    crear_tabla_usuario(conn)  
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    ciudad = ""
    clima_actual = {}
    pronostico_por_dia = {}

    if request.method == 'POST':
        # Ciudad ingresada
        ciudad = request.form['ciudad']

        # Clima actual
        clima_actual = obtener_clima_actual(ciudad)
        
        # Pronostico de 5 dias
        pronostico_por_dia = obtener_pronostico(ciudad)
        
        # Grafico
        crear_grafico(pronostico_por_dia)
    
    return render_template('index.html', ciudad=ciudad, pronostico_por_dia=pronostico_por_dia, clima_actual=clima_actual)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        contraseña = request.form['contraseña']

        conn = crear_conexion('usuarios.db')

        usuario = obtener_usuario_por_email(conn, email)
        if usuario:
            flash("El usuario ya existe. Por favor, ingresa otro email.", 'error')
            return redirect(url_for('registro'))

        # Agregar el usuario
        agregar_usuario(conn, nombre, email, contraseña)
        return redirect(url_for('login')) 

    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        contraseña = request.form['contraseña']

        conn = crear_conexion('usuarios.db')

        # Verificar el login
        usuario = verificar_login(conn, email, contraseña)
        if usuario:
            session['usuario_id'] = usuario[0]  # Guardar el ID del usuario en la sesión
            session['rol'] = usuario[4]         # Guardar el rol en la sesión
            session['nombre_usuario'] = usuario[1]  # Guardar el nombre del usuario en la sesión

            # Redirigir según el rol
            if usuario[4] == 'admin':
                return redirect(url_for('usuarios_admin')) 
            else:
                return redirect(url_for('index')) 
        else:
            flash("Email o contraseña incorrectos.", 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/usuarios_admin', methods=['GET', 'POST'])
def usuarios_admin():
    # Verificar si el usuario es administrador
    if 'usuario_id' not in session or session.get('rol') != 'admin':
        flash("Acceso no autorizado", 'error')
        return redirect(url_for('index'))

    conn = crear_conexion('usuarios.db')

    if request.method == 'POST':
        # Obtener datos del formulario
        id_usuario = request.form.get('id_usuario')
        accion = request.form.get('accion')

        if accion == "actualizar":
            nuevo_rol = request.form.get('nuevo_rol')
            if id_usuario and nuevo_rol:
                actualizar_rol_usuario(conn, id_usuario, nuevo_rol)
                conn.commit()
                flash("Rol actualizado exitosamente.", 'success')

        elif accion == "eliminar":
            if id_usuario:
                eliminar_usuario(conn, id_usuario)
                conn.commit()
                flash("Usuario eliminado exitosamente.", 'success')

        # Redirección para evitar reenvíos de formularios al recargar la página
        return redirect(url_for('usuarios_admin'))

    usuarios = obtener_todos_los_usuarios(conn)
    conn.close()

    return render_template('usuarios_admin.html', usuarios=usuarios)

@app.route('/favoritos')
def favoritos():
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para acceder a tus favoritos', 'warning')
        return redirect(url_for('login'))
    # Aquí puedes agregar la lógica para mostrar los favoritos del usuario.
    return render_template('favoritos.html')

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    session.pop('nombre_usuario', None)
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
