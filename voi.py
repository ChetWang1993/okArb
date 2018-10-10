import pandas as pd
import sys
import numpy as np
from datetime import datetime

filename = sys.argv[1]
roundtime = int(sys.argv[2])

res = pd.read_csv(filename)
resx=res[['OI','OI1','OI2','OI3','OI4','OI5', 'OIS','OIS1','OIS2','OIS3','OIS4','OIS5']]
resx['c']=1
coef = np.array(pd.read_csv('c.csv'))
res['diff'] = resx.dot(coef.T)

res['time'] = pd.Series(datetime.fromtimestamp(x) for x in res['timestamp'])
res['time'] = pd.Series(x.replace(second = x.second/roundtime *roundtime, microsecond=0) for x in res['time'])
res = res.set_index('time')
res = res.groupby(level=0).first()

qty = 0.0
remainingValue = 100000.0
transaction = 0
costM = 1-0.002

def order(tick, side, transaction):
    #print({'diff': tick['midDiffMa'], 'side': side, 'qty': qty, 'remainingValue': remainingValue})
    if (side == -1 and remainingValue != 0):
        transaction = transaction + 1
        return {'remainingValue': 0.0, 'qty': remainingValue / tick['ap1'] * costM, 'transaction': transaction}
    if (side == 1 and qty != 0):
        transaction = transaction + 1
        return {'remainingValue': qty * tick['bp1'] * costM, 'qty': 0, 'transaction': transaction}
    return {'remainingValue': remainingValue , 'qty': qty, 'transaction': transaction}

def getPriceDiff(idx):
    return coef['b0'] + coef['b1'] * res.iloc[idx]['voi'] + coef['b2'] * res.iloc[idx - 1]['voi'] + coef['b3'] * res.iloc[idx - 2]['voi'] + coef['b4'] * res.iloc[idx - 3]['voi'] + coef['b5'] * res.iloc[idx - 4]['voi'] + coef['b6'] * res.iloc[idx - 5]['voi']
        
if __name__ == "__main__":
    u = res['diff'].quantile(0.975)
    l = res['diff'].quantile(0.025)
    print(u)
    print(l)
    for index,tick in res.iterrows():
        if tick['diff'] > u:
            pos = order(tick, -1, transaction)
            qty = pos['qty']
            remainingValue = pos['remainingValue']
            transaction = pos['transaction']
        if tick['diff'] < l:
            pos = order(tick, 1, transaction)
            qty = pos['qty']
            remainingValue = pos['remainingValue']
            transaction = pos['transaction']
    print(((remainingValue + qty * res.iloc[-1]['bp1'])/100000 - 1) * 100)
    print(transaction)