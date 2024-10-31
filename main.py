from flask import Flask, render_template, request
import requests

app = Flask(__name__)  # iniciar flask

@app.route('/', methods=['GET', 'POST'])
def index():
    ciudad = "" 
    temp = ""    
    descripcion = ""  
    
    if request.method == 'POST':
        ciudad = request.form['ciudad']
        url = "https://api.openweathermap.org/data/2.5/weather?q={}&appid=36702f1bcf086e4be0e9d8ecb12c2147&units=metric".format(ciudad)

        res = requests.get(url)
        data = res.json()

        if res.status_code == 200:  # Verificar que la solicitud fue exitosa
            temp = data["main"]["temp"]
            descripcion = data["weather"][0]["description"]
        else:
            descripcion = "Ciudad no encontrada"

    return render_template('index.html', ciudad=ciudad, temp=temp, descripcion=descripcion)

if __name__ == '__main__':
    app.run(debug=True)
