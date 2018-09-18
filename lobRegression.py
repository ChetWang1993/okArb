#-*-coding:utf-8-*-

import pandas as pd
import numpy as np
import sys
from datetime import datetime
from sklearn import linear_model

filename = sys.argv[1]
roundtime = int(sys.argv[2])
data = pd.read_csv(filename, header = 0)
data['time'] = pd.Series(datetime.fromtimestamp(x) for x in data['timestamp'])
data['time'] = pd.Series(x.replace(second = x.second/roundtime *roundtime, microsecond=0) for x in data['time'])
data = data.set_index('time')
data = data.groupby(level=0).first()

VB = []
VA = []
weight = np.array([9/45.0,9/45.0,9/45.0,7/45.0,6/45.0,5/45.0,4/45.0,3/45.0,2/45.0,1/45.0]).T
#weight = np.array([1.0,0,0,0,0,0,0,0,0,0]).T

for i in range(1,len(data)):
    if data['bp1'][i]<data['bp1'][i-1]:
        VB.append((np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])*weight).sum())
    elif data['bp1'][i]==data['bp1'][i-1]:
        VB.append(((np.array(data[['bv1','bv2','bv3','bv4','bv5','bv6','bv7','bv8','bv9','bv10']][i:i+1]) - np.array(data[['bv1','bv2','bv3','bv4','bv5','bv6','bv7','bv8','bv9','bv10']][i-1:i]))*weight).sum())
    elif data['bp1'][i]>data['bp1'][i-1]:
        VB.append(((np.array(data[['bv1', 'bv2', 'bv3', 'bv4', 'bv5', 'bv6', 'bv7', 'bv8', 'bv9', 'bv10']][i:i + 1]))*weight).sum())


for i in range(1,len(data)):
    if data['ap1'][i]>data['ap1'][i-1]:
        VA.append((np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])*weight).sum())
    elif data['ap1'][i]==data['ap1'][i-1]:
        VA.append(((np.array(data[['av1','av2','av3','av4','av5','av6','av7','av8','av9','av10']][i:i+1]) - np.array(data[['av1','av2','av3','av4','av5','av6','av7','av8','av9','av10']][i-1:i]))*weight).sum())
    elif data['ap1'][i]<data['ap1'][i-1]:
        VA.append(((np.array(data[['av1','av2','av3','av4','av5','av6','av7','av8','av9','av10']][i:i + 1]))*weight).sum())


OI = (np.array(VB) - np.array(VA))
OI = np.insert(OI, 0, 0)
dp_var = (data['bp1'][0:] +data['ap1'][0:])/2
dp_var = np.ediff1d(dp_var)
dp_var = np.insert(dp_var, 0, 0)

n = 5
data['OI'] = OI
data['OI1'] = data['OI'].shift(1)
data['OI2'] = data['OI'].shift(2)
data['OI3'] = data['OI'].shift(3)
data['OI4'] = data['OI'].shift(4)
data['OI5'] = data['OI'].shift(5)
data['OI6'] = data['OI'].shift(6)
data['midDiff'] = dp_var
data['midDiffMa'] = pd.rolling_mean(data.midDiff, 6)
data = data.fillna(0)
data.to_csv(filename, index=False)

regr = linear_model.LinearRegression(normalize = True,copy_X = True)
y = np.array(data['midDiffMa']).reshape(-1, 1)
x = np.array(data[['OI', 'OI1', 'OI2', 'OI3', 'OI4', 'OI5']])
    #x = OI[n - i:len(OI) - i].reshape(-1, 1)
regr.fit(x, y)
print('--R2='+ str(regr.score(x,y,sample_weight=None))+ '--coef=' + str(regr.coef_[0]) + '--intercept='+str(regr.intercept_[0]))