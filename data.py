from collections import deque
import pandas as pd
from datetime import datetime

class Data:

    def __init__(self, max_len):
        self.open_time_unix = deque(maxlen=max_len)
        self.open_time = deque(maxlen=max_len)
        self.open = deque(maxlen=max_len)
        self.high = deque(maxlen=max_len)
        self.low = deque(maxlen=max_len)
        self.close = deque(maxlen=max_len)
        self.close_time_unix = deque(maxlen=max_len)
        self.close_time = deque(maxlen=max_len)
        self.volume = deque(maxlen=max_len)


    def append(self, open_time_unix, open, high, low, close, close_time_unix, volume):
        self.open_time_unix.append(open_time_unix)
        self.open_time.append(self.convertUnixTime(open_time_unix))
        self.open.append(open)
        self.high.append(high)
        self.low.append(low)
        self.close.append(close)
        self.close_time_unix.append(close_time_unix)
        self.close_time.append(self.convertUnixTime(close_time_unix))
        self.volume.append(volume)


    def convertUnixTime(self, time):
        return datetime.fromtimestamp(time).strftime('%Y-%m-%dT%H:%M:%SZ')


    def asDataFrame(self):
        dict = {}
        dict['open_time_unix'] = list(self.open_time_unix)
        dict['open_time'] = list(self.open_time)
        dict['open'] = list(self.open)
        dict['high'] = list(self.high)
        dict['low'] = list(self.low)
        dict['close'] = list(self.close)
        dict['close_time_unix'] = list(self.close_time_unix)
        dict['close_time'] = list(self.close_time)
        dict['volume'] = list(self.volume)
        return pd.DataFrame(dict)

