import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, session
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
from graficos import crear_grafico

# Funciones para traer el clima actual y a 5 días
def obtener_clima_actual(ciudad):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid=36702f1bcf086e4be0e9d8ecb12c2147&units=metric"
    res = requests.get(url)
    if res.status_code == 200:
        data = res.json()
        clima = {
            "temp": data['main']['temp'],
            "descripcion": data["weather"][0]["description"],
            "temp_max": round(data["main"]["temp_max"]),
            "temp_min": round(data["main"]["temp_min"])
        }
        return clima

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

<<<<<<< HEAD



# Función para obtener provincias o estados usando la API de Geonames
def obtener_provincias_o_estados_api(ciudad):
    geonames_usuario = "lucass1s" 
    url_ciudad = f"http://api.geonames.org/searchJSON?q={ciudad}&maxRows=1&username={geonames_usuario}"
    res_ciudad = requests.get(url_ciudad)
    if res_ciudad.status_code != 200:
        return [], None

    data_ciudad = res_ciudad.json()
    if not data_ciudad['geonames']:
        return [], None

    pais = data_ciudad['geonames'][0]['countryName']
    url_provincias = f"http://api.geonames.org/childrenJSON?geonameId={data_ciudad['geonames'][0]['countryId']}&username={geonames_usuario}"
    res_provincias = requests.get(url_provincias)
    if res_provincias.status_code != 200:
        return [], None

    data_provincias = res_provincias.json()
    provincias = [prov['name'] for prov in data_provincias.get('geonames', [])]
    return provincias, pais


def obtener_clima_por_provincia(ciudad):
    provincias, pais = obtener_provincias_o_estados_api(ciudad)
    clima_por_provincia = {}

    for provincia in provincias:
        try:
            clima = obtener_clima_actual(provincia) 
            clima_por_provincia[provincia] = clima
        except Exception as e:
            clima_por_provincia[provincia] = {"error": f"No se pudo obtener el clima: {str(e)}"}

    return {
        "ciudad": ciudad,
        "pais": pais,
        "clima_por_provincia": clima_por_provincia
    }


def obtener_provincias_y_clima(ciudad):
    provincias, pais, _ = obtener_provincias_o_estados_api(ciudad)
    provincias_clima = []
    for provincia in provincias:
        clima = obtener_clima_por_provincia(provincia)
        if clima:
            provincias_clima.append({
                "provincia": provincia,
                "descripcion": clima["descripcion"],
                "temp_max": clima["temp_max"],
                "temp_min": clima["temp_min"]
            })
    return provincias_clima, pais





=======
>>>>>>> test
# Scrap para obtener datos del clima del mes actual
def obtener_clima_mes_actual():
    url = 'https://www.meteoprog.com/es/weather/Buenosaires/month/'
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        clima = soup.find_all('span', class_='city-month__day-temperature')  
        fecha = soup.find_all('div', class_='city-month__day-date') 
        estado_clima = soup.find_all('span', class_='city-month__day-icon')  

        fechas = []
        temperaturas_max = []
        temperaturas_min = []
        estados = []

        for i in range(len(fecha)):
            fecha_dia = fecha[i].get_text(strip=True)
            temperaturas = clima[i].get_text(strip=True)
            temp_max = temperaturas[:4]  
            temp_min = temperaturas[4:]  
            icon_class = estado_clima[i].get('class')

            if any('rain' in clase for clase in icon_class):
                estado = 'Lluvia'
            elif any('cloud' in clase for clase in icon_class):
                estado = 'Nublado'
            elif any('snow' in clase for clase in icon_class):
                estado = 'Nieve'
            elif any('storm' in clase for clase in icon_class):
                estado = 'Tormenta'
            elif any('sun' in clase for clase in icon_class):
                estado = 'Soleado'
            
            fechas.append(fecha_dia)
            temperaturas_max.append(temp_max)
            temperaturas_min.append(temp_min)
            estados.append(estado)

        df_clima = pd.DataFrame({
            'Fecha': fechas,
            'Temperatura Máxima': temperaturas_max,
            'Temperatura Mínima': temperaturas_min,
            'Estado del Clima': estados
        })

        return df_clima

    else:
        print(f'Error al acceder a la página: {response.status_code}')
        return None

# Funciones de autenticación y administración de usuarios
def inicializar_base_de_datos():
    conn = crear_conexion('usuarios.db')
    crear_tabla_usuario(conn)  
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
        return redirect(url_for('index'))

    conn = crear_conexion('usuarios.db')

    if request.method == 'POST':
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

        return redirect(url_for('usuarios_admin'))

    usuarios = obtener_todos_los_usuarios(conn)
    conn.close()

    return render_template('usuarios_admin.html', usuarios=usuarios)

def favoritos():
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para acceder a tus favoritos', 'warning')
        return redirect(url_for('login'))
    return render_template('favoritos.html')

def logout():
    session.pop('usuario_id', None)
    session.pop('nombre_usuario', None)
    return redirect(url_for('index'))
