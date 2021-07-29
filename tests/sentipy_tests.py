import os
import unittest

# vcrpy is untyped
# Therefore, ignore all vcr decorators
import vcr  # type: ignore[import]
from beartype import beartype

from sentipy._typing_imports import ListType
from sentipy.sentipy import Sentipy


class SentipyTestCase(unittest.TestCase):
    sentipy: Sentipy

    @beartype
    def setUp(self) -> None:

        sentipy_key = os.getenv("API_SENTIMENTINVESTOR_KEY")
        sentipy_token = os.getenv("API_SENTIMENTINVESTOR_TOKEN")

        # Makes the sentipy args str rather than Optional[str]
        if sentipy_key is None or sentipy_token is None:
            self.fail(
                "API_SENTIMENTINVESTOR_KEY or API_SENTIMENTINVESTOR_TOKEN is not set"
            )

        self.sentipy = Sentipy(
            key=sentipy_key,
            token=sentipy_token,
        )

    @beartype
    def assertHasAttr(self, object: object, attr: str) -> None:
        self.assertTrue(
            hasattr(object, attr), f"{object!r} does not have attribute {attr!r}"
        )

    @beartype
    def assertHasAttrs(self, object: object, attrs: ListType[str]) -> None:
        for attr in attrs:
            self.assertHasAttr(object, attr)

    @beartype
    def check_basics(self, data: object) -> None:
        # The data will have a success attribute
        self.assertTrue(data.success)  # type: ignore[attr-defined]
        self.assertHasAttr(data, "symbol")

    @vcr.use_cassette("vcr_cassettes/parsed.yml")  # type: ignore[misc]
    @beartype
    def test_parsed(self) -> None:
        data = self.sentipy.parsed("AAPL")
        self.check_basics(data)
        self.assertHasAttrs(data, ["sentiment", "AHI", "RHI", "SGP"])

    @vcr.use_cassette("vcr_cassettes/raw.yml")  # type: ignore[misc]
    @beartype
    def test_raw(self) -> None:
        data = self.sentipy.raw("AAPL")
        self.check_basics(data)
        self.assertHasAttrs(
            data,
            [
                "reddit_comment_mentions",
                "reddit_comment_sentiment",
                "reddit_post_mentions",
                "reddit_post_sentiment",
                "tweet_mentions",
                "tweet_sentiment",
                "stocktwits_post_mentions",
                "stocktwits_post_sentiment",
                "yahoo_finance_comment_mentions",
                "yahoo_finance_comment_sentiment",
            ],
        )

    @vcr.use_cassette("vcr_cassettes/quote.yml")  # type: ignore[misc]
    def test_quote(self) -> None:
        data = self.sentipy.quote("AAPL")
        self.check_basics(data)
        self.assertHasAttrs(
            data,
            [
                "sentiment",
                "AHI",
                "RHI",
                "SGP",
                "reddit_comment_mentions",
                "reddit_comment_sentiment",
                "reddit_post_mentions",
                "reddit_post_sentiment",
                "tweet_mentions",
                "tweet_sentiment",
                "stocktwits_post_mentions",
                "stocktwits_post_sentiment",
                "yahoo_finance_comment_mentions",
                "yahoo_finance_comment_sentiment",
            ],
        )

    @vcr.use_cassette("vcr_cassettes/bulk.yml")  # type: ignore[misc]
    @beartype
    def test_bulk(self) -> None:
        data = self.sentipy.bulk(["AAPL", "TSLA", "PYPL"])
        self.assertEqual(len(data), 3)
        for stock in data:
            self.assertHasAttrs(
                stock,
                [
                    "sentiment",
                    "AHI",
                    "RHI",
                    "SGP",
                    "reddit_comment_mentions",
                    "reddit_comment_sentiment",
                    "reddit_post_mentions",
                    "reddit_post_sentiment",
                    "tweet_mentions",
                    "tweet_sentiment",
                    "stocktwits_post_mentions",
                    "stocktwits_post_sentiment",
                    "yahoo_finance_comment_mentions",
                    "yahoo_finance_comment_sentiment",
                ],
            )


if __name__ == "__main__":
    unittest.main()
