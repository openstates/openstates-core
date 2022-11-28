import logging
import os
import jwt
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import time
from typing import List, Dict


class Instrumentation(object):

    def __init__(self) -> None:
        """
        We're currently leveraging https://github.com/civic-eagle/statsd-http-proxy
        to have an easy to reason about stats aggregation tool
        on the other end of an internet connection

        Essentially statsd-style metrics, we can rely on the aggregator
        to continually emit these stats so we get useful stats for monitoring/reporting
        """
        self.enabled = os.environ.get("STATS_ENABLED", False)
        self.logger = logging.getLogger("openstates")
        token: str = self._jwt_token()
        self._batch: List[Dict] = list()
        self.prefix: str = os.environ.get("STATS_PREFIX", "")
        self.endpoint: str = os.environ.get("STATS_ENDPOINT", "")
        stats_retries: int = int(os.environ.get("STATS_RETRIES", 3))
        self.batch_size: str = int(os.environ.get("STATS_BATCH_SIZE", 50))
        self.default_tags: List = list()
        headers = {"X-JWT-Token": token, "Content-Type": "application/json"}
        retry = Retry(
            total=stats_retries,
            read=stats_retries,
            connect=stats_retries,
            backoff_factor=0.3,
            status_forcelist=(500, 502, 503, 504, 429, 104),
        )
        adapter = HTTPAdapter(max_retries=retry)
        self._stat_client = requests.Session()
        self._stat_client.headers.update(headers)
        # only mount https endpoint if we need it
        if self.endpoint.startswith("https"):
            self._stat_client.mount("https://", adapter)
        else:
            self._stat_client.mount("http://", adapter)

    def _jwt_token(self) -> str:
        """
        Only generate a token at startup. Much faster.
        """
        if not self.enabled:
            return ""
        secret = os.environ["STATS_JWT_SECRET"]
        return jwt.encode({"id": "openstates"}, secret, algorithm="HS256")

    def send_stats(self, force: bool = False) -> None:
        """
        Needs to be broken out from _process_metric to have a
        "write at shutdown" function (force=True)
        """
        if not self.endpoint:
            self.logger.warning("No stats endpoint defined, not emitting stats")
            return
        if not self.enabled:
            self.logger.warning("Stats disabled. Send skipped.")
        batch_len = len(self._batch)
        if (force and batch_len > 0) or batch_len > self.batch_size:
            self._stat_client.post(f"{self.endpoint}/batch", json=self._batch)
        self._batch = list()

    def _process_metric(
        self,
        metric_type: str,
        metric: str,
        tags: list,
        value: float,
        sample_rate: float = 0,
    ) -> None:
        """
        Ensure consistent formatting of data objects to add to batch for sending

        returns: None
        """
        if not self.enabled:
            self.logger.warning("Stats disabled. Processing skipped.")
            return
        tags.extend(self.default_tags)
        # list(set()) to remove duplicates
        tagstr = ",".join([f"{k}={v}" for k, v in list(set(tags))])
        data = {
            "value": value,
            "metric": f"{self.prefix}{metric}",
            "metric_type": metric_type,
            "tags": tagstr,
        }
        if sample_rate:
            data["sampleRate"] = sample_rate

        self.logger.debug(f"Adding metric {data}")
        self._batch.append(data)
        """
        we attempt to send (without forcing) after
        adding each stat to make sure we emit
        batches as quickly as we can
        """
        self.send_stats()

    """
    Wrapper scripts for easier sending

    Using these functions would look like:

    from utils.instrument import Instrumentation
    stats = Instrumentation()
    stats.send_gauge("objects_scraped", 10, [{"jurisdiction": "ca"}])
    """

    def send_last_run(self, metric: str, tags: list = []) -> None:
        """
        Set a gauge with a current timestamp
        Emulates a "last run time" feature simply
        """
        self._process_metric("gauge", metric, tags, time.time())

    def send_counter(
        self, metric: str, value: float, tags: list = [], sample_rate: float = 0,
    ) -> None:
        self._process_metric("count", metric, tags, value, sample_rate)

    def send_gauge(self, metric: str, value: float, tags: list = []) -> None:
        self._process_metric("gauge", metric, tags, value)

    def send_timing(
        self,
        metric: str,
        value: float,
        tags: list = [],
        sample_rate: float = 0,
    ) -> None:
        self._process_metric("timing", metric, tags, value)

    def send_set(self, metric: str, value: float, tags: list = []) -> None:
        self._process_metric("set", metric, tags, value)
