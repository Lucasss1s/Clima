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
        temp = data['main']['temp']
        descripcion = data['weather'][0]['description']
        return {'temp': temp, 'descripcion': descripcion}


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
