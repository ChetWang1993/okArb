import pandas as pd
import sys
from datetime import datetime

filename = sys.argv[1]
roundtime = int(sys.argv[2])
res = pd.read_csv(filename)
res['time'] = pd.Series(datetime.fromtimestamp(x) for x in res['timestamp'])
res['time'] = pd.Series(x.replace(second = x.second/roundtime *roundtime, microsecond=0) for x in res['time'])
res = res.set_index('time')
res = res.groupby(level=0).first()

qty = 0.0
remainingValue = 100000.0
transaction = 0
costM = 1
def order(tick, side):
    print({'diff': tick['midDiffMa'], 'side': side, 'qty': qty, 'remainingValue': remainingValue})
    if (side == -1 and remainingValue != 0):
        return {'remainingValue': 0.0, 'qty': remainingValue / tick['ap1'] * costM}
    if (side == 1 and qty != 0):
        return {'remainingValue': qty * tick['bp1'] * costM, 'qty': 0}
    return {'remainingValue': remainingValue , 'qty': qty}

def getPriceDiff(idx):
    return coef['b0'] + coef['b1'] * res.iloc[idx]['voi'] + coef['b2'] * res.iloc[idx - 1]['voi'] + coef['b3'] * res.iloc[idx - 2]['voi'] + coef['b4'] * res.iloc[idx - 3]['voi'] + coef['b5'] * res.iloc[idx - 4]['voi'] + coef['b6'] * res.iloc[idx - 5]['voi']
        
if __name__ == "__main__":
    for index,tick in res.iterrows():
        #print(abs(tick['midDiffMa']))
        #0.00059361 * res['OI'] + 0.00061418 * res['OI1'] + 0.00065906 * res['OI2'] + 0.00064134 * res['OI3'] + 0.00073954 * res['OI4'] + 0.00013306 * res['OI5'] + 0.0108149578065
        #diff = 0.233 * tick['OI'] + 0.342 * tick['OI1'] + 0.365 * tick['OI2'] + 0.389 * tick['OI3'] + 0.336 * tick['OI4'] + 0.494 * tick['OI5'] + 0.0202803706875
        diff = 0.00453 * tick['OI'] + 0.0106 * tick['OI1'] + 0.0191 * tick['OI2'] + 0.0329 * tick['OI3'] + 0.0295 * tick['OI4'] + 0.0193 * tick['OI5'] + 0.312
        if abs(tick['midDiffMa']) > 0.1:
            pos = order(tick, -1 if tick['midDiffMa']> 0.25 else 1)
            transaction = transaction + 1
            print(pos)
            qty = pos['qty']
            remainingValue = pos['remainingValue']
    print(((remainingValue + qty * res.iloc[-1]['bp1'])/100000 - 1) * 100)
    print(transaction)