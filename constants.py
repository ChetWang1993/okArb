import logging

#initialize apikey，secretkey,url
apiKey = '4b36c965-a577-497a-a216-665cedd68655'
secretKey = 'D0AB97E9CFE3F57131162952CE368191'

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

