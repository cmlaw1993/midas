from datetime import datetime
import PySimpleGUI as sg
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import pprint
import time

from bnb import Bnb
import config
from data import Data
from symbol import Symbol
from ui import UI

bnb = None
ui = None

symbols_all = []

symbols_disabled = []
symbols_sleep = []
symbols_enabled = []
symbols_uptrend1h = []
symbols_uptrend5m = []
symbols_uptrendentry = []
symbols_uptrendtp1 = []
symbols_uptrendtp2 = []
symbols_dntrend1h = []
symbols_dntrend5m = []
symbols_dntrendentry = []
symbols_dntrendtp1 = []
symbols_dntrendtp2 = []

symbols_disabled_name = []
symbols_sleep_name = []
symbols_enabled_name = []
symbols_uptrend1h_name = []
symbols_uptrend5m_name = []
symbols_uptrendentry_name = []
symbols_uptrendtp1_name = []
symbols_uptrendtp2_name = []
symbols_dntrend1h_name = []
symbols_dntrend5m_name = []
symbols_dntrendentry_name = []
symbols_dntrendtp1_name = []
symbols_dntrendtp2_name = []

symbols_banner = []

num_uptrend5m = 0

def segregateSymbols():

    global symbols_all

    global symbols_disabled
    global symbols_sleep
    global symbols_enabled
    global symbols_uptrend1h
    global symbols_uptrend5m
    global symbols_uptrendentry
    global symbols_uptrendtp1
    global symbols_uptrendtp2

    global symbols_disabled_name
    global symbols_sleep_name
    global symbols_enabled_name
    global symbols_uptrend1h_name
    global symbols_uptrend5m_name
    global symbols_uptrendentry_name
    global symbols_uptrendtp1_name
    global symbols_uptrendtp2_name

    global symbols_banner

    symbols_disabled = []
    symbols_sleep = []
    symbols_enabled = []
    symbols_uptrend1h = []
    symbols_uptrend5m = []
    symbols_uptrendentry = []
    symbols_uptrendtp1 = []
    symbols_uptrendtp2 = []

    symbols_disabled_name = []
    symbols_sleep_name = []
    symbols_enabled_name = []
    symbols_uptrend1h_name = []
    symbols_uptrend5m_name = []
    symbols_uptrendentry_name = []
    symbols_uptrendtp1_name = []
    symbols_uptrendtp2_name = []

    symbols_banner = []

    count = 0

    for s in symbols_all:
        if s.status == Symbol.ENABLED:
            symbols_enabled_name.append(s.base_asset)
            symbols_enabled.append(count)
            status = ""
        elif s.status == Symbol.UPTREND1H:
            symbols_uptrend1h_name.append(s.base_asset)
            symbols_uptrend1h.append(count)
            status = "UP-1H"
        elif s.status == Symbol.UPTREND5M:
            symbols_uptrend5m_name.append(s.base_asset)
            symbols_uptrend5m.append(count)
            status = "UP-5M"
        elif s.status == Symbol.UPTRENDENTRY:
            symbols_uptrendentry_name.append(s.base_asset)
            symbols_uptrendentry.append(count)
            status = "UP-ENTRY"
        elif s.status == Symbol.UPTRENDTP1:
            symbols_uptrendtp1_name.append(s.base_asset)
            symbols_uptrendtp1.append(count)
            status = "UP-TP1"
        elif s.status == Symbol.UPTRENDTP2:
            symbols_uptrendtp2_name.append(s.base_asset)
            symbols_uptrendtp2.append(count)
            status = "UP-TP2"
        elif s.status == Symbol.SLEEP:
            symbols_sleep_name.append(s.base_asset)
            symbols_sleep.append(count)
            status = "SLEEP"
        elif s.status == Symbol.DISABLED:
            symbols_disabled_name.append(s.base_asset)
            symbols_disabled.append(count)
            status = "DISABLE"
        else:
            status = "???"

        slp = '-'
        if s.next_sleep_wake != -1:
            slp = datetime.fromtimestamp(s.next_sleep_wake).strftime('%H:%M:%S')

        odr = '-'
        if s.order_check:
            odr = datetime.fromtimestamp(s.next_order_check).strftime('%H:%M:%S')

        ast = '-'
        if s.asset_check:
            ast = datetime.fromtimestamp(s.next_asset_check).strftime('%H:%M:%S')

        n1h = '-'
        if s.next_update_1h != -1:
            n1h = datetime.fromtimestamp(s.next_update_1h).strftime('%H:%M:%S')

        n5m = '-'
        if s.next_update_5m != -1:
            n5m = datetime.fromtimestamp(s.next_update_5m).strftime('%H:%M:%S')

        entry = '-'
        if s.entry is not None:
            entry = ('%.8f' % (s.entry))

        sl = '-'
        if s.sl is not None:
            sl = ('%.8f' % (s.sl))

        tp1 = '-'
        if s.entry is not None:
            tp1 = ('%.8f' % (s.tp1))

        tp2 = '-'
        if s.entry is not None:
            tp2 = ('%.8f' % (s.tp2))

        symbols_banner.append('%-10s | %-8s | slp:%-8s | odr:%-8s | ast:% -8s | 1h:%-8s | 5m:%-8s | ent:%-12s | sl:%-12s | tp1:%-12s | tp2:%-12s'
                % (s.base_asset, status, slp, odr, ast, n1h, n5m, entry, sl, tp1, tp2))

        count += 1


