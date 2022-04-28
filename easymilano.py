import matplotlib.pyplot as plt
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import contextily
import geopandas as gpd
import pandas as pd
import io
import csv
from flask import Flask, render_template, request, Response, redirect, url_for
app = Flask(__name__)
matplotlib.use('Agg')

# Dichiarazioni dei geodataframe
dati = pd.read_json("/workspace/EasyMilano/static/file/dati.json")

quartieri = gpd.read_file(
    '/workspace/EasyMilano/static/file/ds964_nil_wm-20220405T093028Z-001.zip')
mezzi_superficie = gpd.read_file(
    '/workspace/EasyMilano/static/file/tpl_percorsi.geojson')
uffici_postali = pd.read_csv(
    '/workspace/EasyMilano/static/file/uffici_postali_milano.csv')
civici = pd.read_csv('/workspace/EasyMilano/static/file/civici.csv')
comandi_polizialocale = gpd.read_file(
    '/workspace/EasyMilano/static/file/geocoded_comandi-decentrati-polizia-locale__final.geojson')
scuole = pd.read_csv(
    '/workspace/EasyMilano/static/file/CITTA_METROPOLITANA_MILANO_-_Scuole_di_ogni_ordine_e_grado.csv')
metro = gpd.read_file(
    '/workspace/EasyMilano/static/file/tpl_metropercorsi.geojson')
stradario = pd.read_csv('/workspace/EasyMilano/static/file/stradario (2).csv')

# home e registrazione


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    elif request.method == 'POST':
        name = request.form.get("name")
        surname = request.form.get("surname")
        psw = request.form.get("pwd")
        cpsw = request.form.get("cpwd")
        via = request.form.get("via")
        if psw==cpsw:
            dati.append({name: name,surname:surname,psw:psw,via:via},ignore_index=True)
            dati.to_json("/workspace/EasyMilano/static/file/dati.json")
            
            return render_template('a.html')
        else:
            return "le password non corrispondono"



# verifico se posso scrivere


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3245, debug=True)
