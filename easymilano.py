from flask import Flask, render_template, request, Response, redirect, url_for, make_response, session 
from flask_session import Session
from ctypes.wintypes import POINT
import json
from re import S
from unittest import skip
from xmlrpc.client import boolean
from numpy import empty, place
import shapely
import urllib.request
# import turtle
# from turtle import color, pos
import pyproj
from pyproj import CRS
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
matplotlib.use('Agg')


app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


from shapely.geometry import Polygon, LineString, MultiPoint, MultiLineString, Point, MultiPolygon, shape
import requests
import contextily
import geopandas as gpd
from geopandas import points_from_xy
import pandas as pd
import io

from functools import partial
import pyproj
from shapely.ops import transform

#___________________________________________________________________________________________________________________________________________________________________________________________________________________________
# Dichiarazioni dei geodataframe
dati = pd.read_csv("./static/file/dati.csv",on_bad_lines=skip,engine='python')

quartieri = gpd.read_file('./static/file/ds964_nil_wm-20220405T093028Z-001.zip')

uffici_postali = gpd.read_file('./static/file/ds555_uffici_postali_milano_final.geojson')

comandi_polizialocale = gpd.read_file('./static/file/geocoded_comandi-decentrati-polizia-locale__final.geojson')

scuole = gpd.read_file('./static/file/CITTA_METROPOLITANA_MILANO_-_Scuole_di_ogni_ordine_e_grado.csv', epsg=3857)
scuole_geometry = gpd.GeoDataFrame()

reg_logout = "./static/images/images route/register.png"

@app.route('/', methods=['GET'])
def home():
    if not session.get('email'):
        session["boolean_user"] = bool(False)
    else:
        session["boolean_user"] = bool(True)
        session['value'] = int()
    return render_template('home.html',boolean = session["boolean_user"])

# _______________________________________________________________________

    # register

# _____________________________________________________________________
@app.route('/register', methods=['GET', 'POST'])
def register():
# prende il nome della via inserita dall'utente e tramite openstreetmap prende le coordinate separatamente, in modo da creare poi il punto quando serve.
    def get_place(via_input, citta="milano"):
        via_input = '+'.join(via_input.lower().split())
        place = requests.get(f"https://nominatim.openstreetmap.org/search?q={via_input},+{citta},+milano&format=json&polygon=1&addressdetails=1").json()
        #se c'è invece viene creato post, un dizionario con 2 coordinate.
        if (len(place) != 0):
            post = {"lng": float(place[0]['lon']), "lat": float(place[0]['lat'])}
            #print(pos)
            return post
        else:
            #se non esiste ritornerà None.
            return None

    if request.method == 'GET':
        
        return render_template('register.html')
    else:
        #prende i diversi dati dal html(register)
        name = request.form.get("name") 
        surname = request.form.get("surname")
        psw = request.form.get("pwd")
        cpsw = request.form.get("cpwd")
        email = request.form.get("email")
        if cpsw!= psw: #Controlla se la password inserita e ripetuta sono uguali
            return render_template('register.html') #Controllo fallito 
        else: #Controllo riuscito con esito positivo
            #si fa il controllo se la via effettivamente esiste o meno, se non esite, riporta al register
            if get_place(request.form.get("via")) == None:
                return render_template('register.html')
            # forniamo 2 variabili vuote da riempire con le 2 coordinate
            lng = get_place(request.form.get("via"))['lng']
            lat = get_place(request.form.get("via"))['lat'] # prende lat e la porta nella funzione get_place, diventa via_input essendo il primo qualcosa
            print(lng)
            print(lat)
            tupla_point = (lng,lat)
            session['tupla_point'] = tupla_point
            # creazione del punto
            points = Point(session['tupla_point'][0], session['tupla_point'][1])
            print(points)
            # creazione del dizionario
            #creo una sessione con valore booleano, servirà per controllare se si ha effettuato il login i meno

            # dati_session = [{"email":email,"points": points,"post":get_place(request.form.get("via")),"place":place,'via':request.form.get("via"),'lat':lat,'boolean_user':session["boolean_user"]}]
            # dati_session = dati_session.append(dati_session,ignore_index=True)

            #creamo utente, in modo da poter appendere nel file csv i dati ricevuti dalla registrazione dell'utente.
            utente = [{"name": name,"surname":surname,"psw": psw,"email":email,'lng':lng,'lat':lat,'geometry':points,"points": points,"post":get_place(request.form.get("via")),"place":place,'via':request.form.get("via"),'boolean_user':session["boolean_user"]}]
            
            
            dati = pd.read_csv("./static/file/dati.csv",on_bad_lines=skip,engine='python')
            # append dei dati forniti
            data = dati.append(utente,ignore_index=True)
            # trasportarli nel file csv a cui si riferisce
            data.to_csv('./static/file/dati.csv',index=False)
            
            return redirect(url_for('login'))
