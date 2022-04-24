from datetime import datetime
import math
import numpy
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import talib
import time
import os

import config
from bnb import Bnb
from data import Data

class Symbol:

    DISABLED     = 'DISABLED'
    SLEEP        = 'SLEEP'
    ENABLED      = 'ENABLED'
    UPTREND1H    = 'UPTREND1H'
    UPTREND5M    = 'UPTREND5M'
    UPTRENDENTRY = 'UPTRENDENTRY'
    UPTRENDTP1   = 'UPTRENDTP1'
    UPTRENDTP2   = 'UPTRENDTP2'
    DNTREND1H    = 'DNTREND1H'
    DNTREND5M    = 'DNTREND5M'
    DNTRENDENTRY = 'DNTRENDENTRY'
    DNTRENDTP1   = 'DNTRENDTP1'
    DNTRENDTP2   = 'DNTRENDTP2'

    ORDER_CANCELED         = Bnb.ORDER_CANCELED
    ORDER_EXPIRED          = Bnb.ORDER_EXPIRED
    ORDER_FILLED           = Bnb.ORDER_FILLED
    ORDER_NEW              = Bnb.ORDER_NEW
    ORDER_PARTIALLY_FILLED = Bnb.ORDER_PARTIALLY_FILLED
    ORDER_PENDING_CANCEL   = Bnb.ORDER_PENDING_CANCEL
    ORDER_REJECTED         = Bnb.ORDER_REJECTED

    COMMISSION = 0.001

    UPTREND1H_DURATION = 1
    UPTREND5M_DURATION = 1

    OCO_LIMIT_PERCENT = 0.8
    OCO_CANCEL_PERCENT = 0.9

    def log(self, ntabs, msg):
        tabs = ''
        for i in range(0, ntabs):
            tabs += '    '
        dt = datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d, %H:%M:%S')
        nmsg = ('%-6s %s, %-12s  =>  %s%s' % (self.base_asset, dt, self.status, tabs, msg))
        f = open(self.log_file, "a+")
        f.write(nmsg + '\n')
        f.close()
        print(nmsg)


    def __init__(self, bnb, symbol_info):

        self.bnb = bnb

        self.name = symbol_info['symbol']
        self.base_asset = symbol_info['baseAsset']
        self.base_asset_precision = int(symbol_info['baseAssetPrecision'])
        self.base_commission_precision = int(symbol_info['baseCommissionPrecision'])
        self.quote_asset = symbol_info['quoteAsset']
        self.quote_asset_precision = int(symbol_info['quotePrecision'])
        self.quote_commission_precision = int(symbol_info['quoteCommissionPrecision'])
        self.is_margin_allowed = bool(symbol_info['isMarginTradingAllowed'])

        for i in symbol_info['filters']:
            if i['filterType'] == 'PRICE_FILTER':
                self.minimum_price_movement = self.convertPrecision(float(i['tickSize']))
            if i['filterType'] == 'LOT_SIZE':
                self.maximum_trade_amount = float(i['maxQty'])
                self.minimum_trade_amount = self.convertPrecision(float(i['minQty']))
            if i['filterType'] == 'MIN_NOTIONAL':
                self.minimum_order_size = float(i['minNotional'])
            if i['filterType'] == 'PERCENT_PRICE':
                self.multiplier_up = float(i['multiplierUp'])
                self.multiplier_down = float(i['multiplierDown'])

        self.status = self.ENABLED

        self.log_file = 'log/' + str(self.base_asset) + '.log'

        self.next_sleep_wake = -1
        self.order_check = 0
        self.next_order_check = -1
        self.asset_check = 0
        self.next_asset_check = -1
        self.next_update_1h = -1
        self.next_update_5m = -1

        self.data1h = None
        self.ema1h_8 = None
        self.ema1h_21 = None

        self.data5m = None
        self.ema5m_8 = None
        self.ema5m_13 = None
        self.ema5m_21 = None

        self.entry = None
        self.sl = None
        self.risk = None
        self.tp1 = None
        self.tp2 = None
        self.percent = None
        self.open_time = None

        self.entry_limit_order_id = None
        self.entry_stop_order_id = None
        self.tp1_limit_order_id = None
        self.tp1_stop_order_id = None
        self.tp2_limit_order_id = None
        self.tp2_stop_order_id = None

        if not os.path.exists("log"):
            os.makedirs("log")

        f = open(self.log_file, "a+")
        f.write("########################################################################################\n")
        f.write("# NEW SESSION                                                                          #\n")
        f.write("########################################################################################\n")
        f.close()


    def __clearTradeInfo(self):
        self.entry = None
        self.sl = None
        self.risk = None
        self.tp1 = None
        self.tp2 = None
        self.percent = None
        self.open_time = None
        self.entry_limit_order_id = None
        self.entry_stop_order_id = None
        self.tp1_limit_order_id = None
        self.tp1_stop_order_id = None
        self.tp2_limit_order_id = None
        self.tp2_stop_order_id = None

    # Can be set from any status
    def setStatusDisable(self):
        self.status = self.DISABLED
        self.next_sleep_wake = -1
        self.order_check = 1
        self.next_order_check = time.time() + 5
        self.asset_check = 1
        self.next_asset_check = time.time() + 10
        self.next_update_1h = -1
        self.next_update_5m = -1
        self.data1h = None
        self.ema1h_8 = None
        self.ema1h_21 = None
        self.data5m = None
        self.ema5m_8 = None
        self.ema5m_13 = None
        self.ema5m_21 = None
        self.__clearTradeInfo()

    # Can be set from any status with no open orders
    def setStatusSleep(self):
        self.status = self.SLEEP
        self.next_sleep_wake = int((time.time() + 300) / 300) * 300
        self.order_check = 0
        self.next_order_check = -1
        self.asset_check = 0
        self.next_asset_check = -1
        self.next_update_1h = -1
        self.next_update_5m = -1
        self.data1h = None
        self.ema1h_8 = None
        self.ema1h_21 = None
        self.data5m = None
        self.ema5m_8 = None
        self.ema5m_13 = None
        self.ema5m_21 = None
        self.__clearTradeInfo()

    # Can be set from any status
    def setStatusEnabled(self):

        if (self.status == self.UPTRENDENTRY or
                self.status == self.UPTRENDTP1 or
                self.status == self.UPTRENDTP2):
            self.plot()

        self.status = self.ENABLED
        self.order_check = 1
        self.next_order_check = time.time() + 5
        self.asset_check = 1
        self.next_asset_check = time.time() + 10
        self.next_update_1h = -1
        self.next_update_5m = -1
        self.data1h = None
        self.ema1h_8 = None
        self.ema1h_21 = None
        self.data5m = None
        self.ema5m_8 = None
        self.ema5m_13 = None
        self.ema5m_21 = None
        self.__clearTradeInfo()

    # Must only set from ENABLED
    def setStatusUptrend1h(self):
        self.status = self.UPTREND1H

    # Must only set from UPTREND1H
    def setStatusUptrend5m(self):
        self.status = self.UPTREND5M

    # Must only set from UPTREND5M
    def setStatusUptrendEntry(self):
        self.status = self.UPTRENDENTRY

    # Must only set from UPTRENDENTRY
    def setStatusUptrendTP1(self):
        self.status = self.UPTRENDTP1

    # Must only set from UPTRENDTP1
    def setStatusUptrendTP2(self):
        self.status = self.UPTRENDTP2

    # Must only set from ENABLED
    def setStatusDntrend1h(self):
        self.status = self.DNTREND1H

    def convertPrecision(self, value):
        v = value

        if v >= 1:
            count = 0
            while True:
                v = v / 10
                if v < 1:
                    return count
                count -= 1
        if v <= 0.1:
            count = 1
            while True:
                v = v * 10
                if v > 0.1:
                    return count
                count += 1


    def roundDown(self, num, precision):
        factor = 10.0 ** precision
        return math.floor(num * factor) / factor


    def updateData1h(self):
        self.data1h = self.bnb.getSymbolData(self.name, Bnb.INTERVAL_1HOUR, "3 days ago", 40)
        self.ema1h_8 = talib.EMA(numpy.array(self.data1h.close), 8)
        self.ema1h_21 = talib.EMA(numpy.array(self.data1h.close), 21)
        self.next_update_1h = int((time.time() + 3600) / 3600) * 3600


    def updateData5m(self):
        self.data5m = self.bnb.getSymbolData(self.name, Bnb.INTERVAL_5MINUTE, "3 days ago", 480)
        self.ema5m_8 = talib.EMA(numpy.array(self.data5m.close), 8)
        self.ema5m_13 = talib.EMA(numpy.array(self.data5m.close), 13)
        self.ema5m_21 = talib.EMA(numpy.array(self.data5m.close), 21)
        self.next_update_5m = int((time.time() + 300) / 300) * 300


    def detectUptrend1h(self):

        curr = len(self.data1h.close) - 1
        conv = curr

        # Find the last convergence point where where either
        # 8 EMA is below 21 EMA, or
        # candlestick touched 8 EMA
        while conv >= 0:
            if math.isnan(self.ema1h_21[conv]):
                conv += 1
                break
            if self.ema1h_8[conv] <= self.ema1h_21[conv]:
                break
            if self.data1h.low[conv] <= self.ema1h_8[conv]:
                break
            conv -= 1

        # Convergence must not be at current point
        if conv == curr:
            return -1

        # Return uptrend duration
        return curr - conv


    def detectUptrend5m(self):

        curr = len(self.data5m.close) - 1
        conv = curr

        # Find the last convergence point where where either
        # 13 EMA is below 21 EMA, or
        # 8 EMA is below 21 EMA, or
        # 8 EMA is below 13 EMA, or
        # candlestick touched 8 EMA
        while conv >= 0:
            if math.isnan(self.ema5m_21[conv]):
                conv += 1
                break
            if self.ema5m_13[conv] <= self.ema5m_21[conv]:
                break
            if self.ema5m_8[conv] <= self.ema5m_21[conv]:
                break
            if self.ema5m_8[conv] <= self.ema5m_13[conv]:
                break
            if self.data5m.low[conv] <= self.ema5m_8[conv]:
                break
            conv -= 1

        # Convergence must not be at current point
        if conv == curr:
            return -1

        # Return uptrend duration
        return curr - conv


    def performOrderCheck(self):
        # Check for any open orders and cancel if any
        self.log(1, "Performing order check")
        order_ids = self.bnb.getOpenOrders(self.name)
        self.log(2, "There are %d open orders" % len(order_ids))
        for order_id in order_ids:
            self.bnb.cancelOrder(self.name, order_id)
            self.log(2, "Canceled order %d" % (order_id))


    def performAssetCheck(self):
        # Check for any remaining assets and market sell off if any
        self.log(1, "Performing asset check")

        while True:
            free, locked = self.bnb.getAssetBalance(self.base_asset)
            self.log(2, "Asset balance, free:%f locked:%f" % (free, locked))

            if (free > self.maximum_trade_amount):
                self.log(2, "Truncating to maximum trade amount.")
                qty = self.maximum_trade_amount
            else:
                qty = free

            qty = self.roundDown(qty, self.minimum_trade_amount)

            last_price = self.bnb.getSymbolLastPrice(self.name)
            if qty * last_price >= self.minimum_order_size:
                order_id = self.bnb.placeMarketOrder(Bnb.SIDE_SELL, self.name, qty)
                order_status = self.bnb.getOrderStatus(self.name, order_id)
                self.log(2, "Sold quantity: %f" % (float(order_status['executedQty'])))
            else:
                self.log(2, "Minimum order size not met")
                return 0


    def serviceStatusDisabled(self):

        if self.status != self.DISABLED:
            return -1

        curr_time = int(time.time())

        if self.order_check:
            if curr_time >= self.next_order_check:
                # Check for any open orders and cancel if any
                self.log(0, "Next order check reached")
                self.performOrderCheck()
                self.order_check = 0
                self.next_order_check = -1
                return 0
            else:
                # Do not perform any uptrend checks until order check is completed
                return -1

        if self.asset_check:
            if curr_time >= self.next_asset_check:
                # Check for any remaining assets and perform market sell off if any
                self.log(0, "Next asset check reached")
                self.performAssetCheck()
                self.asset_check = 0
                self.next_asset_check = -1
                return 0
            else:
                # Do not perform any uptrend checks until asset check is completed
                return -1


    def serviceStatusSleep(self):

        if self.status != self.SLEEP:
            return -1

        curr_time = int(time.time())

        if curr_time > self.next_sleep_wake:
            self.log(0, "Sleep wake time reached")
            self.log(1, "Setting status to %s" % (self.ENABLED))
            self.setStatusEnabled()
            return 0

        return -1


    def serviceStatusEnabled(self):

        if self.status != self.ENABLED:
            return -1

        curr_time = int(time.time())

        if self.order_check:
            if curr_time >= self.next_order_check:
                # Check for any open orders and cancel if any
                self.log(0, "Next order check reached")
                self.performOrderCheck()
                self.order_check = 0
                self.next_order_check = -1
                return 0
            else:
                # Do not perform any uptrend checks until order check is completed
                return -1

        if self.asset_check:
            if curr_time >= self.next_asset_check:
                # Check for any remaining assets and perform market sell off if any
                self.log(0, "Next asset check reached")
                self.performAssetCheck()
                self.asset_check = 0
                self.next_asset_check = -1
                return 0
            else:
                # Do not perform any uptrend checks until asset check is completed
                return -1

        if curr_time >= self.next_update_1h:
            # Update 1h data and check for 1h uptrend
            self.log(0, "Next update 1h reached")
            self.updateData1h()

            if self.detectUptrend1h() >= self.UPTREND1H_DURATION:
                self.log(1, "Detected uptrend on 1h.")
                self.log(1, "Setting status to %s" % (self.UPTREND1H))
                self.setStatusUptrend1h()
            else:
                self.log(1, "Uptrend 1h not detected")

            return 0

        return -1


    def serviceStatusUptrend1h(self):

        if self.status != self.UPTREND1H:
            return -1

        curr_time = int(time.time())

        if curr_time >= self.next_update_1h:
            # Update 1h data and check for 1h uptrend
            self.log(0, "Next update 1h reached")
            self.updateData1h()
            if self.detectUptrend1h() < self.UPTREND1H_DURATION:
                self.log(1, "Uptrend ended on 1h.")
                self.log(1, "Setting status to %s" % (self.ENABLED))
                self.setStatusEnabled()
                return 0
            else:
                self.log(1, "Uptrend 1h maintained")

        if curr_time >= self.next_update_5m:
            # Update 5m data and check for 5m uptrend
            self.log(0, "Next update 5m reached")
            self.updateData5m()
            if self.detectUptrend5m() >= self.UPTREND5M_DURATION:
                self.log(1, "Detected uptrend on 5m.")
                self.log(1, "Setting status to %s" % (self.UPTREND5M))
                self.setStatusUptrend5m()
            else:
                self.log(1, "Uptrend 5m not detected")
            return 0

        return -1


    def serviceStatusUptrend5m(self):

        if self.status != self.UPTREND5M:
            return -1

        curr_time = int(time.time())

        if curr_time >= self.next_update_1h:
            # Update 1h data and check for 1h uptrend
            self.log(0, "Next update 1h reached")
            self.updateData1h()
            if self.detectUptrend1h() < self.UPTREND1H_DURATION:
                self.log(1, "Uptrend ended on 1h.")
                self.log(1, "Setting status to %s" % (self.ENABLED))
                self.setStatusEnabled()
                return 0
            else:
                self.log(1, "Uptrend 1h maintained")

        if curr_time >= self.next_update_5m:
            # Update 5m data and check for 5m uptrend
            self.log(0, "Next update 5m reached")
            self.updateData5m()
            if self.detectUptrend5m() < self.UPTREND5M_DURATION:
                self.log(1, "Uptrend ended on 5m.")
                self.log(1, "Setting status to %s" % (self.ENABLED))
                self.setStatusEnabled()
                return 0
            else:
                self.log(1, "Uptrend 1h maintained")

        # Check for buy trigger
        data = self.bnb.getSymbolDataLatest(self.name, Bnb.INTERVAL_5MINUTE)

        if (data.low[-1] <= self.ema5m_8[-1]) or (self.data5m.low[-1] <= self.ema5m_8[-1]):

            # Find the highest point from the last 5 candles
            max = 0
            for i in range(len(self.data5m.high) - 5, len(self.data5m.high)):
                if max < self.data5m.high[i]:
                    max = self.data5m.high[i]

            # Current price must be below entry point (max)
            if data.close[-1] < max:
                self.log(0, "Buy trigger detected")

                pip3 = 0.003 * max;
                pip1 = 0.001 * max;

                self.entry = self.roundDown(max + pip3, self.minimum_price_movement)
                self.sl    = self.roundDown(data.low[-1] - pip3, self.minimum_price_movement)
                self.risk  = self.roundDown((self.entry - self.sl), self.minimum_price_movement)
                self.tp1   = self.roundDown((self.entry + (self.risk * 1)), self.minimum_price_movement)
                self.tp2   = self.roundDown((self.entry + (self.risk * 2)), self.minimum_price_movement)

                self.percent = (self.risk / self.entry * 100.0)

                if self.percent < config.RISK_PERCENT_MIN or self.percent > config.RISK_PERCENT_MAX:
                    self.log(1, "Risk percentage unsatisfied.")
                    self.log(1, "Setting status to %s" % (self.SLEEP))
                    self.setStatusSleep()
                    return 0

                free, locked = self.bnb.getAssetBalance(self.quote_asset)

                if free < config.TRADE_AMOUNT_USD:
                    self.log(1, "Insufficient USDT balance")
                    self.log(1, "Setting status to %s" % (self.SLEEP))
                    self.setStatusSleep()
                    return 0

                qty = float(config.TRADE_AMOUNT_USD / self.entry)
                qty = self.roundDown(qty, self.minimum_trade_amount)

                self.log(1, "Attempting to place Entry order")
                self.log(2, "entry    : %.9f" % (self.entry))
                self.log(2, "sl       : %.9f" % (self.sl))
                self.log(2, "risk     : %.9f" % (self.risk))
                self.log(2, "tp1      : %.9f" % (self.tp1))
                self.log(2, "tp2      : %.9f" % (self.tp2))
                self.log(2, "percent  : %.9f" % (self.percent))
                self.log(2, "quantity : %.9f" % (qty))

                # Absurd price that will never be triggered as order will be canceled
                # if price moves below stop loss
                limit = self.roundDown((self.sl * self.OCO_LIMIT_PERCENT), self.minimum_price_movement)

                if qty * limit < self.minimum_order_size:
                    self.log(1, "Minimum order size for Entry order unsatisfied")
                    self.log(1, "Setting status to %s" % (self.SLEEP))
                    self.setStatusSleep()
                    return 0

                if (qty / 2) * self.sl < self.minimum_order_size:
                    self.log(1, "Minimum order size for TP1 and TP2 orders unsatisfied")
                    self.log(1, "Setting status to %s" % (self.SLEEP))
                    self.setStatusSleep()
                    return 0

                self.entry_limit_order_id, self.entry_stop_order_id = self.bnb.placeOcoBuy(
                    symbol=self.name,
                    quantity=qty,
                    limit=limit,
                    stop=self.entry,
                    stop_limit=self.entry,
                    time_in_force=Bnb.TIF_FOK
                )
                if self.entry_limit_order_id < 0:
                    self.log(1, "Placing order returned error code %d" % (self.entry_limit_order_id))
                    self.log(1, "Setting status to %s" % (self.SLEEP))
                    self.setStatusSleep()
                    return 0

                self.log(1, "Place Entry order success")
                self.log(2, "entry_limit_order_id: %d" % (self.entry_limit_order_id))
                self.log(2, "entry_stop_order_id: %d" % (self.entry_stop_order_id))
                self.open_time = time.time()
                self.plot()
                self.log(1, "Setting status to %s" % (self.UPTRENDENTRY))
                self.setStatusUptrendEntry()
                return 0

        return -1


    def serviceStatusUptrendEntry(self):

        if self.status != self.UPTRENDENTRY:
            return -1

        order_status = self.bnb.getOrderStatus(self.name, self.entry_stop_order_id)

        # Check if entry stop order has been filled
        if order_status['status'] == Bnb.ORDER_FILLED:
            self.log(0, "Entry stop order filled")
            self.log(1, "Attempting to place TP1 order")
            free, locked = self.bnb.getAssetBalance(self.base_asset)
            qty1 = self.roundDown((free / 2), self.minimum_trade_amount)

            self.tp1_limit_order_id, self.tp1_stop_order_id = self.bnb.placeOcoSell(
                symbol=self.name,
                quantity=qty1,
                limit=self.tp1,
                stop=self.sl,
                stop_limit=self.sl,
                time_in_force=Bnb.TIF_GTC
            )

            if self.tp1_limit_order_id < 0:
                self.log(1, "Placing order returned error code: %d" % (self.tp1_limit_order_id))
                self.log(1, "Performing order and asset check")
                self.performOrderCheck()
                self.performAssetCheck()
                self.log(1, "Setting status to %s" % (self.ENABLED))
                self.setStatusEnabled()
                return 0

            self.log(1, "Place TP1 order  SUCCESS")
            self.log(2, "tp1_limit_order_id: %d" % self.tp1_limit_order_id)
            self.log(2, "tp1_stop_order_id: %d" % self.tp1_stop_order_id)

            self.log(1, "Attempting to place TP2 order")
            qty2 = self.roundDown((free - qty1), self.minimum_trade_amount)

            self.tp2_limit_order_id, self.tp2_stop_order_id = self.bnb.placeOcoSell(
                symbol=self.name,
                quantity=qty2,
                limit=self.tp2,
                stop=self.sl,
                stop_limit=self.sl,
                time_in_force=Bnb.TIF_GTC
            )

            if self.tp2_limit_order_id < 0:
                self.log(1, "Placing order returned error code: %d" % (self.tp2_limit_order_id))
                self.log(1, "Performing order and asset check")
                self.performOrderCheck()
                self.performAssetCheck()
                self.log(1, "Setting status to %s" % (self.ENABLED))
                self.setStatusEnabled()
                return 0

            self.log(1, "Place TP2 order SUCCESS")
            self.log(2, "tp2_limit_order_id: %d" % self.tp2_limit_order_id)
            self.log(2, "tp2_stop_order_id: %d" % self.tp2_stop_order_id)

            self.log(1, "Setting status to %s" % (self.UPTRENDTP1))
            self.setStatusUptrendTP1()
            return 0

        # Check if entry stop order has been canceled
        if order_status['status'] == Bnb.ORDER_CANCELED or order_status['status'] == Bnb.ORDER_EXPIRED:
            # Order is canceled either due to FOK or entry limit filled.
            self.log(0, "Entry order canceled")
            self.log(1, "Performing order and asset check")
            self.performOrderCheck()
            self.performAssetCheck()
            self.log(1, "Setting status to %s" % (self.ENABLED))
            self.setStatusEnabled()
            return 0

        # Check if last price crosses cancel limit
        last_price = self.bnb.getSymbolLastPrice(self.name)
        if last_price <= self.OCO_CANCEL_PERCENT * self.sl:
            self.log(0, "Last price dropped below ema21. Entry order will be cancelled")
            self.log(1, "Performing order and asset check")
            self.performOrderCheck()
            self.performAssetCheck()
            self.log(1, "Setting status to %s" % (self.ENABLED))
            self.setStatusEnabled()
            return 0

        curr_time = int(time.time())

        # Update 5m here and check if last candle closes below ema21
        if curr_time >= self.next_update_5m:
            self.log(0, "Next update 5m reached")
            self.updateData5m()
            if self.data5m.close[-1] <= self.ema5m_21[-1]:
                self.log(1, "5m low dropped below ema21. Entry order will be cancelled")
                self.log(1, "Performing order and asset check")
                self.performOrderCheck()
                self.performAssetCheck()
                self.log(1, "Setting status to %s" % (self.ENABLED))
                self.setStatusEnabled()
                return 0
            else:
                self.log(1, "Entry order is still valid")

        # Update 1h here
        if curr_time >= self.next_update_1h:
            self.log(0, "Next update 1h reached")
            self.updateData1h()

        return -1


    def serviceStatusUptrendTP1(self):

        if self.status != self.UPTRENDTP1:
            return -1

        # Check TP1 order

        order_status = self.bnb.getOrderStatus(self.name, self.tp1_limit_order_id)

        if order_status['status'] == Bnb.ORDER_FILLED:
            self.log(0, "TP1 order FILLED")
            self.log(1, "Setting status to %s" % (self.UPTRENDTP2))
            self.setStatusUptrendTP2()
            return 0

        elif order_status['status'] == Bnb.ORDER_PARTIALLY_FILLED:
            last_price = self.bnb.getSymbolLastPrice(self.name)
            if last_price <= self.sl + ((self.entry - self.sl) / 2):
                self.log(0, "TP1 order partially filled, but price dangerously close to SL")
                self.log(1, "Performing order and asset check")
                self.performOrderCheck()
                self.performAssetCheck()
                self.log(1, "Setting status to %s" % (self.ENABLED))
                self.setStatusEnabled()
                return 0

        elif order_status['status'] == Bnb.ORDER_CANCELED or order_status['status'] == Bnb.ORDER_EXPIRED:
            self.log(0, "Stop loss reached")
            self.log(1, "Performing order and asset check")
            self.performOrderCheck()
            self.performAssetCheck()
            self.log(1, "Setting status to %s" % (self.ENABLED))
            self.setStatusEnabled()
            return 0

        curr_time = int(time.time())

        if curr_time >= self.next_update_1h:
            # Update 1h
            self.log(0, "Next update 1h reached")
            self.updateData1h()
            self.log(1, "data1h updated")
            return 0

        if curr_time >= self.next_update_5m:
            # Update 5m data
            self.log(0, "Next update 5m reached")
            self.updateData5m()
            self.log(1, "data5m updated")
            return 0

        return -1


    def serviceStatusUptrendTP2(self):

        if self.status != self.UPTRENDTP2:
            return -1

        # Check TP2 order

        order_status = self.bnb.getOrderStatus(self.name, self.tp2_limit_order_id)

        if order_status['status'] == Bnb.ORDER_FILLED:
            self.log(0, "TP2 order filled")
            self.performOrderCheck()
            self.performAssetCheck()
            self.log(1, "Setting status to %s" % (self.ENABLED))
            self.setStatusEnabled()
            return 0

        elif order_status['status'] == Bnb.ORDER_PARTIALLY_FILLED:
            last_price = self.bnb.getSymbolLastPrice(self.name)
            if last_price <= self.entry:
                self.log(0, "TP2 order partially filled, but price dangerously close to Entry")
                self.log(1, "Performing order and asset check")
                self.performOrderCheck()
                self.performAssetCheck()
                self.log(1, "Setting status to %s" % (self.ENABLED))
                self.setStatusEnabled()
                return 0

        elif order_status['status'] == Bnb.ORDER_CANCELED or order_status['status'] == Bnb.ORDER_EXPIRED:
            self.log(0, "Stop loss reached.")
            self.log(1, "Performing order and asset check")
            self.performOrderCheck()
            self.performAssetCheck()
            self.log(1, "Setting status to %s" % (self.ENABLED))
            self.setStatusEnabled()
            return 0

        curr_time = int(time.time())

        if curr_time >= self.next_update_1h:
            # Update 1h
            self.log(0, "Next update 1h reached")
            self.updateData1h()
            self.log(1, "data1h updated")
            return 0

        if curr_time >= self.next_update_5m:
            # Update 5m data
            self.log(0, "Next update 5m reached")
            self.updateData5m()
            self.log(1, "data5m updated")
            return 0

        return -1


    def plot(self):

        # Create subplots

        fig = make_subplots(rows=2, cols=1, subplot_titles=('5m', '1h'))

        # 5m

        if self.data5m:
            ndata5m = self.data5m
        else:
            ndata5m = self.bnb.getSymbolData(self.name, Bnb.INTERVAL_5MINUTE, "3 days ago", 480)

        nlatest5m = self.bnb.getSymbolDataLatest(self.name, Bnb.INTERVAL_5MINUTE)

        if nlatest5m.open_time_unix[-1] != ndata5m.open_time_unix[-1]:
            ndata5m.append(
                nlatest5m.open_time_unix[-1],
                nlatest5m.open[-1],
                nlatest5m.high[-1],
                nlatest5m.low[-1],
                nlatest5m.close[-1],
                nlatest5m.close_time_unix[-1],
                nlatest5m.volume[-1]
            )

        ndata5m_df = ndata5m.asDataFrame()
        nema5m_8 = talib.EMA(numpy.array(ndata5m.close), 8)
        nema5m_13 = talib.EMA(numpy.array(ndata5m.close), 13)
        nema5m_21 = talib.EMA(numpy.array(ndata5m.close), 21)

        fig.add_trace(go.Candlestick(x=ndata5m_df['open_time'], open=ndata5m_df['open'],
            high=ndata5m_df['high'], low=ndata5m_df['low'], close=ndata5m_df['close']),
            row=1, col=1)

        fig.add_trace(go.Scatter(x=ndata5m_df['open_time'], y=pd.Series(nema5m_8),
            mode='lines', name='EMA(8)', line=dict(color="Red", width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=ndata5m_df['open_time'], y=pd.Series(nema5m_13),
            mode='lines', name='EMA(13)', line=dict(color="Green", width=1)), row=1, col=1)
        fig.add_trace(go.Scatter(x=ndata5m_df['open_time'], y=pd.Series(nema5m_21),
            mode='lines', name='EMA(21)', line=dict(color="Blue", width=1)), row=1, col=1)

        # 1h

        if self.data1h:
            ndata1h = self.data1h
        else:
            ndata1h = self.bnb.getSymbolData(self.name, Bnb.INTERVAL_1HOUR, "3 days ago", 40)

        nlatest1h = self.bnb.getSymbolDataLatest(self.name, Bnb.INTERVAL_1HOUR)

        ndata1h.append(
            nlatest1h.open_time_unix[-1],
            nlatest1h.open[-1],
            nlatest1h.high[-1],
            nlatest1h.low[-1],
            nlatest1h.close[-1],
            nlatest1h.close_time_unix[-1],
            nlatest1h.volume[-1]
        )

        ndata1h_df = ndata1h.asDataFrame()
        nema1h_8 = talib.EMA(numpy.array(ndata1h.close), 8)
        nema1h_21 = talib.EMA(numpy.array(ndata1h.close), 21)

        fig.add_trace(go.Candlestick(x=ndata1h_df['open_time'], open=ndata1h_df['open'],
            high=ndata1h_df['high'], low=ndata1h_df['low'], close=ndata1h_df['close']),
            row=2, col=1)

        fig.add_trace(go.Scatter(x=ndata1h_df['open_time'], y=pd.Series(nema1h_8),
            mode='lines', name='EMA(8)', line=dict(color="Red", width=1)), row=2, col=1)
        fig.add_trace(go.Scatter(x=ndata1h_df['open_time'], y=pd.Series(nema1h_21),
            mode='lines', name='EMA(21)', line=dict(color="Blue", width=1)), row=2, col=1)

        # Prices

        if self.entry:
            fig.add_hline(y=self.entry, row=1, col=1, annotation_text="entry", annotation_position="bottom right", line_color="grey")
        if self.tp1:
            fig.add_hline(y=self.tp1, row=1, col=1, annotation_text="TP1", annotation_position="bottom right", line_color="yellow")
        if self.tp2:
            fig.add_hline(y=self.tp2, row=1, col=1, annotation_text="TP2", annotation_position="bottom right", line_color="green")
        if self.sl:
            fig.add_hline(y=self.sl, row=1, col=1, annotation_text="SL", annotation_position="bottom right", line_color="red")
        if self.open_time:
            t = datetime.fromtimestamp(self.open_time).strftime('%Y-%m-%dT%H:%M:%SZ')
            fig.add_vrect(x0=t, x1=t, row=1, col=1, annotation_text='open', annotation_position="top left", line_color="black")

        # Layout

        title_str = ("%s - %s" % (self.name, self.status))

        fig.update_layout(title_text=title_str, xaxis1_rangeslider_visible=False, yaxis1_title='Price (USDT)',
                xaxis2_rangeslider_visible=False, yaxis2_title='Price (USDT)')

        fig.show()

