import os
import unittest

import vcr

from sentipy.sentipy import Sentipy


class SentipyTestCase(unittest.TestCase):
    sentipy: Sentipy

    def setUp(self) -> None:
        self.sentipy = Sentipy(
            key=os.getenv('API_SENTIMENTINVESTOR_KEY'),
            token=os.getenv('API_SENTIMENTINVESTOR_TOKEN')
        )

    def assertHasAttr(self, object: object, attr: str):
        self.assertTrue(hasattr(object, attr), f"{object!r} does not have attribute {attr!r}")

    def assertHasAttrs(self, object: object, attrs: list[str]):
        for attr in attrs:
            self.assertHasAttr(object, attr)

    def check_basics(self, data: object):
        self.assertTrue(data.success)
        self.assertHasAttr(data, 'symbol')

    @vcr.use_cassette('vcr_cassettes/parsed.yml')
    def test_parsed(self):
        data = self.sentipy.parsed('AAPL')
        self.check_basics(data)
        self.assertHasAttrs(data, ['sentiment', 'AHI', 'RHI', 'SGP'])

    @vcr.use_cassette('vcr_cassettes/raw.yml')
    def test_raw(self):
        data = self.sentipy.raw('AAPL')
        self.check_basics(data)
        self.assertHasAttrs(data, ['reddit_comment_mentions', 'reddit_comment_sentiment', 'reddit_post_mentions',
                                   'reddit_post_sentiment', 'tweet_mentions', 'tweet_sentiment',
                                   'stocktwits_post_mentions',
                                   'stocktwits_post_sentiment', 'yahoo_finance_comment_mentions',
                                   'yahoo_finance_comment_sentiment'])

    @vcr.use_cassette('vcr_cassettes/quote.yml')
    def test_quote(self):
        data = self.sentipy.quote('AAPL')
        self.check_basics(data)
        self.assertHasAttrs(data,
                            ['sentiment', 'AHI', 'RHI', 'SGP', 'reddit_comment_mentions', 'reddit_comment_sentiment',
                             'reddit_post_mentions', 'reddit_post_sentiment', 'tweet_mentions', 'tweet_sentiment',
                             'stocktwits_post_mentions', 'stocktwits_post_sentiment', 'yahoo_finance_comment_mentions',
                             'yahoo_finance_comment_sentiment'])

    @vcr.use_cassette('vcr_cassettes/bulk.yml')
    def test_bulk(self):
        data = self.sentipy.bulk(['AAPL', 'TSLA', 'PYPL'])
        self.assertEqual(len(data), 3)
        for stock in data:
            self.assertHasAttrs(stock,
                                ['sentiment', 'AHI', 'RHI', 'SGP', 'reddit_comment_mentions',
                                 'reddit_comment_sentiment',
                                 'reddit_post_mentions', 'reddit_post_sentiment', 'tweet_mentions', 'tweet_sentiment',
                                 'stocktwits_post_mentions', 'stocktwits_post_sentiment',
                                 'yahoo_finance_comment_mentions',
                                 'yahoo_finance_comment_sentiment']
                                )


if __name__ == '__main__':
    unittest.main()
