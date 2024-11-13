from flask import Flask, render_template, request
import requests

from datos import obtener_clima_actual, obtener_pronostico
from graficos import crear_grafico

app = Flask(__name__)  # iniciar flask

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

if __name__ == '__main__':
    app.run(debug=True)