# _______________________________________________________________________

    # login


# _______________________________________________________________________
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        check_login = bool(True)
        session['check_login'] = check_login
        l_psw = request.form.get("pwd")
        l_email = request.form.get("email")
        session['l_psw'] = l_psw
        l_psw = session['l_psw'] 
        session['l_email'] = l_email
        l_email =session['l_email']  
        #ridefinisco dati
        dati = pd.read_csv("./static/file/dati.csv",on_bad_lines=skip,engine='python')
        user= dati[(dati['email'] == l_email) & (dati['psw'] == l_psw)]
        session['user'] = user
        #se user è vuoto, significa che non trova l'utente,se le trova invece si parte con la creazione delle sessioni.
        if len(user) != 0 :
            session['email'] = l_email
            session['psw'] = l_psw
            print(session['email'])
            print(session['psw'])
            session['name'] = dati[dati["email"] == l_email]["name"]
            session['surname'] = dati[dati['email'] == l_email]['surname']
            session['lng'] = dati[dati["email"] == l_email]["lng"]
            session['lat'] = dati[dati["email"] == l_email]["lat"]
            session['geometry'] = dati[dati["email"] == l_email]["geometry"]
            
        # altre session provenienti da register/login e openstreetmap
            session['post'] = dati[dati["email"] == l_email]["post"]
            session['points'] = dati[dati["email"] == l_email]["points"]
            session['place'] = dati[dati["email"] == l_email]["place"]
            session['via'] = dati[dati["email"] == l_email]["via"]
            session['boolean_user'] = dati[dati["email"] == l_email]["boolean_user"]
            session["boolean_user"] = bool(True)

            print(session['geometry'])
            print(session['psw'])
            print(session['lng'])
            print(session['lat'])
            print(session['boolean_user'])
            return render_template('home.html', boolean = session["boolean_user"])
        else:
           print(dati['psw'])
           print(dati['email'])
        return render_template("login.html",check_login = bool(False))


@app.route("/logout")
def logout():
    #al logout vengono rese nulle tutte le sessioni, in modo da poter ricominciare il processo alla registrazione/login successiva/o
    session['email'] = None
    session['psw'] = None
    session['lng'] = None
    session['lat'] = None
    session['geometry'] = None
    session['post'] = None
    session['points'] = None
    session['place'] = None
    session['via'] = None
    session['boolean_user'] = None
    session['scelta'] = None
    session['lista_qt'] = None
    session['sceltaposte'] = None
    session['rangevarposte'] = None
    session['sceltapolice'] = None
    session['rangevar'] = None
    session['Grado'] = None
    session['NIL_utente'] = None
    session['name'] = None
    session['surname'] = None
    session['value'] = None
    session['check_login'] = None
    print(session['email'])
    print(session['psw'])
    print(session['lat'])
    print(session['lng'])
    return redirect(url_for('home'))
    #assegna a tutte le variabili un valore non noto 
# _______________________________________________________________________


# quartieri


# _______________________________________________________________________
@app.route('/quartieri', methods=['GET'])
def quartieriFunzione():

    return render_template('quartieriFunzione.html')


@app.route('/selezione', methods=['GET'])
def selezione():
    quartieri = gpd.read_file('./static/file/ds964_nil_wm-20220405T093028Z-001.zip')
    lista_qt = quartieri.NIL.to_list() #creazione di una lista con soltanto la colonna NIL
    session['lista_qt'] = lista_qt
    scelta = request.args["radio"] #Riferimaneto sulla funzione scelta
    session['scelta'] = scelta
    if session['scelta'] == "1":
        return render_template('scelta.html', quartieri=quartieri.NIL.sort_values(ascending=True))#Mette in ordine quartieri basandosi sulla colonna NIL in maniera alfabetica
    elif session['scelta'] == "2":
        session['value'] = 9
        return render_template('scelta.html', quartieri=quartieri.NIL.sort_values(ascending=True))
    elif session['scelta'] == "4":
        session['value'] = 8
# portiamo da tab in modo tale che si possano caricare le informazioni come una tabella(inserire nome della funzione, non della route)
        return redirect(url_for("tab"))
        

