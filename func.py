from HttpMD5Util import buildMySign,httpGet,httpPost
import logging
import time
import hashlib
import json
import constants

def getAmount(amountJson):
    if amountJson['holding'] == []:
        return 0.
    else:
        return amountJson['holding']['buy_amount']

def getFutureUserInfo(sym):
    post_data={"api_key": apiKey }
    post_data['sign'] = buildMySign(post_data, secretKey)
    res = json.loads(httpPost("www.okex.com","/api/v1/future_trade.do", post_data))
    return res[sym]

def spotPrice(sym):
    return json.loads(httpGet("www.okex.com", "/api/v1/depth.do", 'symbol='+ sym + '_usdt'))

def futurePrice(sym, contractType):
    return json.loads(httpGet("www.okex.com", "/api/v1/future_depth.do", 'symbol='+ sym + '_usdt&contract_type=' + contractType + '&size=1'))

def futurePosition(sym, contractType):
    post_data={'symbol': sym, 'contract_type': contractType, 'api_key': apiKey}
    post_data['sign'] = buildMySign(post_data, secretKey)
    res = json.loads(httpPost("www.okex.com","/api/v1/future_position_4fix", post_data))
    return res

def getFutureOrderInfo(sym, contractType, orderId):
    post_data={'symbol': sym, 'contract_type': contractType, 'api_key': apiKey, 'order_id': orderId}
    post_data['sign'] = buildMySign(post_data, secretKey)
    res = json.loads(httpPost("www.okex.com","/api/v1/future_order_info", post_data))
    return res['orders']

def futureCancel(sym, contractType, orderId):
    post_data={'symbol': sym, 'contract_type': contractType, 'api_key': apiKey, 'order_id': orderId}
    post_data['sign'] = buildMySign(post_data, secretKey)
    return json.loads(httpPost("www.okex.com","/api/v1/future_cancel", post_data))
    

def tradeSpread(logger, sym, amount, isLong):
    if isLong:
        res1 = futureTrade(logger, sym, "next_week", amount, '1', '1')
        res2 = futureTrade(logger, sym, "quarter", amount, '2', '1')
    else:
        res1 = futureTrade(logger, sym, "next_week", amount, '2','1')
        res2 = futureTrade(logger, sym, "quarter", amount, '1', '1')
    return True

def clearPosition(logger, sym):
    res1 = futurePosition(sym, 'next_week')
    res2 = futurePosition(sym, 'quarter')
    if res1['holding']['buy_available'] > 0:
        futureTrade(logger, sym, 'next_week', res1['holding']['buy_available'], '3', '1')
    if res1['holding']['sell_available'] > 0:
        futureTrade(logger, sym, 'next_week', res1['holding']['sell_available'], '4', '1')
    if res2['holding']['buy_available'] > 0:
        futureTrade(logger, sym, 'quarter', res2['holding']['buy_available'], '3', '1')
    if res2['holding']['sell_available'] > 0:
        futureTrade(logger, sym, 'quarter', res2['holding']['sell_available'], '4', '1')
    

def futureTrade(logger, sym, contractType, amount, trade_type, match_price):
    #buildMySign是生成签名的函数，交易所通常会要求提供
    iterations = 0
    remainingAmount = amount
    while remainingAmount != 0:
        futurePrice =httpGet("www.okex.com", "/api/v1/future_depth.do", 'sym=' + sym + '_usdt&contract_type='+ contractType + '&size=1')
        price = 0
        if trade_type == 1 or trade_type == 3:
            price = futurePrice['asks'][-1][0]
        if trade_type == 2 or trade_type == 4:
            price = futurePrice['bids'][0][0]
        post_data={"api_key": apiKey, "sym" : sym, "contract_type" : contract_type, "price" : price, "amount" : amount, "type": trade_type, "match_price" : match_price }
        post_data['sign'] = buildMySign(post_data, secretKey)
        res=json.loads(httpPost("www.okex.com","/api/v1/future_trade.do", post_data))
        if res['result'] == 'error':
            logger.error("Fail to place order " + str(res['error_code']), extra={'executionPrice': price, 'amount': amount, 'tradeType': trade_type, 'contract': contract_type, 'sym': sym})    
            continue
        time.sleep(10)
        order = getFutureOrderInfo(sym, contractType, res['order_id'])
        remainingAmount = remainingAmount - order['deal_amount']
        futureCancel(sym, contractType, res['order_id'])
    logger.info("Successfully place order " + res['order_id'], extra={'executionPrice': price, 'amount': amount, 'tradeType': trade_type, 'contract': contract_type, 'sym': sym})
    return res

