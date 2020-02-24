from HttpMD5Util import buildMySign,httpGet,httpPost
import logging
import time
import hashlib
import json
from func import *
from constants import *

#initialize apikey，secretkey,url
eosNextWeek =getFuturePrice('eos','next_week')
eosQuarter =getFuturePrice('eos', 'quarter')

#season - next week > 0.2，short spread, season - next week <= 0.18，long spread
while True:
    time.sleep(10)
    amount = getAmount('eos')
    eosQuarterPosition = getFuturePosition('eos', 'quarter')
    eosQuarterPosition = eosQuarterPosition['holding']
    eosNextWeekPosition = getFuturePosition('eos', 'next_week')
    eosNextWeekPosition = eosNextWeekPosition['holding']
    res = {}
    logger2.info("eos quarter bid: " + str(eosQuarter['bids'][0][0]) + " next week ask: " + str(eosNextWeek['asks'][0][0]))
    if eosQuarter['bids'][0][0] - eosNextWeek['asks'][-1][0] > 0.25:
        print("trigger short")
        if len(eosQuarterPosition) != 0 and eosQuarterPosition[0]['sell_amount'] != 0:
            print("already short")
            continue
        clearPosition(logger1, 'eos')
        tradeSpread(logger1, 'eos', amount, False)
    if eosQuarter['asks'][-1][0] - eosNextWeek['bids'][0][0] < 0.2:
        print("trigger long")
        if len(eosQuarterPosition) != 0 and eosQuarterPosition[0]['buy_amount'] != 0:
            print("already long")
            continue
        clearPosition(logger1, 'eos')
        tradeSpread(logger1, 'eos', amount, True)
