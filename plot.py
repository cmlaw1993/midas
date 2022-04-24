from binance.client import Client
from collections import deque

import pandas as pd
import datetime
import talib
import numpy

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

    def __init__(self):
        self.client = Client(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY)

    def getSymbols(self, quote):
        all_symbols = self.client.get_all_tickers()
        symbols = []
        for s in all_symbols:
            if (s['symbol'].endswith(quote)):
                symbols.append(s['symbol'])
        symbols.sort()
        return symbols

    def getSymbolData(self, symbol, interval, time_ago, output_data):

        klines = self.client.get_historical_klines(symbol, interval, time_ago)

        for kline in klines:
            output_data.append(
                float(kline[0] / 1000), # Convert ms to s
                float(kline[1]),
                float(kline[2]),
                float(kline[3]),
                float(kline[4]),
                float(kline[6] / 1000), # Convert ms to s
                float(kline[7])
            )

        return output_data


import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import time

if (__name__ == '__main__'):
    bnb = Bnb()
#    symbols = bnb.getSymbols('USDT')
#    for s in symbols:
#        print(s)

    data1h = Data(max_len=25)
    data1h = bnb.getSymbolData('BTCUSDT', Bnb.INTERVAL_1HOUR, "3 days ago", data1h)
    data1h_df = data1h.asDataFrame()

    data5m = Data(max_len=300)
    data5m = bnb.getSymbolData('BTCUSDT', Bnb.INTERVAL_5MINUTE, "3 days ago", data5m)
    data5m_df = data5m.asDataFrame()

    rsi = talib.EMA(numpy.array(data1h.close), 5)


    fig = make_subplots(rows=2, cols=1, subplot_titles=('5m', '1h'))

    fig.add_trace(
        go.Candlestick(
            x=data5m_df['open_time'],
            open=data5m_df['open'],
            high=data5m_df['high'],
            low=data5m_df['low'],
            close=data5m_df['close'],
            increasing_line_color='green',
            decreasing_line_color='red',
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Candlestick(
            x=data1h_df['open_time'],
            open=data1h_df['open'],
            high=data1h_df['high'],
            low=data1h_df['low'],
            close=data1h_df['close'],
            increasing_line_color='green',
            decreasing_line_color='red',
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Scatter(
            x=data1h_df['open_time'],
            y=pd.Series(rsi),
            mode='lines',
            name='RSI',
            line=dict(color="Red", width=1)
        ),
        row=2, col=1
    )

    fig.update_layout(
        title_text="BTCUSDT",
        xaxis1_rangeslider_visible=False,
        yaxis1_title='Price (USDT)',
        xaxis2_rangeslider_visible=False,
        yaxis2_title='Price (USDT)',
    )

    fig.add_vrect(x0='2021-02-20', x1='2021-02-20', row=2, col=1, annotation_text="decline", annotation_position="top left",)
    fig.add_hline(y=57000, row=2, col=1, annotation_text="decline", annotation_position="bottom right",)

    fig.show()

