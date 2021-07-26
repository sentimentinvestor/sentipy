import enum
import json
from typing import Optional, Any, Union
from sentipy._typing_imports import DictType, ListType, SetType

import requests


class AccountTier(enum.Enum):
    SANDBOX = 0
    STARTER = 1
    PREMIUM = 1.5
    ENTERPRISE = 2


class _ApiResponse:
    """
    Specifies a basic data item for a specific ticker.
    .. attention:: Do not try to initialise one yourself.
    """

    def __init__(self, json):
        # for every metric returned in the json set it as an attribute for this object
        for k, v in json.items():
            # do not create a results parameter if present as this is handled by derived classes separately
            if k == "results":
                continue
            setattr(self, k, v)

    def __repr__(self) -> str:
        return str(self.__dict__)


class _ApiResult(_ApiResponse):
    """
    For a list of available metrics, use `dir(object)`
    .. attention:: Returned by quote, do not try to initialise one yourself.
    """

    def __init__(self, json):
        super().__init__(json)
        for k, v in json.get("results").items():
            setattr(self, k, v)


class Sentipy:
    """
    The Sentipy module provides a simple and lightweight way to interact with the SentimentInvestor API and data.

    Sentipy is installed through [pip](https://pip.pypa.io/)
    ```
    $ python3 -m pip install sentiment-investor
    ```
    """

    base_url = r"https://api.sentimentinvestor.com/v4/"
    """
    The base URL of the SentimentInvestor API
    """

    def __init__(self, token: str = None, key: str = None):
        """
        Initialise a new SentiPy instance with your token and key

        Examples:
            >>> token = "my-very-secret-token"
            >>> key = "my-very-secret-key"
            >>> sentipy = Sentipy(token=token, key=key)

        Args:
            token (str): API token from the SentimentInvestor website
            key (str): API key from the SentimentInvestor website

        Raises:
            `ValueError` if either `token` or `key` not provided
        """
        if token is None or key is None:
            raise ValueError(
                "Please provide a token and key - these can be obtained at "
                "https://sentimentinvestor.com/developer/dashboard")
        self.token = token
        self.key = key

    def _base_request(self, endpoint: str, params: DictType[str, Any] = None) -> DictType[str, Any]:
        """
        Make a request to a specific REST endpoint on the SentimentInvestor API

        Args:
            endpoint (str): the REST endpoint (final fragment in URL)
            params (dict): any supplementary parameters to pass to the API

        Returns: the JSON response if the request was successful, otherwise None

        """
        if params is None:
            params = {}
        url = self.base_url + endpoint
        params["token"] = self.token
        params["key"] = self.key
        response = requests.get(url, params)
        if response.content.decode("utf-8") == 'invalid_parameter' \
                or response.content.decode("utf-8") == 'incorrect_key':
            raise ValueError("Incorrect key or token")
        else:
            try:
                data = response.json()
            except json.JSONDecodeError:
                raise Exception(response.text)

            if response.ok:
                return data
            else:
                raise Exception(data.message)

    def parsed(self, symbol: str) -> _ApiResult:
        """
        The parsed data endpoints provides the four core metrics for a stock: AHI, RHI, SGP and sentiment.

        Args:
            symbol (str): string specifying the ticker or symbol of the stock to request data for

        Returns: a QuoteData object
        
        Examples:
            >>> parsed_data = sentipy.parsed("AAPL")
            >>> print(parsed_data.AHI)
            0.8478140394088669

        .. versionadded:: 2.0.0
        """
        params = {
            "symbol": symbol
        }
        return _ApiResult(self._base_request("parsed", params=params))

    def raw(self, symbol: str) -> _ApiResult:
        """
        The raw data endpoint provides access to raw data metrics for the monitored social platforms

        Args:
            symbol (str): ticker or symbol of the stock to request data for

        Returns: a QuoteData object

        .. versionadded:: 2.0.0
        """
        params = {
            "symbol": symbol
        }
        return _ApiResult(self._base_request("raw", params=params))

    def quote(self, symbol: str, enrich: bool = False) -> _ApiResult:
        """
        The quote data endpoint provides access to all realtime data about stocks along with further data if requested

        Args:
            symbol (str): ticker or symbol of the stock to request data for
            enrich (bool): whether to request enriched data

        Returns: a QuoteData object

        Examples:
            >>> quote_data = sentipy.quote("TSLA", enrich=True)
            >>> print([var for var in dir(quote_data) if not var.startswith("_")])
            ['AHI',
             'RHI',
             'reddit_comment_mentions',
             'reddit_comment_relative_hype',
             'reddit_comment_sentiment',
             'reddit_post_mentions',
             'reddit_post_relative_hype',
             'reddit_post_sentiment',
             'sentiment',
             'stocktwits_post_mentions',
             'stocktwits_post_relative_hype',
             'stocktwits_post_sentiment',
             'subreddits',
             'success',
             'symbol',
             'tweet_mentions',
             'tweet_relative_hype',
             'yahoo_finance_comment_mentions',
             'yahoo_finance_comment_relative_hype',
             'yahoo_finance_comment_sentiment']
            >>> print(quote_data.reddit_comment_mentions)
            20
            >>> print(quote_data.subreddits) # only for 'enriched' requests
            {'reddit_subreddit_mentions': {'WallStreetBetsELITE': 1,
                                           'investing': 2,
                                           'smallstreetbets': 1,
                                           'stocks': 10,
                                           'wallstreetbets': 7},
             'reddit_subreddit_sentiment': {'WallStreetBetsELITE': 1,
                                            'investing': 0,
                                            'smallstreetbets': 0,
                                            'stocks': 0.8,
                                            'wallstreetbets': 0.5}}
        """
        params = {
            "symbol": symbol,
            "enrich": enrich
        }
        return _ApiResult(self._base_request("quote", params=params))

    def sort(self, metric: str, limit: int) -> ListType[_ApiResponse]:
        """
        The sort data endpoint provides access to ordered rankings of stocks across core metrics

        Args:
            metric (str): the metric by which to sort the stocks
            limit (int): the maximum number of stocks to return

        Returns: a list of TickerData objects

        Examples:
            >>> metric = "AHI"
            >>> limit = 4
            >>> sort_data = sentipy.sort(metric, limit)
            >>> for ticker in sort_data:
            ...     print(ticker)
            ...
            {'AHI': 1.9201046798029555, 'RHI': 1.2556815851300576, 'rank': 0, 'reddit_comment_mentions': 59, 'reddit_post_mentions': 0, 'sentiment': 0.7080172560355916, 'stocktwits_post_mentions': 171, 'subreddits': {'symbol': 'AMC'}, 'symbol': 'AMC', 'tweet_mentions': 149, 'yahoo_finance_comment_mentions': 396}
            {'AHI': 1.833990147783251, 'RHI': 1.506333195051962, 'rank': 1, 'reddit_comment_mentions': 4, 'reddit_post_mentions': 0, 'sentiment': 0.925215723873442, 'stocktwits_post_mentions': 508, 'subreddits': {'symbol': 'ET'}, 'symbol': 'ET', 'tweet_mentions': 0, 'yahoo_finance_comment_mentions': 0}
            {'AHI': 1.3133928571428573, 'RHI': 1.0435689663713186, 'rank': 2, 'reddit_comment_mentions': 58, 'reddit_post_mentions': 0, 'sentiment': 0.7033474218089603, 'stocktwits_post_mentions': 262, 'subreddits': {'symbol': 'SPY'}, 'symbol': 'SPY', 'tweet_mentions': 20, 'yahoo_finance_comment_mentions': 3}
            {'AHI': 0.8098830049261084, 'RHI': 1.4870815942458393, 'rank': 3, 'reddit_comment_mentions': 62, 'reddit_post_mentions': 0, 'sentiment': 0.7574809805579037, 'stocktwits_post_mentions': 113, 'subreddits': {'symbol': 'AAPL'}, 'symbol': 'AAPL', 'tweet_mentions': 20, 'yahoo_finance_comment_mentions': 13}
        """
        params = {
            "metric": metric,
            "limit": limit
        }
        return [_ApiResponse(dp) for dp in self._base_request("sort", params=params).get("results")]

    def historical(self, symbol: str, metric: str, start: int, end: int) -> DictType[Union[int, float], Union[int, float]]:
        """
        The historical data endpoint provides access to historical data for stocks

        Args:
            symbol (str): the stock to look up historical data for
            metric (str): the metric for which to return data
            start (int): Unix epoch timestamp in seconds specifying start of date range
            end (int): Unix epoch timestamp in seconds specifying end of date range

        Returns (dict): a dictionary of (timestamp -> data entry) mappings.

        Examples:
            >>> historical_data = sentipy.historical("AAPL", "RHI", 1614556869, 1619654469)
            >>> for timestamp, value in sorted(historical_data.items()):
            ...     print(timestamp, value)
            ...
            1618057166.5252028 5.9384505075115675e-05
            1618336173.950567 0.0004624613455115948
            1618338607.466995 0.0005780098550856681
            (...lots of lines omitted)

        """
        params = {
            "symbol": symbol,
            "metric": metric,
            "start": start,
            "end": end
        }
        return {dp.get("timestamp"): dp.get("data") for dp in
                self._base_request("historical", params=params).get("results")}

    def bulk(self, symbols: ListType[str], enrich: bool = False) -> ListType[_ApiResponse]:
        """
        Get quote data for several stocks simultaneously
        
        Args:
            symbols (iterable): list of stocks to get quote data for
            enrich (bool): whether to get enriched data
            
        Returns: a list of TickerData objects

        .. versionadded:: 2.0.0
        """
        params = {
            "symbols": ",".join(symbols),
            "enrich": enrich
        }
        return [_ApiResponse(result) for result in self._base_request("bulk", params=params).get("results")]

    def all(self, enrich: bool = False) -> ListType[_ApiResponse]:
        """
        Get all data for all stocks simultaneously. 

        .. note:: this blocking call takes a long time to execute.

        Args:
            enrich (bool): whether to fetch enriched data

        Returns: a list of TickerData objects

        .. versionadded:: 2.0.0
        """
        params = {"enrich": enrich}
        return [_ApiResponse(result) for result in self._base_request("all", params=params).get("results")]

    def supported(self, symbol: str) -> bool:
        """
        Query whether SentimentInvestor has data for a specified stock

        Args:
            symbol (str): stock ticker symbol to query

        Returns: boolean whether supported or not

        Examples:
            >>> for stock in ["AAPL", "TSLA", "SNTPY"]:
            ...     print(f"{stock} {'is' if sentipy.supported(stock) else 'is not'} supported.")
            ...
            AAPL is supported.
            TSLA is supported.
            SNTPY is not supported.

        .. versionadded:: 2.0.0
        """
        return self._base_request("supported", params={"symbol": symbol}).get("result")

    def all_stocks(self) -> SetType[str]:
        """
        Get a list of all stocks for which Sentiment gather data

        Returns (set[str]): list of stock symbols

        .. versionadded:: 2.0.0
        """
        return set(self._base_request("all-stocks").get("results"))

    @property
    def account_info(self) -> Optional[_ApiResponse]:
        return _ApiResponse(self._base_request("account"))

    @property
    def api_credentials(self):
        return self.token, self.key
