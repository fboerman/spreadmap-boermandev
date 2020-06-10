from flask import Flask, make_response, jsonify, render_template
from werkzeug.middleware.proxy_fix import ProxyFix
from logging.config import dictConfig
import os
from secrets import SECRET_KEY_FLASK
import pandas as pd
from util import import_RIVM_csv
from colour import Color
from math import ceil, floor

if "gunicorn" in os.environ.get("SERVER_SOFTWARE", ""):
    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.FileHandler',
            'filename' : 'app.log',
            'formatter': 'default'
        }},
        'root': {
            'level': 'DEBUG',
            'handlers': ['wsgi']
        }
    })

app = Flask(__name__)
app.secret_key = SECRET_KEY_FLASK
app.wsgi_app = ProxyFix(app.wsgi_app)


@app.route("/NL/")
def index_nl():
    return render_template('base_map.html',
                           geojson="gemeente_2019.geojson",
                           centerpoint="[52.2, 5.387]",
                           propname="statnaam",
                           title="Corona virus verspreiding over Nederland",
                           helptext="Hover over een gemeente")


def get_selected_df(fname):
    df = import_RIVM_csv(fname)
    df.set_index('Gemeente', inplace=True)
    df_BevAant = pd.read_csv('base/gemeente_2019_mensen.csv', delimiter=';')
    df_BevAant.set_index('Gemeente', inplace=True)

    df.index = df.index.str.strip()
    df_BevAant.index = df_BevAant.index.str.strip()
    df = pd.merge(df, df_BevAant, left_index=True, right_index=True)
    df.index = ["'s-Gravenhage" if c == 's-Gravenhage' else c for c in df.index]
    df['AantalNorm'] = round(df['Aantal'] / (df['BevAant'] / 100000), 1)
    df.drop('BevAant', inplace=True, axis=1)

    NUMBIN = 25
    white = Color("gray")
    colors = list(white.range_to(Color("darkred"), NUMBIN))
    colors = [c.hex for c in colors]
    BINSIZE = ceil(df['Aantal'].max() / NUMBIN)

    df2 = df.apply(lambda row: pd.Series({
        'ColorAantal': colors[floor(row['Aantal']/BINSIZE)],
        'ColorAantalNorm': colors[floor(row['AantalNorm'] / BINSIZE)],
    }), axis=1)

    df = pd.merge(df, df2, left_index=True, right_index=True)

    df.rename({
        'Aantal': 'aantal',
        'AantalNorm': 'aantal_norm',
        'ColorAantal': 'color_aantal',
        'ColorAantalNorm': 'color_aantal_norm'
    }, inplace=True, axis=1)

    return df


@app.route('/NL/data/gemeenten_<date>.json')
def geojson_nl(date):
    df = get_selected_df(date+".csv")
    return jsonify(df.to_dict('index'))
