import requests

class Sentipy():
  base_url = r"https://sentimentinvestor.com/api/v3/"

  def __init__(self, token=None, key=None):
    if token is None or key is None:
      raise ValueError("Please provide a token and key - these can be obtained at https://sentimentinvestor.com/developer/home")
    self.token = token
    self.key = key

  def base_request(self, endpoint, params={}):
    url = self.base_url + endpoint
    params["token"] = self.token
    params["key"] = self.key
    response = requests.get(url, params)
    if response.content.decode("utf-8")  == 'invalid_parameter' or response.content.decode("utf-8")  == 'incorrect_key':
      raise ValueError("Incorrect key or token")
    elif response.ok:
      return response.json()
    else:
      raise Exception("No response from the server - check your Wifi or try again in 15 minutes")

  def quote(self, symbol):
    params = {
      "symbol": symbol
    }
    response = self.base_request("quote", params=params)
    return QuoteData(response)

  def sort(self, metric, limit):
    params = {
      "metric": metric,
      "limit": limit
    }
    response = self.base_request("sort", params=params)
    return SortData(response)

  def historical(self, symbol, metric):
    params = {
      "symbol": symbol,
      "metric": metric
    }
    response = self.base_request("historical", params=params)
    return HistoricalData(response)

class BasicTicker():
  def __init__(self, json):
    self.ticker = json.get("ticker")
    self.AHI = json.get("AHI")
    self.sentiment = json.get("sentiment")
    self.RHI = json.get("RHI")
    self.SGP = json.get("SGP")

class QuoteData(BasicTicker):
  def __init__(self, json):
    super().__init__(json)
    self.last_update = json.get("last_update")
    self.reddit_comment_mentions = json.get("reddit_comment_mentions")
    self.reddit_comment_sentiment = json.get("reddit_comment_sentiment")
    self.reddit_post_mentions = json.get("reddit_post_mentions")
    self.reddit_post_sentiment = json.get("reddit_post_sentiment")
    self.tweet_mentions = json.get("tweet_mentions")
    self.tweet_sentiment = json.get("tweet_sentiment")
    self.yahoo_finance_mentions = json.get("yahoo_finance_mentions")
    self.yahoo_finance_sentiment = json.get("yahoo_finance_mentions")
    self.stocktwits_mentions = json.get("stocktwits_mentions")
    self.stocktwits_sentiment = json.get("stocktwits_sentiment")

class HistoricalData():
  def __init__(self, json):
    self.history = [HistoricalDatapoint(dp) for dp in json]
    self.sort()

  def sort(self, direction="asc"):
    if direction=="asc":
      self.history.sort(key=lambda x: x.timestamp)
    else:
      self.history.sort(reverse=True, key=lambda x: x.timestamp)

class HistoricalDatapoint():
  def __init__(self, datapoint):
    self.data = datapoint.get("data")
    self.timestamp = datapoint.get("timestamp")

class SortData():
  def __init__(self, json):
    self.sort = [BasicTicker(dp) for dp in json]


