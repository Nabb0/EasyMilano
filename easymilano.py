import matplotlib.pyplot as plt
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import contextily
import geopandas as gpd
import pandas as pd
import io
import os
import csv
from flask import Flask, render_template, request, Response, redirect, url_for
app = Flask(__name__)
matplotlib.use('Agg')

# Dichiarazioni dei geodataframe
dati = pd.read_csv("./static/file/dati.csv")

quartieri = gpd.read_file('./static/file/ds964_nil_wm-20220405T093028Z-001.zip')

mezzi_superficie = gpd.read_file('./static/file/tpl_percorsi.geojson')

uffici_postali = gpd.read_file('./static/file/ds555_uffici_postali_milano_final.geojson')

#vie_milano = 

comandi_polizialocale = gpd.read_file('./static/file/geocoded_comandi-decentrati-polizia-locale__final.geojson')

scuole = pd.read_csv('./static/file/CITTA_METROPOLITANA_MILANO_-_Scuole_di_ogni_ordine_e_grado.csv')
metro = gpd.read_file('./static/file/tpl_metropercorsi.geojson')



# home e registrazione

#a
@app.route('/', methods=['GET'])
def home():

    return render_template('home.html')

#_______________________________________________________________________



                        #register

                   
# _____________________________________________________________________
@app.route('/register', methods=['GET', 'POST'])
def register():

    global utente

    if request.method == 'GET':
        return render_template('register.html')
    else:
        name = request.form.get("name")
        surname = request.form.get("surname")
        psw = request.form.get("pwd")
        cpsw = request.form.get("cpwd")
        email = request.form.get("email")
        via = request.form.get("via")
        civico = request.form.get('civico')
        
        utente = [{"name": name,"surname":surname, "psw": psw,"email":email,"via":via,"civico":civico}]
        
        if cpsw!= psw:
            return 'le password non corrispondono'
        else:
            dati_append = dati.append(utente,ignore_index=True)
            dati_append.to_csv('./static/file/dati.csv',index=False)
            return render_template('login.html', name = name, surname = surname, psw = psw , via = via,utente = utente, email = email, civico = civico)
#_______________________________________________________________________



                             #login


#_______________________________________________________________________
@app.route('/login', methods=['GET', 'POST'])
def login():

    #dichiarazione di df. legge il file json creato per preservare i dati degli utenti

        # ciclo for di controllo alternativo
        if request.method == 'GET':
            return render_template('login.html')
        elif request.method == 'POST':
            psw = request.form.get("pwd")
            email = request.form.get("email")
            print(psw, email)

            for _, r in dati.iterrows():
                if email == r["email"] and psw == r["psw"]:  
                    return '<h1>Login</h1>'

            return '<h1>Errore</h1>'


#_______________________________________________________________________


#quartieri


#_______________________________________________________________________
@app.route('/quartieri', methods=['GET'])
def quartieriFunzione ():
    return render_template('quartieriFunzione.html')




@app.route('/selezione', methods=['GET'])
def selezione():
 global scelta
 scelta = request.args["radio"]


 if scelta=="1":
    return render_template('scelta.html',quartieri=quartieri.NIL.sort_values(ascending=True))
 elif scelta=="2":
    return render_template('scelta.html',quartieri=quartieri.NIL.sort_values(ascending=True))
 elif scelta=="3":
    return render_template('scelta.html',quartieri=quartieri.NIL.sort_values(ascending=True))
 elif scelta=="4":
  return render_template()#postlogin

@app.route('/visualizzaqt', methods=['GET'])
def visualizzaqt():
 global quartiere
 nome_quartiere=request.args["quartiere"]
 quartiere=quartieri[quartieri.NIL.str.contains(nome_quartiere)]
 quartiere2=quartieri[quartieri.NIL.str.contains(nome_quartiere)]
 if scelta=="3":
    area = quartiere2.geometry.area/10**6
    return render_template('Lunghezzaqt.html',area=area) 
 else:
  return render_template('mappafinaleqt.html') 
 


