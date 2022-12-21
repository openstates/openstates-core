from ast import literal_eval
import datetime
import jwt
import logging
import logging.config
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import time
from typing import List, Dict

from .. import settings


class MetricTypes:
    CounterType = "count"
    GaugeType = "gauge"
    TimingType = "timing"
    SetType = "set"


class Instrumentation(object):
    def __init__(self) -> None:
        """
        We're currently leveraging https://github.com/civic-eagle/statsd-http-proxy
        to have an easy to reason about stats aggregation tool
        on the other end of an internet connection

        Essentially statsd-style metrics, we can rely on the aggregator
        to continually emit these stats so we get useful stats for monitoring/reporting
        """
        logging.config.dictConfig(settings.LOGGING)
        self.logger = logging.getLogger("openstates.stats")
        # use a literal_eval to properly turn a string into a bool (literal_eval 'cause it's safer than stdlib eval)
        self.enabled = literal_eval(os.environ.get("STATS_ENABLED", "False"))
        if not self.enabled:
            self.logger.debug("Stat emission is not enabled.")
            return
        token: str = self._jwt_token()
        self._batch: List[Dict] = list()
        self.prefix: str = os.environ.get("STATS_PREFIX", "openstates_")
        self.endpoint: str = os.environ.get("STATS_ENDPOINT", "")
        if self.endpoint.endswith("/"):
            self.endpoint = self.endpoint.strip("/")
        stats_retries: int = int(os.environ.get("STATS_RETRIES", 3))
        self.batch_size: int = int(os.environ.get("STATS_BATCH_SIZE", 50))
        self.default_tags: Dict = dict()
        headers = {"Content-Type": "application/json"}
        if token:
            headers["X-JWT-Token"] = token
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
        self.logger.debug(
            f"Stats emission to {self.endpoint} configured with batch size: {self.batch_size}"
        )

    def _jwt_token(self) -> str:
        """
        Generate a JWT token from a consistent environment secret
        Return empty strings when generation isn't possible.
        """
        if not self.enabled:
            return ""
        secret = os.environ.get("STATS_JWT_SECRET", "")
        if not secret:
            return ""
        """
        We need a pretty long expiration time for runs that take 12+ hours.
        So we add the `exp` setting as 36 hours out. Should give us plenty of time.
        """
        return jwt.encode(
            {
                "id": "openstates",
                "exp": datetime.datetime.now(tz=datetime.timezone.utc)
                + datetime.timedelta(hours=36),
            },
            secret,
            algorithm="HS256",
        )

    def _send_stats(self, force: bool = False) -> None:
        """
        Needs to be broken out from _process_metric to have a
        "write at shutdown" function (force=True)
        Even with force=True, we should only write when there is data
        to write. Otherwise, just skip things.
        """
        batch_len = len(self._batch)
        if (force and batch_len > 0) or batch_len > self.batch_size:
            if not self.enabled:
                self.logger.debug("Stats diasbled. Skipping send")
                return
            if not self.endpoint:
                self.logger.debug("No stats endpoint defined. Not emitting stats")
                return
            self.logger.debug(f"Sending stats batch: {self._batch}")
            try:
                self._stat_client.post(f"{self.endpoint}/batch", json=self._batch)
                self._batch = list()
            except Exception as e:
                self.logger.warning(
                    f"Failed to write {len(self._batch)} stats to {self.endpoint} :: {e}"
                )

    def _process_metric(
        self,
        metric_type: str,
        metric: str,
        tags: dict,
        value: float,
        sample_rate: float = 0,
    ) -> None:
        """
        Ensure consistent formatting of data objects to add to batch for sending
        """
        if not self.enabled:
            return
        # apply defaults only if not overridden
        for k, v in self.default_tags.items():
            if k not in tags:
                tags[k] = v

        """
        Statsd http proxy specific formatting
        """
        # list(set()) to remove duplicates
        tagstr = ",".join(list(set([f"{k}={v}" for k, v in tags.items()])))
        data = {
            "value": value,
            "metric": f"{self.prefix}{metric}",
            "metric_type": metric_type,
            "tags": tagstr,
        }
        if sample_rate:
            data["sampleRate"] = sample_rate
        # End specific formatting

        self._batch.append(data)
        """
        we attempt to send (without forcing) after
        adding each stat to make sure we emit
        batches as quickly as we can, without
        overloading the write endpoint with tiny writes
        """
        self._send_stats()

    """
    Wrapper scripts for easier sending

    Using these functions would look like:

    from utils.instrument import Instrumentation
    stats = Instrumentation()
    stats.send_gauge("objects_scraped", 10, [{"jurisdiction": "ca"}])
    stats.close()
    """

    def close(self) -> None:
        """
        "Shut down" our instrumentation connection
        Currently just forces any batched stats out
        Keep as a wrapper script for later extensibility
        """
        if not self.enabled:
            return
        self._send_stats(force=True)

    def send_last_run(self, metric: str, tags: dict = {}) -> None:
        """
        Set a gauge with a current timestamp
        Emulates a "last run time" feature simply
        """
        if not self.enabled:
            return
        self._process_metric(MetricTypes.GaugeType, metric, tags, int(time.time()))

    def send_counter(
        self,
        metric: str,
        value: float,
        tags: dict = {},
        sample_rate: float = 0,
    ) -> None:
        if not self.enabled:
            return
        self._process_metric(MetricTypes.CounterType, metric, tags, value, sample_rate)

    def send_gauge(self, metric: str, value: float, tags: dict = {}) -> None:
        """
        Gauges aren't calculated, so don't require a sample rate
        """
        if not self.enabled:
            return
        self._process_metric(MetricTypes.GaugeType, metric, tags, value)

    def send_timing(
        self,
        metric: str,
        value: float,
        tags: dict = {},
        sample_rate: float = 0,
    ) -> None:
        if not self.enabled:
            return
        self._process_metric(MetricTypes.TimingType, metric, tags, value)

    def send_set(self, metric: str, value: float, tags: dict = {}) -> None:
        """
        Sets (naturally) aren't calculated, so don't require a sample rate
        """
        if not self.enabled:
            return
        self._process_metric(MetricTypes.SetType, metric, tags, value)
