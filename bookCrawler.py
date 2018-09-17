# --*-- encoding: utf-8 --*--
# pip install python-binance

import time
import os
from binance.client import Client

APIkey = 'R0546VwwTnhBNXdxi9a9Z7dkRHnCP8DyY0ah8KTDClxZqEOBaFkKgYLTLF8Acow8'
Secretkey = 'J72JCQIxm3RRFDIwFXNWnSlmgKadEqaz184j2sjSeBGLBu9dDZ7kB7ImPR6Jdgqx'
symbol = 'BTCUSDT'		# 交易对的名字
search_num = 10			# 买10卖10

# 首次运行，创建data文件夹
if not os.path.exists(symbol + '_' + 'data/'):
	os.makedirs(symbol + '_' + 'data/')

while True:
	try:
		now_week = time.strftime("%y%m%d")
		
		# 判断文件是否存在
		if os.path.exists(symbol + '_' + 'data/' + str(now_week) + '.csv'):
			f = open(symbol + '_' + 'data/' + str(now_week) + '.csv', 'a+')		# 打开文件（委托买单）
		else:		# 第一次创建文件，写表头信息
			f = open(symbol + '_' + 'data/' + str(now_week) + '.csv', 'a+')
			f.write('timestamp,datetime,')
			for i in range(search_num):
				f.write('bp{},bv{},ap{},av{},'.format(i+1, i+1, i+1, i+1))
			f.write('\n')
		client = Client(APIkey, Secretkey)

		# 获取市场深度信息
		depth = client.get_order_book(symbol=symbol)
		bids = depth['bids']		# 委托买单
		asks = depth['asks']		# 委托卖单


		f.write(str(time.time()) + ',')
		f.write(str(time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))) + ',')
		for i in range(search_num):
			f.write(bids[i][0] + ',' + bids[i][1] + ',')
			f.write(asks[i][0] + ',' + asks[i][1] +  ',')
		print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
		print bids[0], asks[0]
		f.write('\n')
		f.close()

		time.sleep(3)
	except Exception,e:
		print(e)
		print time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
		print 'waiting...'
		time.sleep(3)