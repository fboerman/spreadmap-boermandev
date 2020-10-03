import pandas as pd
import os
from datetime import datetime, timedelta


def import_RIVM_csv(dname):
    df = pd.read_csv('RIVM_timeseries/gemeenten_2weken/latest.csv', skip_blank_lines=True, delimiter=';')
    df.drop(['Gemnr', 'Bev_2020', 'van_datum'], axis=1, inplace=True)
    df['tot_datum'] = pd.to_datetime(df['tot_datum'], format='%d-%m-%Y')
    df.rename(columns={'tot_datum': 'time'}, inplace=True)
    df.sort_values(['time', 'Gemeente'], inplace=True)
    df['Totaal_inc100000'] = df['Totaal_inc100000'].str.replace(',', '.').astype(float)
    df['Zkh_inc100000'] = df['Zkh_inc100000'].str.replace(',', '.').astype(float)
    df['Overleden_inc100000'] = df['Overleden_inc100000'].str.replace(',', '.').astype(float)
    #df['Gemeente'] = df['Gemeente'].apply(lambda x: x.split('(')[0].strip() if ' (' in x else x)

    if dname == 'max':
        return df, df[df['time'] == df['time'].max()]
    else:
        d = datetime.strptime(dname, '%Y%m%d')
        periods = [(x-timedelta(days=13),x) for x in pd.to_datetime(df['time'].unique())]
        periods_search = [x[0] <= d <= x[1] for x in periods]
        if not any(periods_search):
            # outside of data range
            return None, None

        selected_period = periods[periods_search.index(True)]
        return df, df[df['time'] == selected_period[1]]


def import_brazil_csv(dname):
    d = datetime.strptime(dname, '%Y%m%d')
    df = pd.read_csv('brazil-states.csv', delimiter=';', parse_dates=['time'])
    df = df[df['time'] == d]
    df.set_index('state', inplace=True)
    df.drop('time', axis=1, inplace=True)

    return df
