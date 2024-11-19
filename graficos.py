import matplotlib.pyplot as plt

def crear_grafico(pronostico_por_dia):
    dias = list(pronostico_por_dia.keys())
    temps_max = [max(d['temp'] for d in pronostico) for pronostico in pronostico_por_dia.values()]
    plt.figure(figsize=(10, 5))
    plt.plot(dias, temps_max, marker='o')
    plt.title("Temperaturas Máximas por Día")
    plt.xlabel("Días")
    plt.ylabel("Temperatura (°C)")
    plt.grid(visible=True)
    #plt.savefig("static/grafico_temperaturas.png")
    plt.close()