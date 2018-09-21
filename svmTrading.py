import pandas as pd
import sys
import numpy as np
from datetime import datetime
from math import sqrt
from sklearn.externals import joblib

filename = sys.argv[1]

res = pd.read_csv(filename)
principal = 100000.0
costM = 1 - 0.001

pos = {'qty': 0.0, 'v': principal, 'transaction': 0, 'direction': 0.0, 'bid': 0.0, 'ask': 0.0, 'total': principal, 'side': -1}
ts = pd.DataFrame([pos])
clf = joblib.load("svm/clf")

def order(tick, side, ts):
    lastT = ts.iloc[-1]
    if (side == -1 and lastT.v != 0):
        executionValue = min(principal * 0.1, lastT.v)
        return(ts.append({'v': lastT.v - executionValue, 'qty': lastT.qty + executionValue / tick['ap1'] * costM, 'transaction': lastT.transaction + 1, 'bid': tick['bp1'], 'ask': tick['ap1'], 'side': side, 'total': lastT.v + lastT.qty * lastT['bid']}, ignore_index = True))
    elif (side == 1 and lastT.qty != 0):
        executionQty = min(lastT.qty, principal * 0.1 / tick['bp1'])
        return(ts.append({'v': lastT.v + executionQty * tick['bp1'] * costM, 'qty': lastT.qty - executionQty, 'transaction': lastT.transaction + 1, 'bid': tick['bp1'], 'ask': tick['ap1'], 'side': side, 'total': lastT.v + lastT.qty * lastT['bid']}, ignore_index = True))
    else:
        return ts
        
if __name__ == "__main__":
    #u = res['pred'].quantile(1.0 - threshold)
    #l = res['pred'].quantile(threshold)
    for index,tick in res.iterrows():
        #print(tick['pred'])
        if tick['pred']  == 2:
            ts = order(tick, -1, ts)
        if tick['pred']  == -2:
            ts = order(tick, 1, ts)
    lastT = ts.iloc[-1]
    print(((lastT.v + lastT.qty * lastT['bid'])/100000 - 1) * 100)
    print("transactions: " + str(lastT.transaction))
    ts.to_csv('pos.csv', index = False)