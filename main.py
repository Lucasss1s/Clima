from flask import Flask, render_template, request
import requests

from datos import *
from graficos import crear_grafico

app = Flask(__name__)  

@app.route('/', methods=['GET', 'POST'])
def index():
    ciudad = ""
    clima_actual = {}
    pronostico_por_dia = {}
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


        # Grafico
        crear_grafico(pronostico_por_dia)
            
        
    
    return render_template('index.html', ciudad=ciudad, pronostico_por_dia=pronostico_por_dia, clima_actual=clima_actual,
                            provincias_o_estados=provincias_o_estados,pais_actual=pais_actual, clima_por_provincia=clima_por_provincia)

if __name__ == '__main__':
    app.run(debug=True)
