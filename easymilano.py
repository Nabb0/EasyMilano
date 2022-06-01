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


#importazioni necessarie per street map



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


# Dichiarazioni dei geodataframe
dati = pd.read_csv("./static/file/dati.csv",on_bad_lines=skip,engine='python')

quartieri = gpd.read_file(
    './static/file/ds964_nil_wm-20220405T093028Z-001.zip')

mezzi_superficie = gpd.read_file('./static/file/tpl_percorsi.geojson')

uffici_postali = gpd.read_file(
    './static/file/ds555_uffici_postali_milano_final.geojson')

# vie_milano =

comandi_polizialocale = gpd.read_file(
    './static/file/geocoded_comandi-decentrati-polizia-locale__final.geojson')

scuole = gpd.read_file(
    './static/file/CITTA_METROPOLITANA_MILANO_-_Scuole_di_ogni_ordine_e_grado.csv', epsg=3857)
scuole_geometry = gpd.GeoDataFrame()

reg_logout = "./static/images/images route/register.png"
@app.route('/', methods=['GET'])
def home():
    return render_template('home.html', boolean_user = False)

# _______________________________________________________________________

    # register


# _____________________________________________________________________
@app.route('/register', methods=['GET', 'POST'])
def register():
# prende il nome della via inserita dall'utente e tramite openstreetmap prende le coordinate separatamente, in modo da creare poi il punto quando serve.
    def get_place(via_input, citta="milano"):
        via_input = '+'.join(via_input.lower().split())
        place = requests.get(f"https://nominatim.openstreetmap.org/search?q={via_input},+{citta},+milano&format=json&polygon=1&addressdetails=1").json()
        if (len(place) != 0):
            post = {"lng": float(place[0]['lon']), "lat": float(place[0]['lat'])}
            #print(pos)
            return post
        else:
            return None

    if request.method == 'GET':
        
        return render_template('register.html')
    else:
        name = request.form.get("name")
        surname = request.form.get("surname")
        psw = request.form.get("pwd")
        cpsw = request.form.get("cpwd")
        email = request.form.get("email")
        if cpsw!= psw:
            return 'le password non corrispondono'
        else:
            if get_place(request.form.get("via")) == None:
                return render_template('register.html')
            # forniamo 2 variabili vuote da riempire con le 2 coordinate
            lng = get_place(request.form.get("via"))['lng']
            lat = get_place(request.form.get("via"))['lat'] # prende lat e la porta nella funzione get_place, diventa via_input essendo il primo qualcosa
            print(lng)
            print(lat)
            tupla_point = (lng,lat)
            session['tupla_point'] = tupla_point
            #print(tupla_point)
            # creazione del punto
            points = Point(session['tupla_point'][0], session['tupla_point'][1])

            print(points)
            # creazione del dizionario
            session["boolean_user"] = bool(False)
            # dati_session = [{"email":email,"points": points,"post":get_place(request.form.get("via")),"place":place,'via':request.form.get("via"),'lat':lat,'boolean_user':session["boolean_user"]}]
            # dati_session = dati_session.append(dati_session,ignore_index=True)

            utente = [{"name": name,"surname":surname,"psw": psw,"email":email,'lng':lng,'lat':lat,'geometry':points,"points": points,"post":get_place(request.form.get("via")),"place":place,'via':request.form.get("via"),'boolean_user':session["boolean_user"]}]
            
            # append dei dati forniti
            dati = dati.append(utente,ignore_index=True)
            # trasportarli nel file csv a cui si riferisce
            dati.to_csv('./static/file/dati.csv',index=False)

            return redirect(url_for('login'))
# _______________________________________________________________________

    # login


