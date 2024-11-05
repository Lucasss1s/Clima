from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)  # iniciar flask

@app.route('/', methods=['GET', 'POST'])
def index():
    ciudad = ""
    clima_actual = {}
    pronostico_por_dia = {}

    if request.method == 'POST':
        ciudad = request.form['ciudad']

        # Clima actual
        url_clima = f"https://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid=36702f1bcf086e4be0e9d8ecb12c2147&units=metric"
        res_clima = requests.get(url_clima)
        data_clima = res_clima.json()

        if res_clima.status_code == 200:
            temp = data_clima['main']['temp']
            descripcion = data_clima['weather'][0]['description']
            clima_actual = {'temp': temp, 'descripcion': descripcion}
        
        # Pronóstico de 5 días
        url_pronostico = f"https://api.openweathermap.org/data/2.5/forecast?q={ciudad}&appid=36702f1bcf086e4be0e9d8ecb12c2147&units=metric"
        res_pronostico = requests.get(url_pronostico)
        data_pronostico = res_pronostico.json()

        if res_pronostico.status_code == 200:
            for item in data_pronostico['list']:
                fecha = datetime.strptime(item['dt_txt'], '%Y-%m-%d %H:%M:%S')
                dia = fecha.strftime('%A')
                
                if dia not in pronostico_por_dia:
                    pronostico_por_dia[dia] = []

                temp = item['main']['temp']
                descripcion = item['weather'][0]['description']
                pronostico_por_dia[dia].append({'fecha': item['dt_txt'], 'temp': temp, 'descripcion': descripcion })
    
    return render_template('index.html', ciudad=ciudad, pronostico_por_dia=pronostico_por_dia, clima_actual=clima_actual)

if __name__ == '__main__':
    app.run(debug=True)
