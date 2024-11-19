import matplotlib.pyplot as plt
import io
import base64

def grafico_temperaturas(df_clima):
    plt.figure(figsize=(10, 5))
    plt.plot(df_clima['Fecha'], df_clima['Temperatura Máxima'], label="Temp. Máxima", color='red', marker='o')
    plt.plot(df_clima['Fecha'], df_clima['Temperatura Mínima'], label="Temp. Mínima", color='blue', marker='o')
    plt.title('Temperaturas Máximas y Mínimas del Mes')
    plt.xlabel('Días')
    plt.ylabel('Temperatura (°C)')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return f"data:image/png;base64,{graph_url}"

def grafico_estado_clima(df_clima):
    estados = df_clima['Estado del Clima'].value_counts()

    plt.figure(figsize=(8, 6))
    estados.plot(kind='bar', color=['skyblue', 'gray', 'green', 'yellow', 'red'])
    plt.title('Estado del Clima en el Mes')
    plt.xlabel('Estado')
    plt.ylabel('Frecuencia')
    plt.xticks(rotation=45)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return f"data:image/png;base64,{graph_url}"

def grafico_combinado(df_clima):
    plt.figure(figsize=(12, 6))
    
    plt.bar(df_clima['Fecha'], df_clima['Temperatura Máxima'], color='red', alpha=0.6, label='Temp. Máxima')
    plt.bar(df_clima['Fecha'], df_clima['Temperatura Mínima'], color='blue', alpha=0.6, label='Temp. Mínima')
    
    estados_frecuencia = df_clima['Estado del Clima'].value_counts()
    plt.plot(estados_frecuencia.index, estados_frecuencia.values, color='green', label='Frecuencia de Estados', marker='o')
    
    plt.title('Gráfico Combinado: Temperaturas y Estados del Clima')
    plt.xlabel('Días')
    plt.ylabel('Temperatura (°C)')
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return f"data:image/png;base64,{graph_url}"
