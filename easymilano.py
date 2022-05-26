
from flask import Flask, render_template, request, Response, redirect, url_for, make_response, session 
from flask_session import Session
from ctypes.wintypes import POINT
import json
from re import S
from unittest import skip
from xmlrpc.client import boolean
from numpy import empty, place
import shapely
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

boolean_user = bool(False)
# for _, r in scuole:
# for _, r in scuole:

# metro = gpd.read_file('./static/file/tpl_metropercorsi.geojson')


# home e registrazione

# a
@app.route('/', methods=['GET'])
def home():
    
    return render_template('home.html', boolean_user = False)

# _______________________________________________________________________

    # register


# _____________________________________________________________________
@app.route('/register', methods=['GET', 'POST'])
def register():
    global point,pos,points, place, via, boolean_user,utente, dati

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
        return render_template('register.html', boolean_user = boolean_user)
    else:
        global utente
        name = request.form.get("name")
        surname = request.form.get("surname")
        psw = request.form.get("pwd")
        cpsw = request.form.get("cpwd")
        email = request.form.get("email")
        if cpsw!= psw:
            return 'le password non corrispondono'
        else:
            global lng, lat
            lng = get_place(request.form.get("via"))['lng']
            lat = get_place(request.form.get("via"))['lat'] # prende lat e la porta nella funzione get_place, diventa via_input essendo il primo qualcosa
            print(lng)
            print(lat)
            tupla_point = (lng,lat)
            #print(tupla_point)
            points = Point(tupla_point[0], tupla_point[1])
            
            print(points)
            utente = [{"name": name,"surname":surname, "psw": psw,"email":email,'lng':lng,'lat':lat,'geometry':points}]
            dati = dati.append(utente,ignore_index=True)
            dati.to_csv('./static/file/dati.csv',index=False)

            return redirect(url_for('login'))

# test

@app.route('/test', methods=['GET', 'POST'])
def test():
    return points.to_html()
# _______________________________________________________________________

    # login


# _______________________________________________________________________
@app.route('/login', methods=['GET', 'POST'])
def login():
    global tupla_point,user
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        l_psw = request.form.get("pwd")
        l_email = request.form.get("email")
        
        user= dati[(dati['email'] == l_email) & (dati['psw'] == l_psw)]
        if len(user) != 0 :
            session['email'] = user['email']
            session['psw'] = user['psw']
            session['lng'] = dati[dati["email"] == l_email]["lng"]
            session['lat'] = dati[dati["email"] == l_email]["lat"]
            session['geometry'] = dati[dati["email"] == l_email]["geometry"]
            boolean_user = bool(True)
            print(session['geometry'])
            print(session['psw'])
            print(session['lng'])
            print(session['lat'])
            print(boolean_user)
            return render_template('home.html', boolean_user = True)
        else: 
           return('<h1>Utente insesistente, riprova.</h1>')


@app.route("/logout")
def logout():
    session['email'] = None
    session['psw'] = None
    session['lng'] = None
    session['lat'] = None
    session['geometry'] = None
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
    global lista_qt, scelta
    lista_qt = quartieri.NIL.to_list()  # DEVO PER FORZA TRASFORMARE IN LISTA
    scelta = request.args["radio"]

    if scelta == "1":
        return render_template('scelta.html', quartieri=quartieri.NIL.sort_values(ascending=True))
    elif scelta == "2":
        return render_template('scelta.html', quartieri=quartieri.NIL.sort_values(ascending=True))
    elif scelta == "3":
        return render_template('scelta.html', quartieri=quartieri.NIL.sort_values(ascending=True))
    elif scelta == "4":
        return render_template('mappafinaleqt.html')


@app.route('/visualizzaqt', methods=['GET'])
def visualizzaqt():
    global quartiere
    nome_quartiere = request.args["quartiere"]
    quartiere = quartieri[quartieri.NIL.str.contains(nome_quartiere)]
    if scelta == "3":
        area = quartiere.geometry.area/10**6
        return render_template('Lunghezzaqt.html', area=area)
    else:
        return render_template('mappafinaleqt.html')


@app.route('/mappa', methods=['GET'])
def mappa():
    if scelta == "1":
        fig, ax = plt.subplots(figsize=(12, 8))
        quartiere.to_crs(epsg=3857).plot(ax=ax, alpha=0.5, edgecolor='k')
        contextily.add_basemap(ax=ax)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')

    elif scelta == '4':
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
    global scelta

    scelta = request.args["radio"]

    if scelta == "1":
        return render_template("sceltaPosteAction.html", quartieri=quartieri.NIL.sort_values(ascending=True),scelta = 1)
    elif scelta == "2":
        return render_template("posteFunzione.html",scelta = 2)
    elif scelta == "3":
        return render_template("mappafinaleposte.html",scelta = 3)


