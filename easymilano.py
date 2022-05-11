
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
# importazioni necessarie per street map
from shapely.geometry import Polygon, LineString, MultiPoint, MultiLineString, Point, MultiPolygon, shape
import requests
import contextily
import geopandas as gpd
from geopandas import points_from_xy
import pandas as pd
import io
import os
import csv
import datetime
from flask import Flask, render_template, request, Response, redirect, url_for
import json
app = Flask(__name__)
matplotlib.use('Agg')

# Dichiarazioni dei geodataframe
dati = pd.read_csv("./static/file/dati.csv")

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
# for _, r in scuole:
# for _, r in scuole:

# metro = gpd.read_file('./static/file/tpl_metropercorsi.geojson')


# home e registrazione

# a
@app.route('/', methods=['GET'])
def home():

    return render_template('home.html')

# _______________________________________________________________________

    # register


# _____________________________________________________________________
@app.route('/register', methods=['GET', 'POST'])
def register():
    global point, pos, points

    def get_place(via_input, citta="milano"):
        via_input = '+'.join(via_input.lower().split())
        place = requests.get(
            f"https://nominatim.openstreetmap.org/search?q={via_input},+{citta}&format=json&polygon=1&addressdetails=1").json()

        if (len(place) != 0):
            pos = {"lng": float(place[0]['lon']),
                   "lat": float(place[0]['lat'])}
            return pos
        else:
            return None

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

        utente = [{"name": name, "surname": surname,
                   "psw": psw, "email": email, "via": via}]

        global point
        res = get_place(via)
        if res == None:
            return "<h1>error</h1>"
        else:
            global point
            point = gpd.GeoSeries(
                [Point((res["lng"], res["lat"]))], crs='epsg:3857')
        global points
        points = gpd.GeoDataFrame(gpd.GeoSeries(point))
        points = points.rename(
            columns={0: 'geometry'}).set_geometry('geometry')

        print(points)
        # pointscuole = gpd.GeoSeries([Point((scuole["coorX"], scuole["CoorY"]))], crs='epsg:3857')

        # controllo password
        if cpsw != psw:
            return 'le password non corrispondono'
        else:
            dati_append = dati.append(utente, ignore_index=True)
            dati_append.to_csv('./static/file/dati.csv', index=False)
            return render_template('login.html', name=name, surname=surname, psw=psw, via=via, utente=utente, email=email)


# test

@app.route('/test', methods=['GET', 'POST'])
def test():
    return points.to_html()
# _______________________________________________________________________

    # login


# _______________________________________________________________________
@app.route('/login', methods=['GET', 'POST'])
def login():

    # dichiarazione di df. legge il file json creato per preservare i dati degli utenti
    # login sistemato---
    # ciclo for di controllo alternativo
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        psw = request.form.get("pwd")
        email = request.form.get("email")
        print(psw, email)

    for _, r in dati.iterrows():
        if email == r['email'] and psw == r['psw']:
            return '<h1>login effettuato </h1>'

    return '<h1>Errore</h1>'


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
        return render_template('mappafinaleqt.html', quartieri=lista_qt)


@app.route('/visualizzaqt', methods=['GET'])
def visualizzaqt():
    global quartiere
    nome_quartiere = request.args["quartiere"]
    quartiere = quartieri[quartieri.NIL.str.contains(nome_quartiere)]
    if scelta == "3":
        area = quartiere.geometry.area/10**6
        return render_template('Lunghezzaqt.html', area=area)
    elif scelta == "4":
        tuoquart = quartieri[quartieri.within(points.gemetry.squeeze())]
        return render_template('mappafinaleqt.html', tuoquart=tuoquart)
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
        fig, ax = plt.subplots(figsize=(12, 8))
        points.to_crs(epsg=3857).plot(ax=ax, color='r')
        quartiere.to_crs(epsg=3857).plot(ax=ax, alpha=0.5, edgecolor='k')
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
        return render_template("sceltaPosteAction.html", quartieri=quartieri.NIL.sort_values(ascending=True))
    elif scelta == "2":
        return render_template("posteFunzione.html")
    elif scelta == "3":
        return render_template("mappafinaleposte.html")


@app.route('/mappaposte', methods=['GET'])
def mappaposte():
    # poste in qt selto

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
    elif scelta == "2":
        range = request.args['range']
        range2 = int(range)
        print(range2)
        myrange_poste = uffici_postali[uffici_postali.distance(
            points.unary_union) <= range2]
        # immagine
        fig, ax = plt.subplots(figsize=(12, 8))
        points.to_crs(epsg=3857).plot(ax=ax, color='r')
        myrange_poste.to_crs(epsg=3857).plot(ax=ax, alpha=0.5)
        contextily.add_basemap(ax=ax)
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
    global scelta
    scelta = request.args["scelta"]
    if scelta == "1":
        return render_template("sceltaPoliziaAction.html", quartieri=quartieri.NIL.sort_values(ascending=True))
    elif scelta == "2":
        return render_template()
    elif scelta == "3":
        return render_template("mappafinalepolizia.html")


@app.route('/mappapolizia', methods=['GET'])
def mappapolizia():

    if scelta == "1":
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

    elif scelta == "2":

        return render_template()
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