@app.route('/visualizzaqt', methods=['GET'])
def visualizzaqt():
    nome_quartiere = request.args["quartiere"] #Chiede valore di quartiere 
    quartiere = quartieri[quartieri.NIL.str.contains(nome_quartiere)]#variabile che contine tutti i dati di quartiere es.geometry
    session['quartiere'] = quartiere
    print(session['quartiere'])
    return render_template('mappafinaleqt.html')#Visualizzazione della mappa del quartiere


@app.route('/mappa', methods=['GET'])
def mappa():
    session['scelta']
    session['value']
    #quartiere sarà uguale alla session quartiere
    quartiere = session['quartiere']
    #inzia il filtraggio tramite il valore dati in precedenza durante la scelta del radiobutton
    if session['scelta'] == "1":
        print(session['scelta'])
        session['value']
        fig, ax = plt.subplots(figsize=(12, 8))
        quartiere.to_crs(epsg=3857).plot(ax=ax, alpha=0.5, edgecolor='k')
        contextily.add_basemap(ax=ax)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')
    #dava errore, utilizzo value, un'altro valore dato nel medesimo punto
    elif session['value'] == 8:
        print(session['scelta'])
        session['value']
        lng = session['lng'].values[0]
        lat = session['lat'].values[0]
        lng = gpd.GeoSeries(lng)
        lat = gpd.GeoSeries(lat)
        print(lng)
        print(lat)
        
        fig, ax = plt.subplots(figsize = (12,8))
        pointz = Point(lng.values[0],lat.values[0])
        gpd.GeoSeries([pointz], crs='EPSG:4326').to_crs('EPSG:3857').plot(ax=ax, color='red')
        quart_in = quartieri[quartieri.contains(pointz)]
        quart_in.to_crs('EPSG:3857').plot(ax = ax, alpha=0.5)
        contextily.add_basemap(ax=ax)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')
    elif session['value'] == 9:
        print(session['scelta'])
        fig, ax = plt.subplots(figsize=(12, 8))
        QtConfinanati = quartieri[quartieri.touches(quartiere.geometry.squeeze())]
        QtConfinanati.to_crs(epsg=3857).plot(ax=ax, facecolor='r')
        quartiere.to_crs(epsg=3857).plot(ax=ax, alpha=0.5, edgecolor='k')
        contextily.add_basemap(ax=ax)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')
# _______________________________________________________________________
# poste
# _______________________________________________________________________


@app.route('/poste', methods=['GET'])
def posteFunzione():
    return render_template('posteFunzione.html')

@app.route('/selezione2', methods=['GET'])
def selezione2():
    sceltaposte = request.args["radio"]
    session['sceltaposte'] = sceltaposte
    if session['sceltaposte'] == "1":
        session['value'] = 1
        return render_template("sceltaPosteAction.html", quartieri=quartieri.NIL.sort_values(ascending=True),sceltaposte = 1)
    elif session['sceltaposte'] == "2":
        session['value'] = 2
        rangevarposte = request.args['rangeposte'] # valore dall' input range
        session['rangevarposte'] = rangevarposte #session['rangevarposte'] assume il valore di rangevarposte
        sceltaposte = 2
        return redirect(url_for("tab"))
        #alternativa durante il tentativo di usare i valori nella route
        # return redirect(f'/mappaposte/2/{range}')
    elif session['sceltaposte'] == "3":
        session['value'] = 3
        sceltaposte = 3
        return redirect(url_for("tab"))
        # return render_template("mappafinaleposte.html",sceltaposte = 3)
        # return redirect(f'/mappaposte/3/None')
