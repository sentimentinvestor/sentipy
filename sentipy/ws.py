"""This provides websocket support for Sentiment Investor.

For more information, please visit https://docs.sentimentinvestor.com/RESTful/websocket
"""

# TODO: Refactor to use the threading library
import _thread as thread
import datetime
import json
import logging
import sys
from typing import Callable, Optional

from beartype import beartype

# websocket comes with no type hints
from websocket import WebSocketApp  # type: ignore[import]

from ._typing_imports import DictType, IterableType


# Defined at the top since it's used in type annotations
class StockUpdateData:
    """A new data container for the stock update."""

    @beartype
    def __init__(self, message: str) -> None:
        """Defines attributes from the message for the new container.

        Args:
            message: A JSON string returned by the websocket server
        """
        for k, v in json.loads(message).items():
            setattr(self, k, v)


# Used to add type annotations for callable arguments
CallableType = Callable[[StockUpdateData], None]


class _Stream:
    """Base class for different kinds of websocket streams."""

    base_url = "ws://socket.sentimentinvestor.com/"
    """
    WebSocket url to connect to
    """

    __params: DictType[str, str] = {}
    __ws = None

    @beartype
    def __init__(
        self, token: str, key: str, callback: CallableType, fragment: str
    ) -> None:
        """Initialise a new web socket stream.

        Args:
            token: SentimentInvestor API token
            key: SentimentInvestor API key
            callback: function accepting one argument of type `StockUpdateData` that is called when data is received
            fragment: the websocket endpoint to contact

        Raises:
            ValueError: if token or key is omitted
        """
        self.__params["key"] = key
        self.__params["token"] = token

        self.__user_callback = callback
        self.__fragment = fragment

        self.__connect()

    @beartype
    def __send_key(self, *args: str) -> None:
        if self.__ws is None:
            return
        # send authentication token and key + any necessary parameters
        self.__ws.send(json.dumps(self.__params))

    @beartype
    def __on_open(self, ws: WebSocketApp) -> None:
        logging.info("WebSocket opened")
        thread.start_new_thread(self.__send_key, ())

    @beartype
    def __on_error(self, ws: WebSocketApp, error: str) -> None:
        logging.error(f"WebSocket error {error}")

    @beartype
    def __on_close(
        self, ws: WebSocketApp, close_status_code: int, close_msg: str
    ) -> None:
        logging.warning(
            f"WebSocket closed with status code {close_status_code}. Info provided: {close_msg}"
        )

        # reconnect
        self.__ws = None
        try:
            self.__connect()
        except KeyboardInterrupt:
            logging.info("Not reconnecting WebSocket")
            sys.exit()

    @beartype
    def __on_message(self, ws: WebSocketApp, message: str) -> None:
        logging.debug(message)
        response = json.loads(message)
        if "authState" in response:
            # notify the client if authentication unsuccessful
            if not response["authState"]:
                raise ValueError("Not authenticated or invalid request")
            else:
                time_formatted = datetime.datetime.utcfromtimestamp(
                    response["timestamp"] / 1000
                ).strftime("%Y-%m-%d %H:%M:%S")
                logging.info(
                    f"WebSocket authentication successful as of {time_formatted}"
                )
                logging.info(
                    f"Subscribed to the following stocks: {', '.join(response['subscribedTo'])}"
                )
        else:
            self.__user_callback(StockUpdateData(message))

    @beartype
    def __connect(self) -> None:

        # initialise websocket
        self.__ws = WebSocketApp(
            self.base_url + self.__fragment,
            on_open=self.__on_open,
            on_error=self.__on_error,
            on_close=self.__on_close,
            on_message=self.__on_message,
        )

        self.__ws.run_forever(ping_interval=30, ping_timeout=10, ping_payload="ping")

    @beartype
    def reconnect(self) -> None:
        """Manually request a websocket reconnection.

        This should not usually be necessary as SentiPy will try to reconnect automatically if connection is lost.
        """
        self.__connect()


class StocksStream(_Stream):
    """A WebSocket listener for specific stocks."""

    @beartype
    def __init__(
        self,
        token: str,
        key: str,
        callback: CallableType,
        symbols: Optional[IterableType[str]] = None,
    ) -> None:
        """Initialises the new websocket listener.

        Args:
            symbols: an iterable of symbols specifying which stock changes to listen for
            token: SentimentInvestor API token
            key: SentimentInvestor API key
            callback: a function taking one argument, a StockUpdateData object,
            that will be called when a stock update is received
        """
        self.__params["symbols"] = list(symbols) if symbols is not None else []
        super().__init__(token, key, callback, "stocks")


class AllStocksStream(_Stream):
    """A WebSocket listener for all available stocks."""

    @beartype
    def __init__(self, token: str, key: str, callback: CallableType) -> None:
        """Initialises the new websocket listener.

        Args:
            token: SentimentInvestor API token
            key: SentimentInvestor API key
            callback: a function taking one argument, a StockUpdateData object,
            that will be called when a stock update is received
        """
        super().__init__(token, key, callback, "all")