@app.route('/mappa', methods=['GET'])
def mappa():
 if scelta=="1":
    fig, ax = plt.subplots(figsize = (12,8))
    quartiere.to_crs(epsg=3857).plot(ax=ax, alpha=0.5,edgecolor='k')
    contextily.add_basemap(ax=ax)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')    
 else:
    fig, ax = plt.subplots(figsize = (12,8))
    QtConfinanati=quartieri[quartieri.touches(quartiere.geometry.squeeze())]
    QtConfinanati.to_crs(epsg=3857).plot(ax=ax,facecolor='r')
    quartiere.to_crs(epsg=3857).plot(ax=ax, alpha=0.5,edgecolor='k')
    contextily.add_basemap(ax=ax)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')    
#_______________________________________________________________________
#poste
#_______________________________________________________________________
@app.route('/poste', methods=['GET'])
def posteFunzione():
    return render_template('posteFunzione.html')

@app.route('/selezione2', methods=['GET'])
def selezione2():
 global scelta
 
 scelta = request.args["scelta"]
 if scelta=="1":
    return render_template("sceltaPosteAction.html",quartieri=quartieri.NIL.sort_values(ascending=True))
 elif scelta=="2":
    return render_template()
 elif scelta=="3":
  return render_template("mappafinaleposte.html")
 

@app.route('/mappaposte', methods=['GET'])
def mappaposte():
    #poste in qt selto
    
 if scelta=="1":
  NIL_utente = request.args["quartiere"]
  quartiere=quartieri[quartieri.NIL.str.contains(NIL_utente)]
  uffici_postali_nil=uffici_postali[uffici_postali.NIL.str.contains(NIL_utente)]

  #immagine
  fig, ax = plt.subplots(figsize = (12,8))
    
  uffici_postali_nil.to_crs(epsg=3857).plot(ax=ax,color  = 'r')
  quartiere.to_crs(epsg=3857).plot(ax=ax, alpha= 0.5)
  contextily.add_basemap(ax=ax)
  output = io.BytesIO()
  FigureCanvas(fig).print_png(output)
  return Response(output.getvalue(), mimetype='image/png')    


  return render_template("mappafinaleposte.html")
 elif scelta=="2":
    
    
    return render_template()
 elif scelta=="3":
    fig, ax = plt.subplots(figsize = (12,8))
    
    uffici_postali.to_crs(epsg=3857).plot(ax=ax,color  = 'r')
    quartieri.to_crs(epsg=3857).plot(ax=ax, alpha= 0.5)
    contextily.add_basemap(ax=ax)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')    

#_______________________________________________________________________
#polizia
#_______________________________________________________________________
@app.route('/polizia', methods=['GET'])
def polizia():
    return render_template("PoliziaFunzione.html")

@app.route('/selezione3', methods=['GET'])
def selezione3():
 global scelta
 scelta = request.args["scelta"]
 if scelta=="1":
    return render_template("sceltaPoliziaAction.html",quartieri=quartieri.NIL.sort_values(ascending=True)))
 elif scelta=="2":
    return render_template()
 elif scelta=="3":
  return render_template("mappafinalepolizia.html")

#copia

@app.route('/mappapolizia', methods=['GET'])
def mappapolizia():
    #poste in qt selto
    
 if scelta=="1":
  NIL_utente = request.args["quartiere"]
  quartiere=quartieri[quartieri.NIL.str.contains(NIL_utente)]
  uffici_polizia_nil=comandi_polizialocale[comandi_polizialocale.NIL.str.contains(NIL_utente)]

  #immagine
  fig, ax = plt.subplots(figsize = (12,8))
    
  uffici_polizia_nil.to_crs(epsg=3857).plot(ax=ax,color  = 'k')
  quartiere.to_crs(epsg=3857).plot(ax=ax, alpha= 0.5)
  contextily.add_basemap(ax=ax)
  output = io.BytesIO()
  FigureCanvas(fig).print_png(output)
  return Response(output.getvalue(), mimetype='image/png')    


  return render_template("mappafinaleposte.html")
 elif scelta=="2":
    
    
    return render_template()
 elif scelta=="3":
    fig, ax = plt.subplots(figsize = (12,8))
    
    comandi_polizialocale.to_crs(epsg=3857).plot(ax=ax,color  = 'k')
    quartieri.to_crs(epsg=3857).plot(ax=ax, alpha= 0.5)
    contextily.add_basemap(ax=ax)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')    

 

    




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3245, debug=True)
