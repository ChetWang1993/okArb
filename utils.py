#!/usr/local/bin/python3
import pandas as pd
import os
root_path = os.path.dirname(os.path.realpath(__file__)) + '/../'
from datetime import timedelta, datetime, date
from jqdatasdk import *
auth('13918125129','fmttm1993')
def get_day_offset(d, offset):
    dates = pd.read_csv('data/trading_days.txt', sep = '\t')
    dates['date'] = pd.to_datetime(dates['date'], format='%Y-%m-%d')
    dates['date'] = dates['date'].dt.date
    idx = dates[dates['date'] == d].index
    idx_offset = idx + offset
    if idx_offset >= 0 and idx_offset <= max(dates.index):
        return list(dates.iloc[idx_offset]['date'])[0]
    return None
def next_bday_from_str(d):
    d = datetime.strptime(d, '%Y%m%d')
    return d + timedelta(3) if d.weekday() == 4 else d + timedelta(1)
def prev_bday_from_str(d):
    d = datetime.strptime(d, '%Y%m%d')
    return d - timedelta(3) if d.weekday() == 0 else d - timedelta(1)
def date_str(d):
    return d[:4] + '-' + d[4:6] + '-' + d[6:]
def get_universe(d):
    t = get_all_securities(types=[], date=d)
    t = t[t['display_name'].str.count('ST') == 0]
    t = t[t['display_name'].str.count('退') == 0]
    rics = [x for x in list(t.index) if x.startswith('60') or x.startswith('00')]
    return rics
def is_bday(d):
    data_path = root_path + 'data/trading_days.txt'
    trading_days = pd.read_csv(data_path, sep = '\t')
    return 0 != trading_days[trading_days['date'] == date_str(d)].size
