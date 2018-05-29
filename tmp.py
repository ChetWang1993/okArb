
from OkcoinSpotAPI import OKCoinSpot
from OkcoinFutureAPI import OKCoinFuture
from HttpMD5Util import *

#初始化apikey，secretkey,url
apikey = '4b36c965-a577-497a-a216-665cedd68655'
secretkey = 'D0AB97E9CFE3F57131162952CE368191'
okcoinRESTURL = 'www.okex.com'   #请求注意：国内账号需要 修改为 www.okcoin.cn

#现货API
okcoinSpot = OKCoinSpot(okcoinRESTURL,apikey,secretkey)

#期货API
okcoinFuture = OKCoinFuture(okcoinRESTURL,apikey,secretkey)
okcoinFuture.future_trade(symbol='eos_usd',contractType='next_week',price=str(json_eos_next_week['asks'][0][0]), amount='1',tradeType='1',matchPrice='0',leverRate='')
params = {'api_key': '4b36c965-a577-497a-a216-665cedd68655', 'amount': '1', 'symbol': 'btc_usd'}
params['sign'] = buildMySign(params,secretkey)
okcoinFuture.futureFundTransfer('btc_usd','1', '1')
okcoinFuture.futureFundTransfer('eos_usd','1', '4.98997989')
param = 'symbol=eos_usdt&contract_type=quarter'
httpGet("www.okex.com", "/api/v1/future_hold_amount.do", param)

okcoinFuture.future_position_4fix('eos_usd','next_week','1')
def getAmount(amountJson):
    if amountJson['holding'] == []:
        return 0.
    else:
        return amountJson['holding']['buy_amount']
