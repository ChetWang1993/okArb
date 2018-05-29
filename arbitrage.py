from OkcoinSpotAPI import OKCoinSpot
from OkcoinFutureAPI import OKCoinFuture
from HttpMD5Util import buildMySign,httpGet,httpPost
import logging
import time
import hashlib
import json

#初始化apikey，secretkey,url
apiKey = '4b36c965-a577-497a-a216-665cedd68655'
secretKey = 'D0AB97E9CFE3F57131162952CE368191'
okcoinRESTURL = 'www.okex.com'

logger1 = logging.getLogger('trading')
hdlr1 = logging.FileHandler('trading.log')
formatter1 = logging.Formatter('%(asctime)s %(levelname)s %(message)s execution price: %(executionPrice)s amount: %(amount)s trade type: %(tradeType)s contract type: %(contract)s')
hdlr1.setFormatter(formatter1)
logger1.addHandler(hdlr1)
logger2 = logging.getLogger("price")
hdlr2 = logging.FileHandler('price.log')
formatter2 = logging.Formatter('%(asctime)s %(levelname) s%(message)s')
hdlr2.setFormatter(formatter2)
logger2.addHandler(hdlr2)
logger2.setLevel(logging.INFO)
def getAmount(amountJson):
    if amountJson['holding'] == []:
        return 0.
    else:
        return amountJson['holding']['buy_amount']

def do_transaction(logger, symbol, contract_type, price, amount, trade_type, match_price):
    api_url = "https://www.okex.com/api/v1/future_trade.do"
    post_data={
        "api_key": apiKey,
        "symbol" : symbol,
        "contract_type" : contract_type,    #value: this_week, next_week, quarter:
        "price" : price,
        "amount" : amount,
        "type": trade_type,
        "match_price" : match_price
    }
    post_data['sign'] = buildMySign(post_data, secretKey)
    # buildMySign是生成签名的函数，交易所通常会要求提供
    res=json.loads(httpPost("www.okex.com","/api/v1/future_trade.do", post_data))
    if res['result'] == True:
        logger.info("Successfully place order " + res['order_id'], extra={'executionPrice': price, 'amount': amount, 'tradeType': trade_type, 'contract': contract_type, 'symbol': symbol})
    else:
        logger.error("Fail to place order " + str(res['error_code']), extra={'executionPrice': price, 'amount': amount, 'tradeType': trade_type, 'contract': contract_type, 'symbol': symbol})
    return res

okcoinFuture = OKCoinFuture(okcoinRESTURL,apiKey,secretKey)
# 使用 urllib2获取 EOS次周合约市场深度
url_of_eos_next_week = "https://www.okex.com/api/v1/future_depth.do?symbol=eos_usdt&contract_type=next_week&size=1" #EOS次周合约市场深度API地址
param = 'symbol=eos_usdt&contract_type=next_week&size=1'
json_eos_next_week =httpGet("www.okex.com", "/api/v1/future_depth.do", param)

eosNextWeekAmountJson = okcoinFuture.future_position_4fix('eos_usd','next_week','1')
eosNextWeekAmount = getAmount(json.loads(eosNextWeekAmountJson))

# 使用 urllib2获取 EOS季度合约市场深度
url_of_eos_quarter = "https://www.okex.com/api/v1/future_depth.do?symbol=eos_usdt&contract_type=quarter&size=1" #EOS季度合约市场深度API地址
param = 'symbol=eos_usdt&contract_type=quarter&size=1'
json_eos_quarter =httpGet("www.okex.com", "/api/v1/future_depth.do", param)
eosQuarterAmountJson = okcoinFuture.future_position_4fix('eos_usd','quarter','1')
eosQuarterAmount = getAmount(json.loads(eosQuarterAmountJson))

while True:
#当季度合约卖出（做空）价格，减去次周合约买入（做多）价格，得到的价差大于 1美元时，即做空季度，做多次周。
    res = {}
    logger2.info("eos quarter bid: " + str(json_eos_quarter['bids'][0][0]) + " next week ask: " + str(json_eos_next_week['asks'][0][0]) + " eos next week amount: " + str(eosNextWeekAmount) + " eos quarter amount: " + str(eosQuarterAmount))
    if json_eos_quarter['bids'][0][0] - json_eos_next_week['asks'][0][0] > 0.25 and eosNextWeekAmount <= 10. and eosQuarterAmount >= -10.:
    #做多eos次周
        do_transaction(logger = logger1, symbol= 'eos_usd', contract_type="next_week", price=str(json_eos_next_week['asks'][0][0]), amount='1', trade_type='1', match_price='0')
    #做空eos季度/
        do_transaction(logger = logger1, symbol= 'eos_usd', contract_type="quarter", price=str(json_eos_quarter['bids'][0][0]), amount='1', trade_type='2', match_price='0')

#当季度合约买入（平空）价格，减去次周合约卖出（平多）价格，得到的价差小于0.5美元时，即双向平仓。
    if json_eos_quarter['asks'][0][0] - json_eos_next_week['bids'][0][0] < 0.15:

    #eos次周平多
        do_transaction(logger = logger1, symbol = 'eos_usd', contract_type="next_week", price=str( json_eos_next_week['bids'][0][0]), amount='1', trade_type='3', match_price='0')

    #eos季度平空
        do_transaction(logger = logger1, symbol = 'eos_usd', contract_type="quarter", price=str(json_eos_quarter['asks'][0][0]), amount='1', trade_type='4', match_price='0')
    time.sleep(5)
                      
