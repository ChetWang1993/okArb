#-*-coding:utf-8-*-

import pandas as pd
import numpy as np
import sys
from datetime import datetime
from sklearn import linear_model
from sklearn.svm import SVC, SVR
from sklearn.externals import joblib

filename = sys.argv[1]
threshold = float(sys.argv[2])

data = pd.read_csv(filename, header = 0)
data['mid1'] = (data['bp1'] + data['ap1'])/2
data['mid2'] = (data['bp2'] + data['ap2'])/2
data['mid3'] = (data['bp1'] + data['ap1'])/2
data['mid4'] = (data['bp2'] + data['ap2'])/2
data['mid5'] = (data['bp1'] + data['ap1'])/2

data['diff1'] = (data['ap1'] - data['bp1'])/2
data['diff2'] = (data['ap2'] - data['bp2'])/2
data['diff3'] = (data['ap3'] - data['bp3'])/2
data['diff4'] = (data['ap4'] - data['bp4'])/2
data['diff5'] = (data['ap5'] - data['bp5'])/2

data['mapd'] = data['ap5'] - data['ap1']
data['mbpd'] = data['bp1'] - data['bp5']
data['apd1'] = abs(data['ap1'] - data['ap2'])
data['apd2'] = abs(data['ap2'] - data['ap3'])
data['apd3'] = abs(data['ap3'] - data['ap4'])
data['apd4'] = abs(data['ap4'] - data['ap5'])
data['bpd1'] = abs(data['bp1'] - data['bp2'])
data['bpd2'] = abs(data['bp2'] - data['bp3'])
data['bpd3'] = abs(data['bp3'] - data['bp4'])
data['bpd4'] = abs(data['bp4'] - data['bp5'])

data['mbp'] = 0.2 * (data['bp1'] + data['bp2'] + data['bp3'] + data['bp4'] + data['bp5'])
data['mbv'] = 0.2 * (data['bv1'] + data['bv2'] + data['bv3'] + data['bv4'] + data['bv5'])
data['map'] = 0.2 * (data['ap1'] + data['ap2'] + data['ap3'] + data['ap4'] + data['ap5'])
data['mav'] = 0.2 * (data['av1'] + data['av2'] + data['av3'] + data['av4'] + data['av5'])


data['midDiff'] = data['mid1'].shift(-1) - data['mid1']
u = data['midDiff'].quantile(1.0 - threshold)
l = data['midDiff'].quantile(threshold)

data['direction'] = pd.Series([ 0 if x == 0 else (2 if x >= u else (1 if x > 0 else (-2 if x <= l else -1))) for x in data['midDiff']])
data = data.fillna(0)
ks = ['bp1', 'bv1', 'ap1', 'av1', 'bp2', 'bv2', 'ap2', 'av2', 'bp3', 'bv3', 'ap3', 'av3', 'bp4', 'bv4', 'ap4', 'av4', 'bp5', 'bv5', 'ap5', 'av5']

#data = data[(data['OI'] < data['OI'].quantile(0.9)) & (data['OI'] > data['OI'].quantile(0.1))]
#print("after extreme filtereing: " + str(len(data)))

clf = SVC()
y = np.array(data['direction'])
x = np.array(data[ks])
clf.fit(x, y)
print('--accuracy='+ str(clf.score(x,y,sample_weight=None)))
pred = [clf.predict(x[ks])[0] for idx,x in data.iterrows()]
data['pred'] = pd.Series(pred)
data.to_csv(filename, index=False)
joblib.dump(clf, "svm/clf")