@app.route('/mappaposte', methods=['GET'])
def root_mappaposte():
    # poste in qt selto
    if session['sceltaposte'] == "1":
        NIL_utente = request.args["quartiere"]
        print(NIL_utente)
        session['NIL_utente'] = NIL_utente
        print(session['NIL_utente'])
    #quartiere che contiene nel nome il valore selezionato(che equivale al nome grazie a {{quartiere}} nell'html)
        quartiere = quartieri[quartieri.NIL.str.contains(session['NIL_utente'])]
        uffici_postali_nil = uffici_postali[uffici_postali.NIL.str.contains(session['NIL_utente'])]

        # immagine
        fig, ax = plt.subplots(figsize=(12, 8))

        uffici_postali_nil.to_crs(epsg=3857).plot(ax=ax, color='r')
        quartiere.to_crs(epsg=3857).plot(ax=ax, alpha=0.5)
        contextily.add_basemap(ax=ax)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')

        #range
    elif session['sceltaposte'] == "3":
        fig, ax = plt.subplots(figsize=(12, 8))

        uffici_postali.to_crs(epsg=3857).plot(ax=ax, color='r')#tutte le poste
        quartieri.to_crs(epsg=3857).plot(ax=ax, alpha=0.5)
        contextily.add_basemap(ax=ax)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')

    elif session['sceltaposte'] == "2":
        session['rangevarposte']
        #trasformiamo il valore del range in un intero
        range_int= int(session['rangevarposte'])
        print(range_int)

        #____________________     
        # s.values[n]           |
        # s.to_list()[n]        |<------------------vari modi per prendere il valore numerico di una series
        # s.to_numpy()[n]      | 
        # list(s)[n]          |
        #____________________
        
        #prendiamo il valore delle sesioni lng e lat, che equivalgono al valore numerico della latitudine e della longitudine
        lng = session['lng'].values[0]
        lat = session['lat'].values[0]
        lng = gpd.GeoSeries(lng)
        lat = gpd.GeoSeries(lat)
        print(lng)
        print(lat)


        fig, ax = plt.subplots(figsize = (12,8))
        #creazione del punto tramite le coordinate
        point = Point(lng.values[0],lat.values[0])
        #geoeseries del punto, convertiamo l'epsg, da 4326(valore attribuito automaticamente da openstreetmap) a 3857
        gpd.GeoSeries([point], crs='EPSG:4326').to_crs('EPSG:3857').plot(ax=ax, color='red')
        #troviamo le distanze tra la nostra posizione e le varie poste
        dist = uffici_postali.to_crs('EPSG:5234').distance(point)
        print(dist)
        #effettuo il calcolo in proporzione
        poste_range = uffici_postali[uffici_postali.distance(point)<=range_int/1000]
        print(poste_range)
        #immagine
        poste_range.to_crs('EPSG:3857').plot(ax = ax)
        contextily.add_basemap(ax=ax)
        ax.set_axis_off()
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')

# _______________________________________________________________________
# polizia
# _______________________________________________________________________


@app.route('/polizia', methods=['GET'])
def polizia():
    return render_template("PoliziaFunzione.html")


@app.route('/selezione3', methods=['GET'])
def selezione3():
    sceltapolice = request.args["scelta"]
    session['sceltapolice'] = sceltapolice
    if session['sceltapolice'] == "1":
        session['value'] = 4
        return render_template("sceltaPoliziaAction.html", quartieri=quartieri.NIL.sort_values(ascending=True),sceltapolice = 1)
    elif session['sceltapolice'] == "2":
        rangevar = request.args['range2']
        session['rangevar'] =rangevar
        session['value'] = 5
        return redirect(url_for("tab"))
    elif session['sceltapolice'] == "3":
        session['value'] = 6
        return redirect(url_for("tab"))

@app.route('/mappapolizia', methods=['GET'])
def mappapolizia():

    if session['sceltapolice'] == "1":
        NIL_utente = request.args["quartiere"]
        session['NIL_utente_police'] = NIL_utente
        quartiere = quartieri[quartieri.NIL.str.contains(session['NIL_utente_police'])]
        uffici_polizia_nil = comandi_polizialocale[comandi_polizialocale.NIL.str.contains(session['NIL_utente_police'])]

        # immagine
        fig, ax = plt.subplots(figsize=(12, 8))

        uffici_polizia_nil.to_crs(epsg=3857).plot(ax=ax, color='k')
        quartiere.to_crs(epsg=3857).plot(ax=ax, alpha=0.5)
        contextily.add_basemap(ax=ax)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')

    elif session['sceltapolice'] == "2":
        session['rangevar']
        range_int= int(session['rangevar'])
        print(range_int)

        lng = session['lng'].values[0]
        lat = session['lat'].values[0]
        lng = gpd.GeoSeries(lng)
        lat = gpd.GeoSeries(lat)
        print(lng)
        print(lat)


        fig, ax = plt.subplots(figsize = (12,8))
        point = Point(lng.values[0],lat.values[0])
        gpd.GeoSeries([point], crs='EPSG:4326').to_crs('EPSG:3857').plot(ax=ax, color='red')
        dist = comandi_polizialocale.to_crs('EPSG:5234').distance(point)

        session['dist'] = dist #distanza in metri
        print(dist)
        #correzione dell'unità di misura per la distanza
        police_range = comandi_polizialocale[comandi_polizialocale.distance(point)<=range_int/1000] 
        print(police_range)
        police_range.to_crs('EPSG:3857').plot(ax = ax)
        contextily.add_basemap(ax=ax)
        ax.set_axis_off()
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')  

    elif session['sceltapolice'] == "3":
        fig, ax = plt.subplots(figsize=(12, 8))
        comandi_polizialocale.to_crs(epsg=3857).plot(ax=ax, color='k')
        quartieri.to_crs(epsg=3857).plot(ax=ax, alpha=0.5)
        contextily.add_basemap(ax=ax)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')
