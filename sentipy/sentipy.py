from json import JSONDecodeError

import requests


class Sentipy:
    base_url = r"https://api.sentimentinvestor.com/v4/"

    def __init__(self, token=None, key=None):
        """
        Initialise a new SentiPy instance with the provided token and key
        :param token: token is a string obtained from SentimentInvestor website
        :param key: key is a string obtained from SentimentInvestor website
        """
        if token is None or key is None:
            raise ValueError(
                "Please provide a token and key - these can be obtained at "
                "https://sentimentinvestor.com/developer/dashboard")
        self.token = token
        self.key = key

    def __base_request(self, endpoint, params=None):
        """
        Make a request to a specific REST endpoint on the SentimentInvestor API
        :param endpoint: The final __fragment specifying the endpoint to call
        :param params: A dictionary of any necessary parameters
        :return: returns the JSON response if the request was successful, otherwise None
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
                json = response.json()
            except JSONDecodeError:
                raise Exception(response.text)

            if response.ok:
                return json
            else:
                raise Exception(json.get("message"))

    def parse(self, symbol):
        """
        The parsed data endpoints provides the four core metrics for a stock: AHI, RHI, SGP and sentiment.
        :param symbol: String specifying the ticker or symbol of the stock to request data for
        :return: returns a QuoteData object
        """
        params = {
            "symbol": symbol
        }
        response = self.__base_request("parsed", params=params)
        return QuoteData(response)

    def raw(self, symbol):
        """
        The raw data endpoint provides access to raw data metrics for the monitored social platforms
        :param symbol: String specifying the ticker or symbol of the stock to request data for
        :return: returns a QuoteData object
        """
        params = {
            "symbol": symbol
        }
        response = self.__base_request("raw", params=params)
        return QuoteData(response)

    def quote(self, symbol, enrich=False):
        """
        The quote data endpoint provides access to all realtime data about stocks along with further data if requested
        :param symbol: String specifying the ticker or symbol of the stock to request data for
        :param enrich: Set this boolean to true to request enriched data
        :return: returns a QuoteData object
        """
        params = {
            "symbol": symbol,
            "enrich": enrich
        }
        response = self.__base_request("quote", params=params)
        return QuoteData(response)

    def sort(self, metric, limit):
        """
        The sort data endpoint provides access to ordered rankings of stocks across core metrics
        :param metric: The metric by which to sort the stocks.
        This can be any of the metrics returned by a quote request.
        :param limit: The maximum number of stocks to return
        :return: returns a list of TickerData objects
        """
        params = {
            "metric": metric,
            "limit": limit
        }
        response = self.__base_request("sort", params=params)
        return [TickerData(dp) for dp in response.get("results")]

    def historical(self, symbol, metric, start, end):
        """
        The historical data endpoint provides access to historical data for stocks
        :param symbol: The stock to look up historical data for
        :param metric: The metric for which to return data.
        This can be any of the metrics returned by a quote request.
        :param start: string or int Unix epoch timestamp in seconds specifying start of date range
        :param end: string or int Unix epoch timestamp in seconds specifying end of date range
        :return: a dict with timestamp -> data entry mappings
        """
        params = {
            "symbol": symbol,
            "metric": metric,
            "start": start,
            "end": end
        }
        response = self.__base_request("historical", params=params)
        return {dp.get("timestamp"): dp.get("data") for dp in response.get("results")}

    def bulk(self, symbols, enrich=False):
        """
        Get quote data for several stocks simultaneously
        :param symbols: iterable of stocks to get quote data for
        :param enrich: boolean whether to get enriched data
        :return: a list of TickerData objects
        """
        params = {
            "symbols": ",".join(symbols),
            "enrich": enrich
        }
        response = self.__base_request("bulk", params=params)
        return [TickerData(result) for result in response.get("results")]
    
    def all(self, enrich=False):
        """
        Get all data for all stocks simultaneously. 
        Note that this call runs on the main thread and can take up to a minute to execute.
        :param enrich: boolean whether to fetch enriched data
        :return: a list of TickerData objects
        """
        params = {
            "enrich": enrich
        }
        response = self.__base_request("all", params=params)
        return [TickerData(result) for result in response.get("results")]

    def supported(self, symbol):
        """
        Query whether SentimentInvestor has data for a specified stock
        :param symbol: The stock ticker symbol to query
        :return: boolean whether supported or not
        """
        return self.__base_request("supported", params={"symbol": symbol}).get("result")

    def all_stocks(self):
        """
        Get a list of all stocks for which Sentiment gather data
        :return: iterable list of stock symbols
        """
        return self.__base_request("all-stocks").get("results")


class TickerData:
    """
    Specifies a basic data item for a specific ticker
    Do not try to initialise one yourself.
    """

    def __init__(self, json):
        # for every metric returned in the json set it as an attribute for this object
        for k, v in json.items():
            # do not create a results parameter if present as this is handled by derived classes separately
            if k == "results":
                continue
            setattr(self, k, v)

    def __str__(self):
        return str({k: self.__getattribute__(k) for k in dir(self) if not k.startswith("__")})


class QuoteData(TickerData):
    """
    For a list of available metrics, use dir(object)
    Returned by quote, do not try to initialise one yourself.
    """

    def __init__(self, json):
        super().__init__(json)
        for k, v in json.get("results").items():
            setattr(self, k, v)
