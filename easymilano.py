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

quartieri = gpd.read_file('/workspace/EasyMilano/static/file/ds964_nil_wm-20220405T093028Z-001.zip')

mezzi_superficie = gpd.read_file('/workspace/EasyMilano/static/file/tpl_percorsi.geojson')

uffici_postali = pd.read_csv('/workspace/EasyMilano/static/file/uffici_postali_milano.csv')

civici = pd.read_csv('/workspace/EasyMilano/static/file/civici.csv')

comandi_polizialocale = gpd.read_file('/workspace/EasyMilano/static/file/geocoded_comandi-decentrati-polizia-locale__final.geojson')

scuole = pd.read_csv('/workspace/EasyMilano/static/file/CITTA_METROPOLITANA_MILANO_-_Scuole_di_ogni_ordine_e_grado.csv')
metro = gpd.read_file('/workspace/EasyMilano/static/file/tpl_metropercorsi.geojson')

stradario = pd.read_csv('/workspace/EasyMilano/static/file/stradario (2).csv')

# home e registrazione


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

#_______________________________________________________________________



                        #register

                   
# _____________________________________________________________________
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        name = request.form.get("name")
        surname = request.form.get("surname")
        psw = request.form.get("pwd")
        cpsw = request.form.get("cpwd")
        email = request.form.get("email")
        via = request.form.get("via")
        df = pd.read_json("./static/file/dati.json")
        if cpsw== psw:
            df= df.append({'name': [name],'surname':[surname],'email' : [email], 'psw':[psw],'via':[via]},ignore_index=True)
            df.to_json("./static/file/dati.json")
            return render_template('login.html', name = name, surname = surname, psw = psw , via = via, df = df, email = email)
        else:
            return "le password non corrispondono"
    else:
        return render_template('register.html')
#_______________________________________________________________________



                             #login


#_______________________________________________________________________
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        log_pwd = request.form.get('pwd')
        log_email = request.form.get('email')
        df = pd.read_json("./static/file/dati.json")



        for _, r in df.iterrows():
            if log_email == r['email'] and log_pwd == r['pwd']:  
                return render_template("ok.html")

        return '<h1>Errore</h1>'
    else:
        return render_template('login.html')
#_______________________________________________________________________
#quartieri
#_______________________________________________________________________
@app.route('/quartieri', methods=['GET'])
def quartieriFunzione ():
    return render_template('quartieriFunzione.html')




@app.route('/selezione', methods=['GET'])
def selezione():
    scelta = request.args["radio"]
    if scelta=="1":
        return render_template('input.html')
    elif scelta=="2":
        return render_template()
    elif scelta=="3":
        return render_template()
    elif scelta=="4":
        return render_template()
  

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3245, debug=True)
