from flask import Flask, render_template, request, session
from datos import *
from graficos import crear_grafico

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

    if request.method == 'POST':
        ciudad = request.form['ciudad']
        clima_actual = obtener_clima_actual(ciudad)
        pronostico_por_dia = obtener_pronostico(ciudad)
        crear_grafico(pronostico_por_dia)
        guardar_busqueda_usuario(ciudad)

    ciudad_url = request.args.get('ciudad')
    if ciudad_url:
        ciudad = ciudad_url
        clima_actual = obtener_clima_actual(ciudad)
        pronostico_por_dia = obtener_pronostico(ciudad)

    if 'usuario_id' in session:
        usuario_id = session['usuario_id']
        historial_busquedas = mostrar_busquedas_usuario()

    return render_template('index.html', ciudad=ciudad, pronostico_por_dia=pronostico_por_dia, clima_actual=clima_actual, historial_busquedas=historial_busquedas)

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


if __name__ == "__main__":
    app.run(debug=True)
