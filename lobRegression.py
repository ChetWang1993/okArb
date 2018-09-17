#-*-coding:utf-8-*-

import pandas as pd
import numpy as np
from sklearn import linear_model
data = pd.read_csv("btc-depth-sample.csv",header = 0)

VB = []
VA = []
#weight = np.array([10/45.0,9/45.0,8/45.0,7/45.0,6/45.0,5/45.0,4/45.0,3/45.0,2/45.0,1/45.0]).T
weight = np.array([1.0,0,0,0,0,0,0,0,0,0]).T

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


# 加权平均
# OI = (np.array(VB) - np.array(VA))
# dp_var = (data['bp1'][1:] +data['ap1'][1:])/2
# dp_var_mov = []
# n = 20
# for i in range(n,len(dp_var)):
#     dp_var_mov.append(dp_var[i-n:i-1].mean())
#
# for i in range(0,5):
#     regr = linear_model.LinearRegression(normalize = True,copy_X = True)
#     y = np.array(dp_var_mov).reshape(-1, 1)
#     x = OI[n - i:len(OI) - i].reshape(-1, 1)
#     regr.fit(x, y)
#     print('lag='+ str(i)+'--R2='+ str(regr.score(x,y,sample_weight=None))+ '--' +'coef=' + str(regr.coef_[0][0]))



#不加权平均
OI = (np.array(VB) - np.array(VA))
OI = np.insert(OI, 0, 0)
dp_var = (data['bp1'][0:] +data['ap1'][0:])/2
dp_var = np.ediff1d(dp_var)
dp_var = np.insert(dp_var, 0, 0)

n = 5
data['OI'] = pd.Series(OI)
data['OI1'] = data['OI'].shift(1)
data['OI2'] = data['OI'].shift(2)
data['OI3'] = data['OI'].shift(3)
data['OI4'] = data['OI'].shift(4)
data['OI5'] = data['OI'].shift(5)
data['OI6'] = data['OI'].shift(6)
data['midDiff'] = pd.Series(dp_var)
data['midDiffMa'] = data.midDiff.rolling(5).mean()
data = data.fillna(0)

regr = linear_model.LinearRegression(normalize = True,copy_X = True)
y = np.array(data['midDiffMa']).reshape(-1, 1)
x = np.array(data[['OI', 'OI1', 'OI2', 'OI3', 'OI4', 'OI5']])
    #x = OI[n - i:len(OI) - i].reshape(-1, 1)
regr.fit(x, y)
print('--R2='+ str(regr.score(x,y,sample_weight=None))+ '--' +'coef=' + str(regr.coef_[0][0]))