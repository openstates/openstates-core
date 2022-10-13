import logging
import os
import jwt
import requests
from typing import List, Dict


class Instrumentation(object):
    def __init__(self) -> None:
        self.enabled = os.environ.get("STATS_ENABLED", False)
        self.logger = logging.getLogger("openstates.instrument")
        self.token = self._jwt_token()
        self.batch: List[Dict] = list()
        self.endpoint = os.environ.get("STATS_ENDPOINT", None)
        self.default_tags: List = list()
        self.batch_size = 50

    def _jwt_token(self) -> str:
        if not self.enabled:
            return ""
        secret = os.environ["JWT_SECRET"]
        return jwt.encode({"id": "openstates"}, secret, algorithm="HS256")

    def send_stats(self, force: bool = False) -> None:
        if not self.endpoint or not self.enabled:
            self.logger.warning("No stats endpoint defined, not emitting stats")
            return
        batch_len = len(self.batch)
        if (force and batch_len > 0) or batch_len > self.batch_size:
            headers = {"X-JWT-Token": self.token, "Content-Type": "application/json"}
            requests.post(f"{self.endpoint}/batch", json=self.batch, headers=headers)
            self.batch = list()

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
        tags.extend(self.default_tags)
        tagstr = ",".join([f"{k}={v}" for k, v in list(set(tags))])
        data = {
            "value": value,
            "metric": metric,
            "metric_type": metric_type,
            "tags": tagstr,
        }
        # don't add a useless key if we don't need it
        if sample_rate:
            data["sampleRate"] = sample_rate
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
        self._process_metric("counter", metric, tags, value, sample_rate)

    def send_gauge(self, metric: str, value: float, tags: list = []) -> None:
        if not self.enabled:
            return
        self._process_metric("counter", metric, tags, value)

    def send_timing(
        self, metric: str, value: float, tags: list = [], sample_rate: float = 0
    ) -> None:
        if not self.enabled:
            return
        self._process_metric("counter", metric, tags, value)

    def send_set(self, metric: str, value: float, tags: list = []) -> None:
        if not self.enabled:
            return
        self._process_metric("counter", metric, tags, value)