# _______________________________________________________________________
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        l_psw = request.form.get("pwd")
        l_email = request.form.get("email")
        # session['l_psw'] = l_psw
        # session['l_email'] = l_email
        
        user= dati[(dati['email'] == l_email) & (dati['psw'] == l_psw)]
        session['user'] = user
        if len(user) != 0 :
            session['email'] = dati[dati['email'] == l_email]['email']
            session['psw'] = dati[dati['psw'] == l_psw]['psw']
            print(session['email'])
            print(session['psw'])
            session['name'] = dati[dati["email"] == l_email]["name"]
            session['surname'] = dati[dati['email'] == l_email]['surname']
            session['lng'] = dati[dati["email"] == l_email]["lng"]
            session['lat'] = dati[dati["email"] == l_email]["lat"]
            session['geometry'] = dati[dati["email"] == l_email]["geometry"]
            
        # session provenienti da register/login
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
            return render_template('home.html', boolean_user = True)
        else:
           print(dati['psw'])
           print(dati['email'])
        return('<h1>Utente insesistente, riprova.</h1>')


@app.route("/logout")
def logout():
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
    print(session['email'])
    print(session['psw'])
    print(session['lat'])
    print(session['lng'])
    return redirect(url_for('home'))
# _______________________________________________________________________


# quartieri


# _______________________________________________________________________
@app.route('/quartieri', methods=['GET'])
def quartieriFunzione():

    return render_template('quartieriFunzione.html')


@app.route('/selezione', methods=['GET'])
def selezione():
    lista_qt = quartieri.NIL.to_list()  # DEVO PER FORZA TRASFORMARE IN LISTA
    session['lista_qt'] = lista_qt
    scelta = request.args["radio"]
    session['scelta'] = scelta
    if session['scelta'] == "1":
        return render_template('scelta.html', quartieri=quartieri.NIL.sort_values(ascending=True))
    elif session['scelta'] == "2":
        return render_template('scelta.html', quartieri=quartieri.NIL.sort_values(ascending=True))
    elif session['scelta'] == "3":
        return render_template('scelta.html', quartieri=quartieri.NIL.sort_values(ascending=True))
    elif session['scelta'] == "4":
        return render_template('mappafinaleqt.html')


@app.route('/visualizzaqt', methods=['GET'])
def visualizzaqt():
    nome_quartiere = request.args["quartiere"]
    quartiere = quartieri[quartieri.NIL.str.contains(nome_quartiere)]
    session['quartiere'] = quartiere
    print(session['quartiere'])
    return render_template('mappafinaleqt.html')


@app.route('/mappa', methods=['GET'])
def mappa():
    session['scelta']
    quartiere = session['quartiere']
    if session['scelta'] == "1":
        fig, ax = plt.subplots(figsize=(12, 8))
        quartiere.to_crs(epsg=3857).plot(ax=ax, alpha=0.5, edgecolor='k')
        contextily.add_basemap(ax=ax)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')

    elif session['scelta'] == '4':
        fig, ax = plt.subplots(figsize=(24, 16))
       
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
        print(quart_in)
        quart_in.to_crs('EPSG:3857').plot(ax = ax, alpha=0.5)
        contextily.add_basemap(ax=ax)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')
    else:
        fig, ax = plt.subplots(figsize=(12, 8))
        QtConfinanati = quartieri[quartieri.touches(
            quartiere.geometry.squeeze())]
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
        return render_template("sceltaPosteAction.html", quartieri=quartieri.NIL.sort_values(ascending=True),sceltaposte = 1)
    elif session['sceltaposte'] == "2":
        rangevarposte = request.args['rangeposte']
        session['rangevarposte'] = rangevarposte
        return render_template("mappafinaleposte.html",sceltaposte = 2)
        # return redirect(f'/mappaposte/2/{range}')
    elif session['sceltaposte'] == "3":
        return render_template("mappafinaleposte.html",sceltaposte = 3)
        # return render_template("mappafinaleposte.html",sceltaposte = 3)
        # return redirect(f'/mappaposte/3/None')