@app.route('/table.png', methods=['GET'])
def tab():
    #filtraggio per la creazione delle mappe e tabelle
    if session['value'] == 9:
        #quartieri limitrofi
        #passiamo i dati che necessità per creare poi la mappa nella route finale
            lng = session['lng'].values[0]
            lat = session['lat'].values[0]
            lng = gpd.GeoSeries(lng)
            lat = gpd.GeoSeries(lat)
            QtConfinanati = quartieri[quartieri.touches(quartiere.geometry.squeeze())]
            tabella = quartieri[quartieri.contains(QtConfinanati)][['NIL']]
            return render_template("mappafinaleqt.html", table = tabella.to_html())
    elif session['value'] == 8:
        #quartiere in cui ti trovi
            lng = session['lng'].values[0]
            lat = session['lat'].values[0]
            lng = gpd.GeoSeries(lng)
            lat = gpd.GeoSeries(lat)
            pointz = Point(lng.values[0],lat.values[0])
            tabella = quartieri[quartieri.contains(pointz)][['NIL']]
            return render_template("mappafinaleqt.html", table = tabella.to_html())

    elif session['value'] == 7:
        #mostrare i comandi di polizia del quartiere scelto
            tabella = comandi_polizialocale[['Polizia Locale -  Comandi decentrati','Indirizzo','email']]
            return render_template("scelta.html", table = tabella.to_html())
    elif session['value'] == 6:
        #tutti i comandi di polizia
        tabella = comandi_polizialocale[['Polizia Locale -  Comandi decentrati','Indirizzo','email']]
        return render_template("mappafinalepolizia.html", table = tabella.to_html())
    elif session['value'] == 5:
        #range polizia
        session['rangevar']
        range_int= int(session['rangevar'])
        print(range_int)
        lng = session['lng'].values[0]
        lat = session['lat'].values[0]
        lng = gpd.GeoSeries(lng)
        lat = gpd.GeoSeries(lat)
        point = Point(lng.values[0],lat.values[0])

        dist2 = comandi_polizialocale[comandi_polizialocale.distance(point)<=range_int/1000]
        session['dist2'] = dist2
        print(session['dist2'])
        tabella =session['dist2'][['Polizia Locale -  Comandi decentrati','Indirizzo','email']]
        print(tabella)
        return render_template("mappafinalepolizia.html", table = tabella.to_html())
    elif session['value'] == 3:
        #tutte le poste
        tabella = uffici_postali[['Ente','Indirizzo','Telefono']]
        return render_template("mappafinaleposte.html", table = tabella.to_html())
    elif session['value'] == 2:
        #range poste
        session['rangevarposte']
        range_int= int(session['rangevarposte'])
        lng = session['lng'].values[0]
        lat = session['lat'].values[0]
        lng = gpd.GeoSeries(lng)
        lat = gpd.GeoSeries(lat)
        point = Point(lng.values[0],lat.values[0])

        dist2 = uffici_postali[uffici_postali.distance(point)<=range_int/1000]
        session['dist2'] = dist2
        print(session['dist2'])
        tabella =session['dist2'][['Ente','Indirizzo','Telefono']]
        print(tabella)
        return render_template("mappafinaleposte.html", table = tabella.to_html())

@app.route('/scuole', methods=['GET'])
def SceltaGrado():
    return render_template("SceltaGrado.html", gradi=sorted(list([" ".join(s.split("'")) for s in list(scuole.Tipologia.drop_duplicates())])))


@app.route('/Gradoselezionato', methods=['GET'])
def Gradoselezionato():
    Grado = request.args["grado"]
    #session Grado assume il valore della scelta dell'utente
    session['Grado'] = Grado
    if session['Grado'] == "Ctp":
        return render_template("mappafinalescuole.html")
    elif session['Grado'] == "Istituto Istruzione Primario":
        return render_template("mappafinalescuole.html")
    elif session['Grado'] == "Istituto Istruzione Secondario Primo grado":
        return render_template("mappafinalescuole.html")
    elif session['Grado'] == "Scuola dell Infanzia":
        return render_template("mappafinalescuole.html")
    elif session['Grado'] == "Istituto Istruzione Secondario Secondo grado":
        return render_template("mappafinalescuole.html")


