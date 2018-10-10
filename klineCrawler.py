# encoding: UTF-8

import time
import datetime
from func import *

# 将时间戳转化为标准时间
def to_localtime(strap):
    time_local = time.localtime(strap)
    dt = time.strftime("%Y-%m-%d %H:%M:%S",time_local)
    return dt


symbol = "btg_usd"

startDate = datetime.datetime(2018,7,17)
klines = getSpotKline(symbol, time.mktime(startDate.timetuple()) * 1000, '1min')      # 获取 K 线
# strap = klines[0][0]/1000		# 币安时间戳除以1000可获得正确时间戳

# 比对官网数据，发现返回值前六项的含义以及对应顺序：时间戳，开，高，低，收，量
with open(symbol + '.csv', 'w') as f:
    f.write('Timestamp,datetime,symbol,high,low,open,close,volume')
    f.write('\n')
    for element in klines:
        real_stamp = element[0]/1000        # 观察发现币安时间戳其实是1000倍的时间戳
        real_time = to_localtime(real_stamp)       # 转化为标准时间
        f.write(str(real_stamp) + ',' + str(real_time) + ',' + symbol + ',' + str(element[2]) + ',' + str(element[3]) + ',' + str(element[1]) + ',' + str(element[4]) + ',' + str(element[5]))
        f.write('\n')
