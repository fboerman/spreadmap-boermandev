from flask import Flask, make_response, jsonify, render_template, abort
from werkzeug.middleware.proxy_fix import ProxyFix
from logging.config import dictConfig
import os
from secrets import SECRET_KEY_FLASK
import pandas as pd
from util import import_RIVM_csv, import_brazil_csv
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
                           zoom_level="8",
                           propname="statnaam",
                           data_prefix="gemeenten",
                           title="Corona virus verspreiding over Nederland",
                           helptext="Hover over een gemeente")


@app.route("/NL/hotspots/")
def index_nl_hotspots():
    return render_template('base_map.html',
                           geojson="gemeente_2019.geojson",
                           centerpoint="[52.2, 5.387]",
                           zoom_level="8",
                           propname="statnaam",
                           data_prefix="gemeentenhotspots",
                           title="Corona hotspots (>30 besmettingen per 100.000 afgelopen 2 weken)",
                           helptext="Hover over een gemeente")


@app.route("/BRA/")
def index_bra():
    return render_template('base_map.html',
                           geojson="states_bra.geojson",
                           centerpoint="[-11.39, -53.85]",
                           zoom_level="5",
                           propname="name",
                           data_prefix="states",
                           title="Corona virus spread over Brasil",
                           helptext="Hover over a state")

 #Totaal_Absoluut, Totaal_inc100000

def fix_names(df):
    return df.rename({
        "'s-Gravenhage (gemeente)": "'s-Gravenhage",
        "Groningen (gemeente)": "Groningen",
        "Hengelo (O.)": "Hengelo",
        "Utrecht (gemeente)": "Utrecht",
        "Laren (NH.)": "Laren",
        "Rijswijk (ZH.)": "Rijswijk",
        "Middelburg (Z.)": "Middelburg",
        "Beek (L.)": "Beek",
        "Stein (L.)": "Stein"
    })

def get_selected_df_nl(dname):
    df_all, df = import_RIVM_csv(dname)
    if df_all is None:
        return None

    NUMBIN = 25
    white = Color("gray")
    colors = list(white.range_to(Color("darkred"), NUMBIN))
    colors = [c.hex for c in colors]
    BINSIZE_Aantal = ceil(df_all['Totaal_Absoluut'].max() / NUMBIN)
    BINSIZE_AantalNorm = ceil(df_all['Totaal_inc100000'].max() / NUMBIN)

    df2 = df.apply(lambda row: pd.Series({
        'color_Totaal_Absoluut': colors[floor(row['Totaal_Absoluut']/BINSIZE_Aantal)],
        'color_Totaal_inc100000': colors[floor(row['Totaal_inc100000'] / BINSIZE_AantalNorm)],
    }), axis=1)

    df = pd.merge(df, df2, left_index=True, right_index=True)
    df.set_index('Gemeente', inplace=True)
    df = fix_names(df)

    # df.rename({
    #     'Aantal': 'aantal',
    #     'AantalNorm': 'aantal_norm',
    #     'ColorAantal': 'color_aantal',
    #     'ColorAantalNorm': 'color_aantal_norm'
    # }, inplace=True, axis=1)

    return df

def get_hotspots_df_nl():
    df_all, df = import_RIVM_csv('max')
    if df_all is None:
        return None

    df.loc[:, 'color_hotspot'] = df.apply(
        lambda row: Color('darkred').get_hex() if row['Totaal_inc100000'] > 30 else Color('white').get_hex()
        , axis=1)
    df.set_index('Gemeente', inplace=True)
    df.rename({'Totaal_inc100000': 'hotspot'}, axis=1, inplace=True)
    df = fix_names(df)
    return df

def get_selected_df_bra(date):
    df = import_brazil_csv(date)

    NUMBIN = 25
    white = Color("gray")
    colors = list(white.range_to(Color("darkred"), NUMBIN))
    colors = [c.hex for c in colors]

    for c in ['cases_cum', 'deaths_cum', 'cases_cum_norm', 'deaths_cum_norm']:
        BINSIZE = ceil(df[c].max() / NUMBIN)
        df['color_'+c] = df.apply(lambda row: colors[floor(row[c]/BINSIZE)], axis=1)

    return df


@app.route('/NL/data/gemeenten_<date>.json')
def json_nl(date):
    try:
        df = get_selected_df_nl(date)
    except ValueError:
        return abort(400)
    if df is None:
        return abort(404)
    return jsonify(df.to_dict('index'))


@app.route('/NL/hotspots/data/gemeentenhotspots_<date>.json')
def hotspots_json_nl(date):
    try:
        df = get_hotspots_df_nl()
    except ValueError:
        return abort(400)
    if df is None:
        return abort(404)
    return jsonify(df.to_dict('index'))


@app.route('/BRA/data/states_<date>.json')
def json_bra(date):
    df = get_selected_df_bra(date)
    return jsonify(df.to_dict('index'))
