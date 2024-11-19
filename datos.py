import requests
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session, jsonify
from bd.usuario import *
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session
import folium
from bd.usuario import *
from graficos import *
from collections import OrderedDict

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
            hora = fecha.strftime('%H:%M')  

            if dia not in pronostico_por_dia:
                pronostico_por_dia[dia] = []

            temp = item['main']['temp']
            sensacion_termica = item['main']['feels_like']
            humedad = item['main']['humidity']
            presion = item['main']['pressure']
            punto_rocio = item['main']['temp_min'] 
            viento_velocidad = item['wind']['speed']
            viento_direccion = item['wind']['deg']
            nubosidad = item['clouds']['all']
            visibilidad = item.get('visibility', 0) / 1000  
            lluvia = item.get('rain', {}).get('3h', 0) 
            rafagas = item['wind'].get('gust', 0)
            niebla = 'Sí' if 'mist' in item['weather'][0]['description'].lower() else 'No'
            cota_nieve = item.get('snow', {}).get('3h', 0)  
            
            descripcion = item['weather'][0]['description']

            pronostico_por_dia[dia].append({
                'fecha': item['dt_txt'],
                'hora' : hora,
                'temp': temp,
                'sensacion_termica': sensacion_termica,
                'humedad': humedad,
                'presion': presion,
                'punto_rocio': punto_rocio,
                'viento': viento_velocidad,
                'viento_direccion': viento_direccion,
                'nubosidad': nubosidad,
                'visibilidad': visibilidad,
                'lluvia': lluvia,
                'rafagas': rafagas,
                'niebla': niebla,
                'cota_nieve': cota_nieve,
                'descripcion': descripcion
            })

    return pronostico_por_dia



# Funcines para obtener provincias 
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




# Scrap para obtener datos del clima del mes actual
def scrap_clima(provincia):
    url = 'https://www.meteoprog.com/es/weather/{}/month/'.format(provincia)

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



#Radar de lluvias tiempo real
def crear_radar():
    mapa = folium.Map(location=[0, 0], zoom_start=2)

    api_key = "36702f1bcf086e4be0e9d8ecb12c2147"
    base_url = "https://tile.openweathermap.org/map/"

    horas = [-3, -2, -1, 0, 1, 2, 3] 
    capas = []

    for hora in horas:
        capas.append({
            "nombre": f"Precipitación ({'+' if hora > 0 else ''}{hora}h)",
            "url": f"{base_url}precipitation_new/{{z}}/{{x}}/{{y}}.png?appid={api_key}&tm={hora}",
        })

    for capa in capas:
        folium.TileLayer(
            tiles=capa["url"],
            attr="OpenWeatherMap",
            name=capa["nombre"],
            overlay=True
        ).add_to(mapa)

    folium.LayerControl().add_to(mapa)

    return mapa._repr_html_()
