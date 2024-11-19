from flask import Flask, render_template, request, redirect, url_for, session, abort
from datos import *
from graficos import *

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

@app.before_request
def setup_database():
    inicializar_base_de_datos()

@app.route('/', methods=['GET', 'POST'])
def index():
    ciudad = ""
    clima_actual = {}
    pronostico_por_dia = {}
    historial_busquedas = []
    provincias_o_estados = []
    pais_actual = ""
    clima_por_provincia = {}

    if request.method == 'POST':
        # Ciudad ingresada
        ciudad = request.form['ciudad']

        # Clima actual
        clima_actual = obtener_clima_actual(ciudad)
        
        # Pronostico de 5 dias
        pronostico_por_dia = obtener_pronostico(ciudad)
        
        # Obtener provincias o estados 
        provincias_o_estados, pais_actual = obtener_provincias_o_estados_api(ciudad)
        
        # Clima para cada provincia
        for provincia in provincias_o_estados:
            clima_por_provincia[provincia] = obtener_clima_actual(provincia)
        
        # Guardar datos en la sesión
        session['ciudad'] = ciudad
        session['clima_actual'] = clima_actual
        session['pronostico_por_dia'] = pronostico_por_dia
        session['provincias_o_estados'] = provincias_o_estados
        session['pais_actual'] = pais_actual
        session['clima_por_provincia'] = clima_por_provincia
    else:
        # Recuperar datos de la sesión si existen
        ciudad = session.get('ciudad', None)
        clima_actual = session.get('clima_actual', None)
        pronostico_por_dia = session.get('pronostico_por_dia', [])
        provincias_o_estados = session.get('provincias_o_estados', [])
        pais_actual = session.get('pais_actual', None)
        clima_por_provincia = session.get('clima_por_provincia', {})
        
        # Guardar la búsqueda en el historial del usuario
        if 'usuario_id' in session:
            guardar_busqueda_usuario(ciudad)
    
    # Si se pasa una ciudad en la URL, mostrar el clima de esa ciudad
    ciudad_url = request.args.get('ciudad')
    if ciudad_url:
        ciudad = ciudad_url
        clima_actual = obtener_clima_actual(ciudad)
        pronostico_por_dia = obtener_pronostico(ciudad)

    if 'usuario_id' in session:
        usuario_id = session['usuario_id']
        historial_busquedas = mostrar_busquedas_usuario()    
        
    
    return render_template('index.html', ciudad=ciudad, pronostico_por_dia=pronostico_por_dia, clima_actual=clima_actual,
                            provincias_o_estados=provincias_o_estados,pais_actual=pais_actual, clima_por_provincia=clima_por_provincia,
                            historial_busquedas=historial_busquedas)






# Añadir las rutas al estilo simplificado
app.add_url_rule('/registro', view_func=registro, methods=['GET', 'POST'])
app.add_url_rule('/login', view_func=login, methods=['GET', 'POST'])
app.add_url_rule('/usuarios_admin', view_func=usuarios_admin, methods=['GET', 'POST'])
app.add_url_rule('/favoritos', view_func=favoritos, methods=['GET', 'POST'])
app.add_url_rule('/logout', view_func=logout)
app.add_url_rule('/borrar_historial', view_func=borrar_historial, methods=['POST'])
app.add_url_rule('/eliminar_favorito', view_func=eliminar_favorito, methods=['POST'])
app.add_url_rule('/clima_ciudad', view_func=obtener_clima_ciudad, methods=['GET'])
app.add_url_rule('/agregar-favorito', view_func=agregar_favorito, methods=['POST'])




#Radar de lluvia
@app.route('/radar')
def radar():
    mapa_html = crear_radar() 
    return render_template('radar.html', mapa_html=mapa_html)





#Graficos
@app.route('/graficos', methods=['GET'])
def graficos():
    provincia = session.get('ciudad', 'miami') 
    df_clima = scrap_clima(provincia)
    
    if df_clima is not None:
        grafico_temp = grafico_temperaturas(df_clima)
        grafico_estado = grafico_estado_clima(df_clima)
        grafico_comb = grafico_combinado(df_clima)

        return render_template('graficos.html', grafico_temp=grafico_temp, grafico_estado=grafico_estado, grafico_comb=grafico_comb)
    else:
        abort(500)  





if __name__ == "__main__":
    app.run(debug=True)