@app.route('/mappaposte', methods=['GET'])
def root_mappaposte():
    # poste in qt selto
    if session['sceltaposte'] == "1":
        NIL_utente = request.args["quartiere"]
        session['NIL_utente'] = NIL_utente
        quartiere = quartieri[quartieri.NIL.str.contains(NIL_utente)]
        uffici_postali_nil = uffici_postali[uffici_postali.NIL.str.contains(NIL_utente)]

        # immagine
        fig, ax = plt.subplots(figsize=(12, 8))

        uffici_postali_nil.to_crs(epsg=3857).plot(ax=ax, color='r')
        quartiere.to_crs(epsg=3857).plot(ax=ax, alpha=0.5)
        contextily.add_basemap(ax=ax)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return render_template("mappafinaleposte.html",sceltaposte = 1)

        #range
    elif session['sceltaposte'] == "3":
        fig, ax = plt.subplots(figsize=(12, 8))

        uffici_postali.to_crs(epsg=3857).plot(ax=ax, color='r')
        quartieri.to_crs(epsg=3857).plot(ax=ax, alpha=0.5)
        contextily.add_basemap(ax=ax)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')
    elif session['sceltaposte'] == "2":
        session['rangevarposte']
        range_int= int(session['rangevarposte'])
        print(range_int)

        #____________________     
        # s.values[n]           |
        # s.to_list()[n]        |<------------------vari modi per prendere il valore numerico di una series
        # s.to_numpy()[n]      | 
        # list(s)[n]          |
        #____________________

        lng = session['lng'].values[0]
        lat = session['lat'].values[0]
        lng = gpd.GeoSeries(lng)
        lat = gpd.GeoSeries(lat)
        print(lng)
        print(lat)


        fig, ax = plt.subplots(figsize = (12,8))
        point = Point(lng.values[0],lat.values[0])
        gpd.GeoSeries([point], crs='EPSG:4326').to_crs('EPSG:3857').plot(ax=ax, color='red')
        dist = uffici_postali.to_crs('EPSG:5234').distance(point)
        print(dist)
        poste_range = uffici_postali[uffici_postali.distance(point)<=range_int/1000]
        print(poste_range)
        poste_range.to_crs('EPSG:3857').plot(ax = ax)
        contextily.add_basemap(ax=ax)
        ax.set_axis_off()
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        # img_poste = urllib.request.urlretrieve("../static/images/img_user/poste/range_poste.jpg")
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
        return render_template("sceltaPoliziaAction.html", quartieri=quartieri.NIL.sort_values(ascending=True),sceltapolice = 1)
    elif session['sceltapolice'] == "2":
        rangevar = request.args['range2']
        session['rangevar'] =rangevar
        return render_template("mappafinalepolizia.html",sceltapolice = 2)
    elif session['sceltapolice'] == "3":
        return render_template("mappafinalepolizia.html",sceltapolice = 3)

@app.route('/mappapolizia', methods=['GET'])
def mappapolizia():

    if session['sceltapolice'] == "1":
        NIL_utente = request.args["quartiere"]
        quartiere = quartieri[quartieri.NIL.str.contains(NIL_utente)]
        uffici_polizia_nil = comandi_polizialocale[comandi_polizialocale.NIL.str.contains(NIL_utente)]

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
        dist = comandi_polizialocale.to_crs('EPSG:5234').distance(point) #distanza in metri
        print(dist)
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
    tabella = uffici_polizia_nil.to_list()
    return render_template("mappafinalepolizia.html", table = tabella)
    
# _______________________________________________________________________
# Scuole non va https://www.dati.lombardia.it/widgets/9pqm-h622
# https://github.com/Nabb0/Python-appunti-ed-esercizi/blob/main/esercizi/Geopandas/Riva_es6.ipynb
# _______________________________________________________________________

@app.route('/scuole', methods=['GET'])
def SceltaGrado():
    return render_template("SceltaGrado.html", gradi=sorted(list([" ".join(s.split("'")) for s in list(scuole.Tipologia.drop_duplicates())])))


@app.route('/Gradoselezionato', methods=['GET'])
def Gradoselezionato():
    Grado = request.args["grado"]
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

    elif Grado == "Istituto Istruzione Primario":
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
