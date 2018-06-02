from HttpMD5Util import buildMySign,httpGet,httpPost
import logging
import time
import hashlib
import json
from func import *

#initialize apikey，secretkey,url
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

eosNextWeek =futurePrice('eos','next_week')
eosQuarter =futurePrice('eos', 'quarter')

#season - next week > 0.2，short spread, season - next week <= 0.18，long spread
while True:
    spotBid1 = spotPrice[sym]["bid"][0][0]
    spotAsk1 = spotPrice[sym]["ask"][-1][0]
    midPrice = (spotBid1 + spotAsk1) / 2
    futureInfo = getFutureUserInfo(sym)
    marginInUSD = midPrice * futureInfo(sym)
    totalShares = 3 * marginInUS / 10 if sym != 'btc' else marginInUS / 100
    amount = str(totalShares / 3)
    res = {}
    logger2.info("eos quarter bid: " + str(json_eos_quarter['bids'][0][0]) + " next week ask: " + str(json_eos_next_week['asks'][0][0]) + " eos next week amount: " + str(eosNextWeekAmount) + " eos quarter amount: " + str(eosQuarterAmount))
    nextWeekPosition = futurePosition(sym, 'next_week')
    quarterPosition = futurePosition(sym, 'quarter')
    if eosQuarter['bids'][0][0] - eosNextWeek[-1][0] > 0.22:
        if nextWeekPosition['holding']['sell_available']:
            clearPosition(logger1, 'eos')
        tradeSpread(logger1, 'eos', amount, True)
    if eosQuarter['asks'][-1][0] - eosNextWeek['bids'][0][0] < 0.18:
        if quarterPosition['holding']['buy_available']:
            clearPosition(logger1, 'eos')
        tradeSpread(logger1, 'eos', amount, False)
    time.sleep(5)
                      