def getSymbolInstance(symbols, name):
    for s in symbols:
        if s.name == name:
            print(s.name)
            return s


def updateTradeListbox():
    segregateSymbols()
    ui.updateListBox(UI.TRADE_LISTBOX_DISABLED_ID,     symbols_disabled_name)
    ui.updateListBox(UI.TRADE_LISTBOX_SLEEP_ID,        symbols_sleep_name)
    ui.updateListBox(UI.TRADE_LISTBOX_ENABLED_ID,      symbols_enabled_name)
    ui.updateListBox(UI.TRADE_LISTBOX_UPTREND1H_ID,    symbols_uptrend1h_name)
    ui.updateListBox(UI.TRADE_LISTBOX_UPTREND5M_ID,    symbols_uptrend5m_name)
    ui.updateListBox(UI.TRADE_LISTBOX_UPTRENDENTRY_ID, symbols_uptrendentry_name)
    ui.updateListBox(UI.TRADE_LISTBOX_UPTRENDTP1_ID,   symbols_uptrendtp1_name)
    ui.updateListBox(UI.TRADE_LISTBOX_UPTRENDTP2_ID,   symbols_uptrendtp2_name)
    ui.updateListBox(UI.TRADE_LISTBOX_ALL_ID,          symbols_banner)


def onTradeButtonDisableClicked(name):
    s = getSymbolInstance(symbols_all, name + "USDT")
    s.setStatusDisable()
    updateTradeListbox()
    ui.deselectListBox()


def onTradeButtonEnableClicked(name):
    s = getSymbolInstance(symbols_all, name + "USDT")
    s.status = Symbol.ENABLED
    updateTradeListbox()
    ui.deselectListBox()


def onTradeButtonPlotClicked(name):
    for s in symbols_all:
        if name == s.base_asset:
            s.plot()


def handle_exit():
    for s in symbols_all:
        if (s.status == Symbol.UPTRENDENTRY or s.status == Symbol.UPTRENDTP1
                or s.status == Symbol.UPTRENDTP2):
            s.performOrderCheck()
            s.performAssetCheck()

    exit()


if __name__ == '__main__':

    pp = pprint.PrettyPrinter(indent=4)
    bnb = Bnb()

    symbols = bnb.getSymbols()
    if len(symbols) <= 0:
        exit()

    for s in symbols:
        symbols_all.append(Symbol(bnb, s))

    ui = UI(
        onTradeButtonDisableClicked,
        onTradeButtonEnableClicked,
        onTradeButtonPlotClicked,
    )

    ui.readEvent(0) # A read is required to update the window.
    updateTradeListbox()
    ui.readEvent(0) # Another read for the update to kick in.

    while True:

        if ui.readEvent(2000) < 0:
            handle_exit()

        # High priority - Process everything before returning to low priority

        for s in symbols_uptrendtp2:
            if symbols_all[s].serviceStatusUptrendTP2() == 0:
                updateTradeListbox()
            if ui.readEvent(0) < 0:
                handle_exit()

        for s in symbols_uptrendtp1:
            if symbols_all[s].serviceStatusUptrendTP1() == 0:
                updateTradeListbox()
            if ui.readEvent(0) < 0:
                handle_exit()

        for s in symbols_uptrendentry:
            if symbols_all[s].serviceStatusUptrendEntry() == 0:
                updateTradeListbox()
            if ui.readEvent(0) < 0:
                handle_exit()

        for s in symbols_uptrend5m:
            if symbols_all[s].serviceStatusUptrend5m() == 0:
                updateTradeListbox()
            if ui.readEvent(0) < 0:
                handle_exit()

        # Low priority - Process only 10 before returning to high priority

        low_hit = 0

        for s in symbols_uptrend1h:
            if symbols_all[s].serviceStatusUptrend1h() == 0:
                updateTradeListbox()
                low_hit += 1
                if low_hit >= 10:
                    break
            if ui.readEvent(0) < 0:
                handle_exit()

        if low_hit >= 10:
            continue

        for s in symbols_enabled:
            if symbols_all[s].serviceStatusEnabled() == 0:
                updateTradeListbox()
                low_hit += 1
                if low_hit >= 10:
                    break
            if ui.readEvent(0) < 0:
                handle_exit()

        if low_hit >= 10:
            continue

        for s in symbols_sleep:
            if symbols_all[s].serviceStatusSleep() == 0:
                updateTradeListbox()
                low_hit += 1
                if low_hit >= 10:
                    break
            if ui.readEvent(0) < 0:
                handle_exit()

        if low_hit >= 10:
            continue

        for s in symbols_disabled:
            if symbols_all[s].serviceStatusDisabled() == 0:
                updateTradeListbox()
                low_hit += 1
                if low_hit >= 10:
                    break
            if ui.readEvent(0) < 0:
                handle_exit()

        if low_hit >= 10:
            continue

        # Sleep longer if no high or low priority symbols to process

        #if len(symbols_uptrend5m) == 0 and len(symbols_uptrendentry) == 0 and len(symbols_uptrendtp1) == 0 and len(symbols_uptrendtp2):
        #    if ui.readEvent(2500) < 0:
        #        handle_exit()

