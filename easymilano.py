from flask import Flask,render_template, request, Response, redirect, url_for
app = Flask(__name__)

import io
import pandas as pd
import geopandas as gpd
import contextily
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

#Dichiarazioni dei geodataframe

dati = []

mezzi_superficie=gpd.read_file('/workspace/EasyMilano/static/file/tpl_percorsi.geojson')
uffici_postali=csv.read_file('/workspace/EasyMilano/static/file/uffici_postali_milano.csv')
civici=csv.read_file('/workspace/EasyMilano/static/file/civici.csv')
comandi_polizialocale=csv.read_file('/workspace/EasyMilano/static/file/geocoded_comandi-decentrati-polizia-locale__final.geojson')
scuole=csv.read_file('/workspace/EasyMilano/static/file/CITTA_METROPOLITANA_MILANO_-_Scuole_di_ogni_ordine_e_grado.csv')
metro=
#home e regiistrazione


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3245, debug=True)