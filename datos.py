import requests
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from bd.usuario import *

# Funciones para traer el clima actual y a 5 días
def obtener_clima_actual(ciudad):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid=36702f1bcf086e4be0e9d8ecb12c2147&units=metric"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        temp = data['main']['temp']
        descripcion = data['weather'][0]['description']
        return {'temp': temp, 'descripcion': descripcion}

def obtener_pronostico(ciudad):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={ciudad}&appid=36702f1bcf086e4be0e9d8ecb12c2147&units=metric"
    res = requests.get(url)
    pronostico_por_dia = {}
    if res.status_code == 200:
        data = res.json()
        for item in data['list']:
            fecha = datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S')
            dia = fecha.strftime('%A')
            if dia not in pronostico_por_dia:
                pronostico_por_dia[dia] = []
            temp = item['main']['temp']
            descripcion = item['weather'][0]['description']
            pronostico_por_dia[dia].append({'fecha': item['dt_txt'], 'temp': temp, 'descripcion': descripcion})
    return pronostico_por_dia

# Funciones de autenticación y administración de usuarios
def inicializar_base_de_datos():
    conn = crear_conexion('usuarios.db')
    crear_tabla_usuario(conn) 
    crear_tabla_busquedas(conn)
    crear_tabla_favoritos(conn)
    conn.close()

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

        agregar_usuario(conn, nombre, email, contraseña)
        return redirect(url_for('login')) 

    return render_template('registro.html')

def login():
    if request.method == 'POST':
        email = request.form['email']
        contraseña = request.form['contraseña']
        conn = crear_conexion('usuarios.db')
        usuario = verificar_login(conn, email, contraseña)
        if usuario:
            session['usuario_id'] = usuario[0]
            session['rol'] = usuario[4]
            session['nombre_usuario'] = usuario[1]
            if usuario[4] == 'admin':
                return redirect(url_for('usuarios_admin')) 
            else:
                return redirect(url_for('index')) 
        else:
            flash("Email o contraseña incorrectos.", 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

def usuarios_admin():
    if 'usuario_id' not in session or session.get('rol') != 'admin':
        flash("Acceso no autorizado", 'error')
        return redirect(url_for('login'))

    conn = crear_conexion('usuarios.db')

    if request.method == 'POST':
        id_usuario = request.form.get('id_usuario')
        accion = request.form.get('accion')

        if accion == "actualizar":
            nuevo_rol = request.form.get('nuevo_rol')
            if id_usuario and nuevo_rol:
                actualizar_rol_usuario(conn, id_usuario, nuevo_rol)
                conn.commit()
        elif accion == "eliminar":
            if id_usuario:
                eliminar_usuario(conn, id_usuario)
                conn.commit()

        return redirect(url_for('usuarios_admin'))

    usuarios = obtener_todos_los_usuarios(conn)
    conn.close()

    return render_template('usuarios_admin.html', usuarios=usuarios)

def logout():
    session.pop('usuario_id', None)
    session.pop('nombre_usuario', None)
    session.pop('historial_busquedas', None)  
    session.clear()
    return redirect(url_for('index'))

# Funciones de busqueda
def guardar_busqueda_usuario(ciudad):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']
    conn = crear_conexion('usuarios.db')

    guardar_busqueda(conn, usuario_id, ciudad)
    
    conn.close()
    return redirect(url_for('index'))

def mostrar_busquedas_usuario():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']
    conn = crear_conexion('usuarios.db')
    busquedas = obtener_busquedas(conn, usuario_id)
    conn.close()

    return busquedas

def guardar_favorito_usuario(usuario_id, ciudad):
    conn = crear_conexion('usuarios.db')
    guardar_favorito(conn, usuario_id, ciudad)
    conn.close()

def obtener_favoritos_usuario(usuario_id):
    conn = crear_conexion('usuarios.db')
    favoritos_lista = obtener_favoritos(conn, usuario_id)
    conn.close()
    return favoritos_lista

def eliminar_favorito_usuario(usuario_id, ciudad):
    conn = crear_conexion('usuarios.db')
    eliminar_favorito(conn, usuario_id, ciudad)  
    conn.close()

def favoritos():
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para acceder a tus favoritos', 'error')
        return redirect(url_for('login'))

    usuario_id = session['usuario_id']
 
    favoritos_lista = obtener_favoritos_usuario(usuario_id)

    if request.method == 'POST':
        ciudad = request.form.get('ciudad')
        if ciudad:
            eliminar_favorito_usuario(usuario_id, ciudad)  
            flash(f'Ciudad "{ciudad}" eliminada de tus favoritos.', 'success')
            return redirect(url_for('favoritos'))

    return render_template('favoritos.html', favoritos_lista=favoritos_lista)

def borrar_historial_usuario(usuario_id):
    conn = crear_conexion('usuarios.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM busquedas WHERE usuario_id = ?", (usuario_id,))
    conn.commit()
    conn.close()

def borrar_historial():
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para borrar el historial', 'error')
        return redirect(url_for('login'))
    
    usuario_id = session['usuario_id']
    borrar_historial_usuario(usuario_id)
    flash('Historial borrado correctamente', 'success')
    return redirect(url_for('favoritos'))

def obtener_clima_ciudad():
    ciudad = request.args.get('ciudad')
    if ciudad:
        clima_actual = obtener_clima_actual(ciudad)
        if clima_actual:
            return jsonify({
                'temp': clima_actual['temp'],
                'descripcion': clima_actual['descripcion']
            })
        else:
            return jsonify({'error': 'No se pudo obtener el clima de la ciudad.'})
    return jsonify({'error': 'Ciudad no proporcionada'})

def agregar_favorito():
    if not session.get('usuario_id'):
        return jsonify({'message': 'Debes iniciar sesión para agregar a favoritos.'}), 401

    datos = request.get_json()
    ciudad = datos.get('ciudad')
    usuario_id = session['usuario_id']
    
    try:
        conn = crear_conexion('usuarios.db')
        guardar_favorito(conn, usuario_id, ciudad)
        conn.close()
        return jsonify({'message': f'{ciudad} se agregó a favoritos exitosamente.'}), 200
    except Exception as e:
        return jsonify({'message': f'Error al agregar a favoritos: {str(e)}'}), 500
