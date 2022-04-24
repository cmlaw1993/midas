
from binance.client import Client
from binance.exceptions import BinanceAPIException
from collections import deque
from datetime import datetime
import numpy
from operator import itemgetter
import pandas as pd
import talib
import time

import config
from data import Data



class Bnb:

    INTERVAL_1MINUTE = Client.KLINE_INTERVAL_1MINUTE
    INTERVAL_3MINUTE = Client.KLINE_INTERVAL_3MINUTE
    INTERVAL_5MINUTE = Client.KLINE_INTERVAL_5MINUTE
    INTERVAL_15MINUTE = Client.KLINE_INTERVAL_15MINUTE
    INTERVAL_30MINUTE = Client.KLINE_INTERVAL_30MINUTE
    INTERVAL_1HOUR = Client.KLINE_INTERVAL_1HOUR
    INTERVAL_2HOUR = Client.KLINE_INTERVAL_2HOUR
    INTERVAL_4HOUR = Client.KLINE_INTERVAL_4HOUR
    INTERVAL_6HOUR = Client.KLINE_INTERVAL_6HOUR
    INTERVAL_8HOUR = Client.KLINE_INTERVAL_8HOUR
    INTERVAL_12HOUR = Client.KLINE_INTERVAL_12HOUR
    INTERVAL_1DAY = Client.KLINE_INTERVAL_1DAY
    INTERVAL_3DAY = Client.KLINE_INTERVAL_3DAY
    INTERVAL_1WEEK = Client.KLINE_INTERVAL_1WEEK
    INTERVAL_1MONTH = Client.KLINE_INTERVAL_1MONTH

    SIDE_SELL = Client.SIDE_SELL
    SIDE_BUY  = Client.SIDE_BUY

    ORDER_CANCELED         = Client.ORDER_STATUS_CANCELED
    ORDER_EXPIRED          = Client.ORDER_STATUS_EXPIRED
    ORDER_FILLED           = Client.ORDER_STATUS_FILLED
    ORDER_NEW              = Client.ORDER_STATUS_NEW
    ORDER_PARTIALLY_FILLED = Client.ORDER_STATUS_PARTIALLY_FILLED
    ORDER_PENDING_CANCEL   = Client.ORDER_STATUS_PENDING_CANCEL
    ORDER_REJECTED         = Client.ORDER_STATUS_REJECTED

    TIF_FOK = Client.TIME_IN_FORCE_FOK
    TIF_GTC = Client.TIME_IN_FORCE_GTC
    TIF_IOC = Client.TIME_IN_FORCE_IOC

    RETRY = 20


    def __log(self, func, code, message):
        dt = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d, %H:%M:%S')
        print("###############################################################")
        print("SERVER, %s, %s:%d:%s" % (dt, func, code, message))
        print("###############################################################")


    def __logMisc(self, func, e):
        dt = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d, %H:%M:%S')
        print("***************************************************************")
        print("SERVER, %s, %s: " % (dt, func), e)
        print("***************************************************************")


    def __startClient(self):
        while True:
            try:
                self.client = Client(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY)
                return
            except BinanceAPIException as e:
                self.__log('startClient', e.code, e.message)
                time.sleep(1)
            except Exception as e:
                self.__logMisc('startClient', e)
                time.sleep(1)


    def __init__(self):
        self.__startClient()



    def getSymbols(self):
        retry = self.RETRY
        while True:
            try:
                info = self.client.get_exchange_info()

                if len(info) > 0:

                    ret = []
                    symbols = info['symbols']
                    for s in symbols:
                        if s['quoteAsset'] != 'USDT':
                            continue
                        if s['status'] != 'TRADING':
                            continue
                        if s['ocoAllowed'] != True:
                            continue
                        if s['isSpotTradingAllowed'] != True:
                            continue
                        if 'LIMIT' not in s['orderTypes']:
                            continue
                        if 'MARKET' not in s['orderTypes']:
                            continue
                        if 'STOP_LOSS_LIMIT' not in s['orderTypes']:
                            continue
                        if 'SPOT' not in s['permissions']:
                            continue
                        if 'MARGIN' not in s['permissions']:
                            continue
                        ret.append(s)

                    return sorted(ret, key=itemgetter('symbol'))
                else:
                    if retry > 0:
                        retry -= 1
                    else:
                        self.__log('getSymbols', 0, "-No results returned-")
                        return []

            except BinanceAPIException as e:
                self.__log('getSymbols', e.code, e.message)
                self.__startClient()
            except Exception as e:
                self.__logMisc('getSymbols', e)
                self.__startClient()


    def getSymbolData(self, symbol, interval, time_ago, max_len):
        retry = self.RETRY
        while True:
            try:
                klines = self.client.get_historical_klines(symbol, interval, time_ago)
                output_data = Data(max_len=max_len)
                if len(klines) > 0:
                    curr_time = time.time()
                    for kline in klines:
                        # Only accept closed candles.
                        if int(kline[6] / 1000) > curr_time:
                            continue
                        output_data.append(
                            float(kline[0] / 1000), # Open time - Convert ms to s
                            float(kline[1]),        # Open
                            float(kline[2]),        # High
                            float(kline[3]),        # Low
                            float(kline[4]),    # Close
                            float(kline[6] / 1000), # Close time - Convert ms to s
                            float(kline[7])         # Volume
                        )
                    return output_data
                else:
                    if retry > 0:
                        retry -= 1
                    else:
                        self.__log('getSymbolData', 0, "-No results returned-")
                        return None

            except BinanceAPIException as e:
                self.__log('getSymbolData', e.code, e.message)
                self.__startClient()
            except Exception as e:
                self.__logMisc('getSymbolData', e)
                self.__startClient()


    def getSymbolDataLatest(self, symbol, interval):
        retry = self.RETRY
        while True:
            try:
                klines = self.client.get_klines(symbol=symbol, interval=interval, limit=5)
                output_data = Data(max_len=1)
                if len(klines) > 0:
                    output_data.append(
                        float(klines[-1][0] / 1000), # Open time - Convert ms to s
                        float(klines[-1][1]),        # Open
                        float(klines[-1][2]),        # High
                        float(klines[-1][3]),        # Low
                        float(klines[-1][4]),        # Close
                        float(klines[-1][6] / 1000), # Close time Convert ms to s
                        float(klines[-1][7])         # Volume
                    )
                    return output_data
                else:
                    if retry > 0:
                        retry -= 1
                    else:
                        self.__log('getSymbolDataLatest', 0, "-No results returned-")
                        return None

            except BinanceAPIException as e:
                self.__log('getSymbolDataLatest', e.code, e.message)
                self.__startClient()
            except Exception as e:
                self.__logMisc('getSymbolDataLatest', e)
                self.__startClient()


    def getSymbolLastPrice(self, symbol):
        retry = self.RETRY
        while True:
            try:
                tickers = self.client.get_all_tickers()
                for t in tickers:
                    if t['symbol'] == symbol:
                        return float(t['price'])

                if retry > 0:
                    retry -= 1
                else:
                    return -1.0

            except BinanceAPIException as e:
                self.__log('getSymbolLastPrice', e.code, e.message)
                self.__startClient()
            except Exception as e:
                self.__logMisc('getSymbolLastPrice', e)
                self.__startClient()


    def getAssetBalance(self, asset):
        retry = self.RETRY
        while True:
            try:
                balance = self.client.get_asset_balance(asset)
                if float(balance['free']) == 0.0 and float(balance['locked']) == 0.0:
                    if retry > 0:
                        retry -= 1
                    else:
                        return float(balance['free']), float(balance['locked'])
                else:
                    return float(balance['free']), float(balance['locked'])
            except BinanceAPIException as e:
                self.__log('getAssetBalance', e.code, e.message)
                self.__startClient()
            except Exception as e:
                self.__logMisc('getAssetBalance', e)
                self.__startClient()


    def getOpenOrders(self, symbol):
        retry = self.RETRY
        while True:
            try:
                ret = []
                orders = self.client.get_open_orders(symbol=symbol)
                if len(orders) > 0:
                    for o in orders:
                        ret.append(o['orderId'])
                    return ret
                elif retry > 0:
                    retry -= 1
                else:
                    return ret
            except BinanceAPIException as e:
                self.__log('getOpenOrders', e.code, e.message)
                self.__startClient()
            except Exception as e:
                self.__logMisc('getOpenOrders', e)
                self.__startClient()


    def getOrderStatus(self, symbol, order_id):
        retry = self.RETRY
        while True:
            try:
                order = self.client.get_order(
                    symbol=symbol,
                    orderId=order_id
                )
                return order
            except BinanceAPIException as e:
                # Unknown order id
                if e.code == -2011:
                    if retry > 0:
                        retry -= 1
                    else:
                        self.__log('getOrderStatus', e.code, e.message)
                        return e.code
                else:
                    self.__log('getOrderStatus', e.code, e.message)
                    self.__startClient()
            except Exception as e:
                self.__logMisc('getOrderStatus', e)
                self.__startClient()


    def placeMarketOrder(self, side, symbol, quantity):
        retry = self.RETRY
        while True:
            try:
                order = self.client.create_order(
                    symbol=symbol,
                    side=side,
                    type=Client.ORDER_TYPE_MARKET,
                    quantity=quantity,
                    newOrderRespType=Client.ORDER_RESP_TYPE_RESULT
                )
                return int(order['orderId'])
            except BinanceAPIException as e:
                # 2010 - order rejected
                # 1013 - minimum volume not met
                # 1111 - precision over specified
                # 1100 - illegal characters in parameter 'quantity'
                if e.code == -2010 or e.code == -1013 or e.code == -1111 or e.code == -1100:
                    if retry > 0:
                        retry -= 1
                    else:
                        self.__log('placeMarketOrder', e.code, e.message)
                        return e.code
                else:
                    self.__log('placeMarketOrder', e.code, e.message)
                    self.__startClient()
            except Exception as e:
                self.__logMisc('placeMarketOrder', e)
                self.__startClient()


    def placeOcoBuy(self, symbol, quantity, limit, stop, stop_limit, time_in_force):
        retry = self.RETRY
        while True:
            try:
                order = self.client.order_oco_buy(
                    symbol=symbol,
                    quantity=quantity,
                    price=limit,
                    stopPrice=stop,
                    stopLimitPrice=stop_limit,
                    stopLimitTimeInForce=time_in_force
                )

                if order['orderReports'][0]['type'] == Client.ORDER_TYPE_STOP_LOSS_LIMIT:
                    stop_order_id = order['orderReports'][0]['orderId']
                    limit_order_id = order['orderReports'][1]['orderId']
                else:
                    stop_order_id = order['orderReports'][1]['orderId']
                    limit_order_id = order['orderReports'][0]['orderId']

                return limit_order_id, stop_order_id

            except BinanceAPIException as e:
                # 2010 - order rejected
                # 1013 - minimum volume not met
                # 1111 - precision over specified
                # 1100 - illegal characters in parameter 'quantity'
                if e.code == -2010 or e.code == -1013 or e.code == -1111 or e.code == -1100:
                    if retry > 0:
                        retry -= 1
                    else:
                        self.__log('placeOcoBuy', e.code, e.message)
                        return e.code, e.code
                else:
                    self.__log('placeOcoBuy', e.code, e.message)
                    self.__startClient()
            except Exception as e:
                self.__logMisc('placeOcoBuy', e)
                self.__startClient()


    def placeOcoSell(self, symbol, quantity, limit, stop, stop_limit, time_in_force):
        retry = self.RETRY
        while True:
            try:
                order = self.client.order_oco_sell(
                    symbol=symbol,
                    quantity=quantity,
                    price=limit,
                    stopPrice=stop,
                    stopLimitPrice=stop_limit,
                    stopLimitTimeInForce=time_in_force
                )

                if order['orderReports'][0]['type'] == Client.ORDER_TYPE_STOP_LOSS_LIMIT:
                    stop_order_id = order['orderReports'][0]['orderId']
                    limit_order_id = order['orderReports'][1]['orderId']
                else:
                    stop_order_id = order['orderReports'][1]['orderId']
                    limit_order_id = order['orderReports'][0]['orderId']

                return limit_order_id, stop_order_id

            except BinanceAPIException as e:
                # 2010 - order rejected
                # 1013 - minimum volume not met
                # 1111 - precision over specified
                # 1100 - illegal characters in parameter 'quantity'
                if e.code == -2010 or e.code == -1013 or e.code == -1111 or e.code == -1100:
                    if retry > 0:
                        retry -= 1
                    else:
                        self.__log('placeOcoSell', e.code, e.message)
                        return e.code, e.code
                else:
                    self.__log('placeOcoSell', e.code, e.message)
                    self.__startClient()
            except Exception as e:
                self.__logMisc('placeOcoSell', e)
                self.__startClient()


    def placeStopLimitSell(self, symbol, quantitiy, stop, limit):
        while True:
            try:
                order = self.client.create_order(
                    symbol=symbol,
                    side=Client.SIDE_SELL,
                    type=Client.ORDER_TYPE_STOP_LOSS_LIMIT,
                    timeInForce=Client.TIME_IN_FORCE_GTC,
                    quantity=quantity,
                    stopPrice = stop,
                    price=limit
                )
                return 0
            except BinanceAPIException as e:
                print('Bnb.placeStopLimitSell:%d:%s' % (e.code, e.message))
                # order rejected (eg. due to insufficient balance)
                if e.code == -2010:
                    return -1, -1
                # ??? (eg. due to minimum volume not met)
                if e.code == -1013:
                    return -1, -1
                # restart connection
                self.__startClient()


    def cancelOrder(self, symbol, order_id):
        retry = self.RETRY
        while True:
            try:
                self.client.cancel_order(
                    symbol=symbol,
                    orderId=order_id
                )
                return
            except BinanceAPIException as e:
                # Unknown order id
                if e.code == -2011:
                    if retry > 0:
                        retry -= 1
                    else:
                        self.__log('cancelOrder', e.code, e.message)
                        return e.code
                else:
                    self.__log('cancelOrder', e.code, e.message)
                    self.__startClient()
            except Exception as e:
                self.__logMisc('cancelOrder', e)
                self.__startClient()

