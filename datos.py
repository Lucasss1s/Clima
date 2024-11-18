import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta


# Funciones para traer el clima actual y a 5 dias
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





# Scrap para obtener datos del clima del mes actual
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

    #print(df_clima.head(30))  

else:
    print(f'Error al acceder a la página: {response.status_code}')
