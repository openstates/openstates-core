import logging
import os
import jwt
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from typing import List, Dict


class Instrumentation(object):
    stat_emission_types = ["STATSD", "PROMETHEUS"]

    def __init__(self) -> None:
        self.enabled = os.environ.get("STATS_ENABLED", False)
        self.logger = logging.getLogger("openstates")
        token: str = self._jwt_token()
        self.batch: List[Dict] = list()
        self.prefix: str = os.environ.get("STATS_PREFIX", "")
        self.endpoint: str = os.environ.get("STATS_ENDPOINT", "")
        self.send_type: str = os.environ.get("STATS_TYPE", "")
        if self.send_type not in self.stat_emission_types:
            raise Exception(f"Invalid stats type {self.send_type}!")
        if self.send_type == "STATSD":
            headers = {"X-JWT-Token": token, "Content-Type": "application/json"}
        else:
            headers = {"Content-Type": "text/plain"}
            token = os.environ.get("PROMETHEUS_AUTH_TOKEN", "")
            if token:
                headers["Authorization"] = f"Bearer {token}"
        self.default_tags: List = list()
        self.batch_size = 50
        retries = 3
        retry = Retry(
            total=retries,
            read=retries,
            connect=retries,
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
        secret = os.environ["JWT_SECRET"]
        return jwt.encode({"id": "openstates"}, secret, algorithm="HS256")

    def _send_statsd(self) -> None:
        """
        Very simple wrapper currently.
        We may want to change this, so keep it a function
        """
        self._stat_client.post(f"{self.endpoint}/batch", json=self.batch)

    def _send_prom_push(self) -> None:
        """
        convert stats into separate Prometheus-style blocks
        to post to a push gateway
        """
        for metric in self.batch:
            path = "/".join(f"{k}/{v}" for k, v in metric["tags"].items())
            url = f"{self.endpoint}/metrics/job/scrapers/{path}"
            metric_name = metric["metric"]
            mtype = metric["metric_type"]
            description = metric["description"]
            value = metric["value"]
            data = f"# TYPE {metric_name} {mtype}\n"
            data += f"# HELP {metric_name} {description}\n"
            data += f"{metric_name} {value}\n"
            # url can change per stat, so post each individually
            try:
                self._stat_client.post(url, data=data)
            except Exception as e:
                self.logger.warning(
                    f"Failed to push scrape stats to {self.endpoint} => {e}"
                )

    def send_stats(self, force: bool = False) -> None:
        """
        Wrapper for sending stats, regardless of chosen output type

        Needs to be broken out from _process_metric to have a
        "write at shutdown" function
        """
        if not self.endpoint or not self.enabled:
            self.logger.warning("No stats endpoint defined, not emitting stats")
            return
        batch_len = len(self.batch)
        if (force and batch_len > 0) or batch_len > self.batch_size:
            if self.send_type == "STATSD":
                self._send_statsd()
            elif self.send_type == "PROMETHEUS":
                self._send_prom_push()
        self.batch = list()

    def _process_metric(
        self,
        metric_type: str,
        metric: str,
        tags: list,
        value: float,
        sample_rate: float = 0,
        description: str = "",
    ) -> None:
        """
        Ensure consistent formatting of data objects to add to batch for sending

        returns: None
        """
        tags.extend(self.default_tags)
        tagstr = ",".join([f"{k}={v}" for k, v in list(set(tags))])
        data = {
            "value": value,
            "metric": f"{self.prefix}{metric}",
            "metric_type": metric_type,
            "tags": tagstr,
        }
        # don't add a useless key if we don't need it
        if data["metric_type"] == "count" and self.send_type == "PROMETHEUS":
            data["metric_type"] == "counter"
        if self.send_type == "STATSD":
            data["sampleRate"] = sample_rate
        if self.send_type == "PROMETHEUS":
            data["description"] = description
        self.logger.debug(f"Adding metric {data}")
        self.batch.append(data)
        self.send_stats()

    """
    Wrapper scripts for easier sending
    """

    def send_counter(
        self, metric: str, value: float, tags: list = [], sample_rate: float = 0
    ) -> None:
        if not self.enabled:
            return
        self._process_metric("count", metric, tags, value, sample_rate)

    def send_gauge(self, metric: str, value: float, tags: list = []) -> None:
        if not self.enabled:
            return
        self._process_metric("gauge", metric, tags, value)

    def send_timing(
        self,
        metric: str,
        value: float,
        tags: list = [],
        sample_rate: float = 0,
        description: str = "",
    ) -> None:
        if not self.enabled:
            return
        self._process_metric("timing", metric, tags, value, sample_rate, description)

    def send_set(self, metric: str, value: float, tags: list = []) -> None:
        if not self.enabled:
            return
        self._process_metric("set", metric, tags, value)
