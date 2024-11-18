from flask import Flask, render_template, request
from datos import (
    inicializar_base_de_datos, 
    registro, 
    login, 
    usuarios_admin, 
    favoritos, 
    logout,
    obtener_clima_actual, 
    obtener_pronostico
)
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

    if request.method == 'POST':
        ciudad = request.form['ciudad']
        clima_actual = obtener_clima_actual(ciudad)
        pronostico_por_dia = obtener_pronostico(ciudad)
        crear_grafico(pronostico_por_dia)
    
    return render_template('index.html', ciudad=ciudad, pronostico_por_dia=pronostico_por_dia, clima_actual=clima_actual)

# Rutas para otras funciones
app.add_url_rule('/registro', view_func=registro, methods=['GET', 'POST'])
app.add_url_rule('/login', view_func=login, methods=['GET', 'POST'])
app.add_url_rule('/usuarios_admin', view_func=usuarios_admin, methods=['GET', 'POST'])
app.add_url_rule('/favoritos', view_func=favoritos)
app.add_url_rule('/logout', view_func=logout)

if __name__ == "__main__":
    app.run(debug=True)
