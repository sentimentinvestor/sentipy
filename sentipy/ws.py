import datetime
import json
import logging
import sys

import websocket

try:
    import thread
except ImportError:
    import _thread as thread


class _Stream:
    base_url = "ws://socket.sentimentinvestor.com/"
    __fragment = None
    __params = {}
    __user_callback = None
    __ws = None

    logging.basicConfig(level=logging.DEBUG)

    def __init__(self, token, key, callback):
        if token is None or key is None:
            raise ValueError(
                "Please provide a token and key - these can be obtained at "
                "https://sentimentinvestor.com/developer/dashboard")
        self.__params["key"] = key
        self.__params["token"] = token

        self.__user_callback = callback

        self.__connect()

    def __send_key(self, *args):
        if self.__ws is None:
            return
        # send authentication token and key + any necessary parameters
        self.__ws.send(json.dumps(self.__params))

    def __on_open(self, ws):
        logging.info("WebSocket opened")
        thread.start_new_thread(self.__send_key, ())

    def __on_error(self, ws, error):
        logging.error(f"WebSocket error {error}")

    def __on_close(self, ws, close_status_code, close_msg):
        logging.warning(f"WebSocket closed with status code {close_status_code}. Info provided: {close_msg}")

        # reconnect
        self.__ws = None
        try:
            self.__connect()
        except KeyboardInterrupt:
            logging.info("Not reconnecting WebSocket")
            sys.exit()

    def __on_message(self, ws, message):
        logging.debug(message)
        response = json.loads(message)
        if "authState" in response:
            # notify the client if authentication unsuccessful
            if not response["authState"]:
                raise ValueError("Not authenticated or invalid request")
            else:
                time_formatted = datetime.datetime.utcfromtimestamp(
                    response['timestamp'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
                logging.info(f"WebSocket authentication successful as of {time_formatted}")
                logging.info(f"Subscribed to the following stocks: {', '.join(response['subscribedTo'])}")
        else:
            self.__user_callback(StockUpdateData(message))

    def __connect(self):
        websocket.enableTrace(True)

        if self.__fragment is None:
            raise Exception("Use StocksStream or AllStocksStream, cannot use Stream base class!")

        # initialise websocket
        self.__ws = websocket.WebSocketApp(self.base_url + self.__fragment,
                                           on_open=self.__on_open,
                                           on_error=self.__on_error,
                                           on_close=self.__on_close,
                                           on_message=self.__on_message)

        self.__ws.run_forever(ping_interval=30, ping_timeout=10, ping_payload="ping")

    def reconnect(self):
        """
        Manually request a websocket reconnection.
        This should not usually be necessary as Sentipy will try to reconnect automatically if connection is lost
        :return: None
        """
        self.__connect()


class StocksStream(_Stream):
    __fragment = "stocks"

    def __init__(self, symbols=None, token=None, key=None, callback=None):
        """
        Initialise a new WebSocket listener for specific stocks
        :param symbols: an iterable of symbols specifying which stock changes to listen for
        :param token: your SentimentInvestor token
        :param key:  your SentimentInvestor key
        :param callback:  a function taking one argument, a StockUpdateData object,
        that will be called when a stock update is received
        """
        self.__params["symbols"] = list(symbols) if symbols is not None else []
        super(StocksStream, self).__init__(token, key, callback)


class AllStocksStream(_Stream):
    __fragment = "all"

    def __init__(self, token=None, key=None, callback=None):
        """
        Initialise a new WebSocket listener for all available stocks
        :param token: your SentimentInvestor token
        :param key:  your SentimentInvestor key
        :param callback:  a function taking one argument, a StockUpdateData object,
        that will be called when a stock update is received
        """
        super(AllStocksStream, self).__init__(token, key, callback)


class StockUpdateData:
    def __init__(self, message):
        """
        Initialise a new data container for the stock update
        :param message: A JSON string returned by the websocket server
        """
        for k, v in json.loads(message).items():
            setattr(self, k, v)
