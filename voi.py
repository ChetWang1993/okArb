import pandas as pd

qty = 0
remainingValue = 100000
def order(depth, value, side):
    if (side == -1 and remainingValue != 0) or (side == 1 and qty != 0):
        return {'remainingValue': 0, 'qty': remainingValue / depth['ap1'] if side == -1 else remainingValue / depth['bp1']}

def getPriceDiff(idx):
    return coef['b0'] + coef['b1'] * res.iloc[idx]['voi'] + coef['b2'] * res.iloc[idx - 1]['voi'] + coef['b3'] * res.iloc[idx - 2]['voi'] + coef['b4'] * res.iloc[idx - 3]['voi'] + coef['b5'] * res.iloc[idx - 4]['voi'] + coef['b6'] * res.iloc[idx - 5]['voi']
        
if __name__ == "__main__":
    res = pd.read('btc-depth-20180827')
    res['voi'] = [getVoi(x) for x in res]
    for idx in [5 + x for x in range(len(res) - 5)]:
        diff = getPriceDiff(idx)
        if abs(diff) > 0.2:
            pos = order(remainingValue, 1 if diff > 0.2 else -1) if remainingValue > 0
            qty = pos['qty']
            remainingValue = pos['qty']
    print(remainingValue)