@app.route('/mappaposte', methods=['GET'])
def mappaposte():
    # poste in qt selto
    scelta = request.args["radio"]
    if scelta == "1":
        NIL_utente = request.args["quartiere"]
        quartiere = quartieri[quartieri.NIL.str.contains(NIL_utente)]
        uffici_postali_nil = uffici_postali[uffici_postali.NIL.str.contains(
            NIL_utente)]

        # immagine
        fig, ax = plt.subplots(figsize=(12, 8))

        uffici_postali_nil.to_crs(epsg=3857).plot(ax=ax, color='r')
        quartiere.to_crs(epsg=3857).plot(ax=ax, alpha=0.5)
        contextily.add_basemap(ax=ax)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')

        return render_template("mappafinaleposte.html")
    elif scelta=="2":
        range = request.args['range']
        range_int= int(range)
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
        return Response(output.getvalue(), mimetype='image/png')  

    elif scelta == "3":
        fig, ax = plt.subplots(figsize=(12, 8))

        uffici_postali.to_crs(epsg=3857).plot(ax=ax, color='r')
        quartieri.to_crs(epsg=3857).plot(ax=ax, alpha=0.5)
        contextily.add_basemap(ax=ax)
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
    global scelta,val
    val = 0
    scelta = request.args["scelta"]
    if scelta == "1":
        return render_template("sceltaPoliziaAction.html", quartieri=quartieri.NIL.sort_values(ascending=True),val = 1)
    elif scelta == "2":
        return render_template("sceltaPoliziaAction.html",val = 2)
    elif scelta == "3":
        return render_template("mappafinalepolizia.html",val = 3)


@app.route('/mappapolizia', methods=['GET'])
def mappapolizia():

    if val == "1":
        NIL_utente = request.args["quartiere"]
        quartiere = quartieri[quartieri.NIL.str.contains(NIL_utente)]
        uffici_polizia_nil = comandi_polizialocale[comandi_polizialocale.NIL.str.contains(
            NIL_utente)]

        # immagine
        fig, ax = plt.subplots(figsize=(12, 8))

        uffici_polizia_nil.to_crs(epsg=3857).plot(ax=ax, color='k')
        quartiere.to_crs(epsg=3857).plot(ax=ax, alpha=0.5)
        contextily.add_basemap(ax=ax)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')

    elif val == "2":
        range_int= int(range)
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
        print(poste_range)
        police_range.to_crs('EPSG:3857').plot(ax = ax)
        contextily.add_basemap(ax=ax)
        ax.set_axis_off()
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')  

    elif scelta == "3":
        fig, ax = plt.subplots(figsize=(12, 8))

        comandi_polizialocale.to_crs(epsg=3857).plot(ax=ax, color='k')
        quartieri.to_crs(epsg=3857).plot(ax=ax, alpha=0.5)
        contextily.add_basemap(ax=ax)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')


# _______________________________________________________________________
# Scuole non va https://www.dati.lombardia.it/widgets/9pqm-h622
# https://github.com/Nabb0/Python-appunti-ed-esercizi/blob/main/esercizi/Geopandas/Riva_es6.ipynb
# _______________________________________________________________________

@app.route('/scuole', methods=['GET'])
def SceltaGrado():
    return render_template("SceltaGrado.html", gradi=sorted(list([" ".join(s.split("'")) for s in list(scuole.Tipologia.drop_duplicates())])))


@app.route('/Gradoselezionato', methods=['GET'])
def Gradoselezionato():
    global Grado
    Grado = request.args["grado"]

    if Grado == "Ctp":
        return render_template("mappafinalescuole.html")
    elif Grado == "Istituto Istruzione Primario":
        return render_template("mappafinalescuole.html")
    elif Grado == "Istituto Istruzione Secondario Primo grado":
        return render_template("mappafinalescuole.html")
    elif Grado == "Scuola dell Infanzia":
        return render_template("mappafinalescuole.html")
    elif Grado == "Istituto Istruzione Secondario Secondo grado":
        return render_template("mappafinalescuole.html")


@app.route('/mappascuole', methods=['GET'])
def mappascuole():
    print(Grado)
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3245, debug=True)
