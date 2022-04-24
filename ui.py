import PySimpleGUI as sg

class UI:

    TRADE_LISTBOX_DISABLED_ID      = '-TRADE-DISABLED-'
    TRADE_LISTBOX_SLEEP_ID         = '-TRADE-SLEEP-'
    TRADE_LISTBOX_ENABLED_ID       = '-TRADE-ENABLED-'
    TRADE_LISTBOX_UPTREND1H_ID     = '-TRADE-UPTREND1H-'
    TRADE_LISTBOX_UPTREND5M_ID     = '-TRADE-UPTREND5M-'
    TRADE_LISTBOX_UPTRENDENTRY_ID  = '-TRADE-UPTRENDENTRY-'
    TRADE_LISTBOX_UPTRENDTP1_ID    = '-TRADE-UPTRENDTP1-'
    TRADE_LISTBOX_UPTRENDTP2_ID    = '-TRADE-UPTRENDTP2-'
    TRADE_LISTBOX_ALL_ID           = '-TRADE-ALL-'

    TRADE_BUTTON_ENABLE_ID         = '-TRADE_ENABLE-'
    TRADE_BUTTON_DISABLE_ID        = '-TRADE_DISABLE-'
    TRADE_BUTTON_PLOT_ID           = '-TRADE_PLOT-'


    def __init__    (
                self,
                trade_button_disable_clicked_cb,
                trade_button_enable_clicked_cb,
                trade_button_plot_clicked_cb
            ):

        # Register callbacks

        self.trade_button_enable_clicked_cb = trade_button_enable_clicked_cb
        self.trade_button_disable_clicked_cb = trade_button_disable_clicked_cb
        self.trade_button_plot_clicked_cb = trade_button_plot_clicked_cb

        # Trade listboxes

        trade_listbox_disabled = sg.Listbox(
            values=[],
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            enable_events=True,
            size=(7, 15),
            font=['ubuntu mono',10],
            key=self.TRADE_LISTBOX_DISABLED_ID
        )

        trade_listbox_sleep = sg.Listbox(
            values=[],
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            enable_events=True,
            size=(7, 15),
            font=['ubuntu mono',10],
            key=self.TRADE_LISTBOX_SLEEP_ID
        )

        trade_listbox_enabled = sg.Listbox(
            values=[],
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            enable_events=True,
            size=(7, 15),
            font=['ubuntu mono',10],
            key=self.TRADE_LISTBOX_ENABLED_ID
        )

        trade_listbox_uptrend1h = sg.Listbox(
            values=[],
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            enable_events=True,
            size=(7, 15),
            font=['ubuntu mono',10],
            key=self.TRADE_LISTBOX_UPTREND1H_ID
        )

        trade_listbox_uptrend5m = sg.Listbox(
            values=[],
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            enable_events=True,
            size=(7, 15),
            font=['ubuntu mono',10],
            key=self.TRADE_LISTBOX_UPTREND5M_ID
        )

        trade_listbox_uptrendentry = sg.Listbox(
            values=[],
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            enable_events=True,
            size=(7, 15),
            font=['ubuntu mono',10],
            key=self.TRADE_LISTBOX_UPTRENDENTRY_ID
        )

        trade_listbox_uptrendtp1 = sg.Listbox(
            values=[],
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            enable_events=True,
            size=(7, 15),
            font=['ubuntu mono',10],
            key=self.TRADE_LISTBOX_UPTRENDTP1_ID
        )

        trade_listbox_uptrendtp2 = sg.Listbox(
            values=[],
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            enable_events=True,
            size=(7, 15),
            font=['ubuntu mono',10],
            key=self.TRADE_LISTBOX_UPTRENDTP2_ID
        )

        trade_listbox_all = sg.Listbox(
            values=[],
            select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
            enable_events=True,
            size=(175, 15),
            font=['ubuntu mono',10],
            key=self.TRADE_LISTBOX_ALL_ID
        )

        # Trade buttons

        trade_button_enable = sg.Button(
            button_text='Enable',
            size=(10, 1),
            disabled=True,
            key=self.TRADE_BUTTON_ENABLE_ID
        )

        trade_button_disable = sg.Button(
            button_text='Disable',
            size=(10, 1),
            disabled=True,
            key=self.TRADE_BUTTON_DISABLE_ID
        )

        trade_button_plot = sg.Button(
            button_text='Plot',
            size=(10, 1),
            disabled=True,
            key=self.TRADE_BUTTON_PLOT_ID
        )

        # Trade frames

        trade_frame_disabled = sg.Frame(
            title='Disabled',
            layout=[[trade_listbox_disabled]]
        )

        trade_frame_sleep = sg.Frame(
            title='Sleep',
            layout=[[trade_listbox_sleep]],
            pad=((5,0),(0,0))
        )

        trade_frame_enabled = sg.Frame(
            title='Enabled',
            layout=[[trade_listbox_enabled]],
            pad=((70,0),(0,0))
        )

        trade_frame_uptrend1h = sg.Frame(
            title='Up 1h',
            layout=[[trade_listbox_uptrend1h]],
            pad=((70,0),(0,0))
        )

        trade_frame_uptrend5m = sg.Frame(
            title='Up 5m',
            layout=[[trade_listbox_uptrend5m]],
            pad=((5,0),(0,0))
        )

        trade_frame_uptrendentry = sg.Frame(
            title='Up Entry',
            layout=[[trade_listbox_uptrendentry]],
            pad=((5,0),(0,0))
        )

        trade_frame_uptrendtp1 = sg.Frame(
            title='Up TP1',
            layout=[[trade_listbox_uptrendtp1]],
            pad=((5,0),(0,0))
        )

        trade_frame_uptrendtp2 = sg.Frame(
            title='Up TP2',
            layout=[[trade_listbox_uptrendtp2]],
            pad=((5,0),(0,0))
        )

        trade_frame_all = sg.Frame(
            title='All',
            layout=[[trade_listbox_all]],
            pad=((5,0),(0,0))
        )

        # Trade tab

        trade_tab = sg.Tab(
            title='Trade',
            layout=[[trade_frame_disabled, trade_frame_sleep, trade_frame_enabled, trade_frame_uptrend1h, trade_frame_uptrend5m, trade_frame_uptrendentry, trade_frame_uptrendtp1, trade_frame_uptrendtp2 ],
                [trade_frame_all],
                [trade_button_enable, trade_button_disable, trade_button_plot]]
        )

        # Tab group

        tab_group = sg.TabGroup(
            layout=[[trade_tab]]
        )

        # Window

        self.window = sg.Window(
            title='Midas',
            layout=[[tab_group]]
        )

        # Misc variables

        self.trade_selected_symbol = None


    def __selectTradeListboxItem(self, listbox_id, symbol):
        all = self.window.Element(listbox_id).get_list_values()
        c = 0
        for a in all:
            if symbol in a:
                self.window.Element(listbox_id).Update(set_to_index=c, scroll_to_index=c)
                return 0
            c += 1
        self.window.Element(listbox_id).Update(set_to_index=[])
        return -1


    def __handleTradeListboxItemClicked(self, event):

        if event == self.TRADE_LISTBOX_DISABLED_ID:
            symbol = self.window.Element(self.TRADE_LISTBOX_DISABLED_ID).get()
            if symbol:
                self.trade_selected_symbol = symbol[0]
                self.__selectTradeListboxItem(self.TRADE_LISTBOX_ALL_ID, symbol[0])
                self.window.Element(self.TRADE_LISTBOX_SLEEP_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_ENABLED_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTREND1H_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTREND5M_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTRENDENTRY_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTRENDTP1_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTRENDTP2_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_BUTTON_ENABLE_ID).Update(disabled=False)
                self.window.Element(self.TRADE_BUTTON_DISABLE_ID).Update(disabled=True)
                self.window.Element(self.TRADE_BUTTON_PLOT_ID).Update(disabled=False)

        if event == self.TRADE_LISTBOX_SLEEP_ID:
            symbol = self.window.Element(self.TRADE_LISTBOX_SLEEP_ID).get()
            if symbol:
                self.trade_selected_symbol = symbol[0]
                self.__selectTradeListboxItem(self.TRADE_LISTBOX_ALL_ID, symbol[0])
                self.window.Element(self.TRADE_LISTBOX_DISABLED_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_ENABLED_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTREND1H_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTREND5M_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTRENDENTRY_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTRENDTP1_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTRENDTP2_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_BUTTON_ENABLE_ID).Update(disabled=False)
                self.window.Element(self.TRADE_BUTTON_DISABLE_ID).Update(disabled=True)
                self.window.Element(self.TRADE_BUTTON_PLOT_ID).Update(disabled=False)

        elif event == self.TRADE_LISTBOX_ENABLED_ID:
            symbol = self.window.Element(self.TRADE_LISTBOX_ENABLED_ID).get()
            if symbol:
                self.trade_selected_symbol = symbol[0]
                self.__selectTradeListboxItem(self.TRADE_LISTBOX_ALL_ID, symbol[0])
                self.window.Element(self.TRADE_LISTBOX_DISABLED_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_SLEEP_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTREND1H_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTREND5M_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTRENDENTRY_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTRENDTP1_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTRENDTP2_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_BUTTON_ENABLE_ID).Update(disabled=True)
                self.window.Element(self.TRADE_BUTTON_DISABLE_ID).Update(disabled=False)
                self.window.Element(self.TRADE_BUTTON_PLOT_ID).Update(disabled=False)

        elif event == self.TRADE_LISTBOX_UPTREND1H_ID:
            symbol = self.window.Element(self.TRADE_LISTBOX_UPTREND1H_ID).get()
            if symbol:
                self.trade_selected_symbol = symbol[0]
                self.__selectTradeListboxItem(self.TRADE_LISTBOX_ALL_ID, symbol[0])
                self.window.Element(self.TRADE_LISTBOX_DISABLED_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_SLEEP_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_ENABLED_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTREND5M_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTRENDENTRY_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTRENDTP1_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTRENDTP2_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_BUTTON_ENABLE_ID).Update(disabled=True)
                self.window.Element(self.TRADE_BUTTON_DISABLE_ID).Update(disabled=False)
                self.window.Element(self.TRADE_BUTTON_PLOT_ID).Update(disabled=False)

        elif event == self.TRADE_LISTBOX_UPTREND5M_ID:
            symbol = self.window.Element(self.TRADE_LISTBOX_UPTREND5M_ID).get()
            if symbol:
                self.trade_selected_symbol = symbol[0]
                self.__selectTradeListboxItem(self.TRADE_LISTBOX_ALL_ID, symbol[0])
                self.window.Element(self.TRADE_LISTBOX_DISABLED_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_SLEEP_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_ENABLED_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTREND1H_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTRENDENTRY_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTRENDTP1_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTRENDTP2_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_BUTTON_ENABLE_ID).Update(disabled=True)
                self.window.Element(self.TRADE_BUTTON_DISABLE_ID).Update(disabled=False)
                self.window.Element(self.TRADE_BUTTON_PLOT_ID).Update(disabled=False)

        elif event == self.TRADE_LISTBOX_UPTRENDENTRY_ID:
            symbol = self.window.Element(self.TRADE_LISTBOX_UPTRENDENTRY_ID).get()
            if symbol:
                self.trade_selected_symbol = symbol[0]
                self.__selectTradeListboxItem(self.TRADE_LISTBOX_ALL_ID, symbol[0])
                self.window.Element(self.TRADE_LISTBOX_DISABLED_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_SLEEP_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_ENABLED_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTREND1H_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTREND5M_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTRENDTP1_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTRENDTP2_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_BUTTON_ENABLE_ID).Update(disabled=True)
                self.window.Element(self.TRADE_BUTTON_DISABLE_ID).Update(disabled=False)
                self.window.Element(self.TRADE_BUTTON_PLOT_ID).Update(disabled=False)

        elif event == self.TRADE_LISTBOX_UPTRENDTP1_ID:
            symbol = self.window.Element(self.TRADE_LISTBOX_UPTRENDTP1_ID).get()
            if symbol:
                self.trade_selected_symbol = symbol[0]
                self.__selectTradeListboxItem(self.TRADE_LISTBOX_ALL_ID, symbol[0])
                self.window.Element(self.TRADE_LISTBOX_DISABLED_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_SLEEP_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_ENABLED_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTREND1H_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTREND5M_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTRENDENTRY_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTRENDTP2_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_BUTTON_ENABLE_ID).Update(disabled=True)
                self.window.Element(self.TRADE_BUTTON_DISABLE_ID).Update(disabled=False)
                self.window.Element(self.TRADE_BUTTON_PLOT_ID).Update(disabled=False)

        elif event == self.TRADE_LISTBOX_UPTRENDTP2_ID:
            symbol = self.window.Element(self.TRADE_LISTBOX_UPTRENDTP1_ID).get()
            if symbol:
                self.trade_selected_symbol = symbol[0]
                self.__selectTradeListboxItem(self.TRADE_LISTBOX_ALL_ID, symbol[0])
                self.window.Element(self.TRADE_LISTBOX_DISABLED_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_SLEEP_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_ENABLED_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTREND1H_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTREND5M_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTRENDENTRY_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_LISTBOX_UPTRENDTP1_ID).Update(set_to_index=[])
                self.window.Element(self.TRADE_BUTTON_ENABLE_ID).Update(disabled=True)
                self.window.Element(self.TRADE_BUTTON_DISABLE_ID).Update(disabled=False)
                self.window.Element(self.TRADE_BUTTON_PLOT_ID).Update(disabled=False)

        elif event == self.TRADE_LISTBOX_ALL_ID:
            self.window.Element(self.TRADE_BUTTON_ENABLE_ID).Update(disabled=False)
            self.window.Element(self.TRADE_BUTTON_DISABLE_ID).Update(disabled=False)
            self.window.Element(self.TRADE_BUTTON_PLOT_ID).Update(disabled=False)
            line = self.window.Element(self.TRADE_LISTBOX_ALL_ID).get()
            if line:
                symbol = line[0].partition(' ')[0]
                self.trade_selected_symbol = symbol
                if self.__selectTradeListboxItem(self.TRADE_LISTBOX_DISABLED_ID, symbol) == 0:
                    self.window.Element(self.TRADE_BUTTON_DISABLE_ID).Update(disabled=True)
                else:
                    self.window.Element(self.TRADE_BUTTON_ENABLE_ID).Update(disabled=True)
                self.__selectTradeListboxItem(self.TRADE_LISTBOX_SLEEP_ID, symbol)
                self.__selectTradeListboxItem(self.TRADE_LISTBOX_ENABLED_ID, symbol)
                self.__selectTradeListboxItem(self.TRADE_LISTBOX_UPTREND1H_ID, symbol)
                self.__selectTradeListboxItem(self.TRADE_LISTBOX_UPTREND5M_ID, symbol)
                self.__selectTradeListboxItem(self.TRADE_LISTBOX_UPTRENDENTRY_ID, symbol)
                self.__selectTradeListboxItem(self.TRADE_LISTBOX_UPTRENDTP1_ID, symbol)
                self.__selectTradeListboxItem(self.TRADE_LISTBOX_UPTRENDTP2_ID, symbol)


    def __handleTradeButtonClicked(self, event):
        if event == self.TRADE_BUTTON_DISABLE_ID:
            self.trade_button_disable_clicked_cb(self.trade_selected_symbol)
        elif event == self.TRADE_BUTTON_ENABLE_ID:
            self.trade_button_enable_clicked_cb(self.trade_selected_symbol)
        elif event == self.TRADE_BUTTON_PLOT_ID:
            self.trade_button_plot_clicked_cb(self.trade_selected_symbol)


    def updateListBox(self, listbox_id, values):
        idx = self.window.Element(listbox_id).get_indexes()
        scroll = self.window.Element(listbox_id).TKListbox.yview()
        if idx:
            self.window.Element(listbox_id).Update(values=values, set_to_index=idx[0])
        else:
            self.window.Element(listbox_id).Update(values=values)
        self.window.Element(listbox_id).set_vscroll_position(scroll[0])


    def deselectListBox(self):
        self.window.Element(self.TRADE_LISTBOX_ALL_ID).Update(set_to_index=[])
        self.window.Element(self.TRADE_LISTBOX_DISABLED_ID).Update(set_to_index=[])
        self.window.Element(self.TRADE_LISTBOX_SLEEP_ID).Update(set_to_index=[])
        self.window.Element(self.TRADE_LISTBOX_ENABLED_ID).Update(set_to_index=[])
        self.window.Element(self.TRADE_LISTBOX_UPTREND1H_ID).Update(set_to_index=[])
        self.window.Element(self.TRADE_LISTBOX_UPTREND5M_ID).Update(set_to_index=[])
        self.window.Element(self.TRADE_LISTBOX_UPTRENDENTRY_ID).Update(set_to_index=[])
        self.window.Element(self.TRADE_LISTBOX_UPTRENDTP1_ID).Update(set_to_index=[])
        self.window.Element(self.TRADE_LISTBOX_UPTRENDTP2_ID).Update(set_to_index=[])
        self.window.Element(self.TRADE_BUTTON_ENABLE_ID).Update(disabled=True)
        self.window.Element(self.TRADE_BUTTON_DISABLE_ID).Update(disabled=True)
        self.window.Element(self.TRADE_BUTTON_PLOT_ID).Update(disabled=True)


    def readEvent(self, timeout):
        event, value = self.window.read(timeout=timeout)
        if event == sg.WIN_CLOSED:
            return -1

        self.__handleTradeListboxItemClicked(event)
        self.__handleTradeButtonClicked(event)

#        print(event)
        self.eventValue = value
        return 1


    def close(self):
        self.window.close()
