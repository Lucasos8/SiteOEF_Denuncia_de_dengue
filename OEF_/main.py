from flask import Flask, render_template, url_for, request
import pandas as pd
import requests
import os
import folium
#Temos usar o comando "pip install" no CMD para baixar o openpyxl, pandas, folium e o flask.

app = Flask(__name__)

@app.route("/")
def pag_home():
    return render_template("home.html")


@app.route("/sobre")
def pag_sobre():
    return render_template("sobre.html")


@app.route("/cadastro")
def pag_cadastro():
    return render_template("cadastro.html")


@app.route("/mapa")
def pag_mapa():
    pag_imagemMapa()
    return render_template("mapa.html")


@app.route("/imagemMapa")
def pag_imagemMapa():
    # Cria um mapa centrado em uma localização
    mapa = folium.Map(location=[-19.93167, -44.05361], zoom_start=13.5)

    # Lê o arquivo xlsx e extrai as coordenadas
    df = pd.read_excel('dados.xlsx')

    # Adiciona um marcador para cada par de coordenadas no dataframe
    for index, row in df.iterrows():
        folium.Circle(
            radius=280,
            location=[row['Latitude'], row['Longitude']],
            opacity=0,
            FILLOpacity=0.5,
            FILLColor="crimson",  
            color="crimson",
            fill=True,
        ).add_to(mapa)

    # Salva o mapa como uma string HTML
    mapa.save("static/imagemMapa.html")

    return render_template("imagemMapa.html")

@app.route('/submit', methods=['POST'])
def form():
    nome = request.form['nome']# pegando dados do forms
    rua = request.form['rua']
    numero = request.form['numero']
    bairro = request.form['bairro']
    cidade = request.form['cidade']
    estado = request.form['estado']
    
    latitude, longitude = obter_coordenadas(f"{rua}, {numero}, {bairro}, {cidade}, {estado}, Brasil")

    data = {
            'Nome': [nome],
            'Rua': [rua],
            'Numero': [numero],
            'Bairro': [bairro],
            'Cidade': [cidade],
            'Estado': [estado],
            'Latitude': [str(latitude).replace(',', '.')],
            'Longitude': [str(longitude).replace(',', '.')]
        }
    # convertendo os dados do form em um DataFrame do pandas
    dataFrame = pd.DataFrame(data)

    # conferindo se o arquivo já existe
    if os.path.isfile('dados.xlsx'):
        # caso o arquivo xls já existe

        dadosExistentes = pd.read_excel('dados.xlsx')
        # concatene os dados existentes com os novossalvados em dataFrame
        dados = pd.concat([dadosExistentes, dataFrame])
    else:
        # caso não exista, começa agora recebendo de dataFrame
        dados = dataFrame
        
    # aqui é onde GRAVA o dataFrame criado acima na planilha xls
    dados.to_excel('dados.xlsx', index=False)

    return pag_mapa()

def obter_coordenadas(endereco):
    #chave de API do Google Maps
    api_key = "Coloca sua chave aqui."

    # URL da API do Google Maps
    url = "https://maps.googleapis.com/maps/api/geocode/json"

    
    params = {
        "address": endereco,
        "key": api_key
    }

    #Solicitação GET para a API do Google Maps
    response = requests.get(url, params=params)
    data = response.json()

    # Verificando se a solicitação foi bem-sucedida
    if response.status_code == 200:
        # Extraindo as coordenadas de latitude e longitude
        results = data.get("results", [])
        if results:
            location = results[0].get("geometry", {}).get("location", {})
            latitude = location.get("lat")
            longitude = location.get("lng")
            return latitude, longitude


app.run(debug=True)