import pandas as pd
import os
from datetime import datetime,date


def import_RIVM_csv(fname):
    # fname = "RIVM_timeseries/{}.csv".format(d_str)
    d = datetime.strptime(fname.split('.')[0], '%d%m%Y').date()
    if d <= date(year=2020, month=3, day=11):
        df = pd.read_csv('RIVM_timeseries/' + fname, delimiter=';')
        del df['id']
        del df['Indicator']
        df.fillna(0, inplace=True)
    elif d == date(year=2020, month=3, day=12):
        df = pd.read_csv('RIVM_timeseries/' + fname, delimiter=';', skiprows=[2, 3], skip_blank_lines=True)
        del df['Gemnr']
    elif d <= date(year=2020, month=3, day=16):
        df = pd.read_csv("RIVM_timeseries/" + fname, delimiter=';', skiprows=[2, 3], skip_blank_lines=True,
                         index_col=False, usecols=['Gemeente', 'Aantal'])
    elif d <= date(year=2020, month=3, day=30):
        df = pd.read_csv("RIVM_timeseries/" + fname, delimiter=';', skiprows=[2], skip_blank_lines=True,
                         index_col=False, usecols=['Gemeente', 'BevAant', 'Aantal'])
        if df['Aantal'].sum() > 17e6:
            # column mix up, so swap the two
            df['Aantal'] = df['BevAant']
        df.drop('BevAant', axis=1, inplace=True)
    elif d <= date(year=2020, month=4, day=7):
        df = pd.read_csv("RIVM_timeseries/" + fname, delimiter=';', skiprows=[], skip_blank_lines=True,
                         index_col=False, usecols=['Gemeente', 'BevAant', 'Aantal'])
        if df['Aantal'].sum() > 17e6:
            # column mix up, so swap the two
            df['Aantal'] = df['BevAant']
        df.drop('BevAant', axis=1, inplace=True)
    else:
        df = pd.read_csv("RIVM_timeseries/" + fname, delimiter=';', skiprows=[], skip_blank_lines=True,
                         index_col=False, usecols=['Gemeente', 'Zkh opname'])
        df.rename(columns={'Zkh opname': 'Aantal'}, inplace=True)
    # df = df.T
    # df.index = [d]
    return df


def import_brazil_csv(dname):
    d = datetime.strptime(dname, '%d%m%Y')
    df = pd.read_csv('brazil-states.csv', delimiter=';', parse_dates=['time'])
    df = df[df['time'] == d]
    df.set_index('state', inplace=True)
    df.drop('time', axis=1, inplace=True)

    return df