@app.route('/mappascuole', methods=['GET'])
def mappascuole():
    Grado = session['Grado']
    if Grado == "Ctp":
        #milano=quartieri[quartieri.intersects(quartieri.unary_union)]
        #prendiamo le scuole del grado scelto
        scuola_geo = scuole[scuole["Tipologia"] == Grado]
        print(scuola_geo.crs)
        #creazione del punto tramite le 2 coordinate
        scuola_geo = gpd.GeoDataFrame(scuola_geo, geometry=gpd.points_from_xy(
            scuola_geo["coorX"], scuola_geo["coorY"]))#creazione di un punto prendendo come dati prima la longitudine (x) e poi la latitudine (y)

        # immagine
        fig, ax = plt.subplots(figsize=(12, 8))

        scuola_geo.set_crs(epsg=4236).to_crs(epsg=3857).plot(ax=ax, color='r')
        print(scuola_geo)
        quartieri.to_crs(epsg=3857).plot(ax=ax, alpha=0.5)
        contextily.add_basemap(ax=ax, crs=3857)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')

    elif Grado == "Istituto Istruzione Primario":
        scuola_geo = scuole[scuole["Tipologia"] == Grado]
        print(scuola_geo.crs)
        scuola_geo = gpd.GeoDataFrame(scuola_geo, geometry=gpd.points_from_xy(
            scuola_geo["coorX"], scuola_geo["coorY"])) #creazione di un punto prendendo come dati prima la longitudine (x) e poi la latitudine (y)

        # immagine
        fig, ax = plt.subplots(figsize=(12, 8))

        scuola_geo.set_crs(epsg=4236).to_crs(epsg=3857).plot(ax=ax, color='r')
        print(scuola_geo)
        quartieri.to_crs(epsg=3857).plot(ax=ax, alpha=0.5)
        contextily.add_basemap(ax=ax, crs=3857)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')

    elif Grado == "Istituto Istruzione Secondario Primo grado":
        scuola_geo = scuole[scuole["Tipologia"] == Grado]
        print(scuola_geo.crs)
        scuola_geo = gpd.GeoDataFrame(scuola_geo, geometry=gpd.points_from_xy(
         scuola_geo["coorX"], scuola_geo["coorY"]))

        # immagine
        fig, ax = plt.subplots(figsize=(12, 8))

        scuola_geo.set_crs(epsg=4236).to_crs(epsg=3857).plot(ax=ax, color='r')
        print(scuola_geo)
        quartieri.to_crs(epsg=3857).plot(ax=ax, alpha=0.5)
        contextily.add_basemap(ax=ax, crs=3857)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')
    
    elif Grado == "Istituto Istruzione Secondario Secondo grado":
        scuola_geo = scuole[scuole["Tipologia"] == Grado]
        print(scuola_geo.crs)
        scuola_geo = gpd.GeoDataFrame(scuola_geo, geometry=gpd.points_from_xy(
         scuola_geo["coorX"], scuola_geo["coorY"])) #creazione di un punto prendendo come dati prima la longitudine (x) e poi la latitudine (y)

        # immagine
        fig, ax = plt.subplots(figsize=(12, 8))

        scuola_geo.set_crs(epsg=4236).to_crs(epsg=3857).plot(ax=ax, color='r')
        print(scuola_geo)
        quartieri.to_crs(epsg=3857).plot(ax=ax, alpha=0.5)
        contextily.add_basemap(ax=ax, crs=3857)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')


    elif Grado == "Scuola dell Infanzia":
        scuola_geo = scuole[scuole["Tipologia"] ==  "Scuola dell'Infanzia"]
        scuola_geo = gpd.GeoDataFrame(scuola_geo, geometry=gpd.points_from_xy(
         scuola_geo["coorX"], scuola_geo["coorY"]))

        # immagine
        fig, ax = plt.subplots(figsize=(12, 8))

        scuola_geo.set_crs(epsg=4236).to_crs(epsg=3857).plot(ax=ax, color='r')
        print(scuola_geo)
        quartieri.to_crs(epsg=3857).plot(ax=ax, alpha=0.5)
        contextily.add_basemap(ax=ax, crs=3857)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3245, debug=True)
