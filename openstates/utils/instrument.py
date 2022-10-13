import logging
import os
import pyjwt
import requests


class Instrumentation(object):
    def __init__(self):
        self.logger = logging.getLogger("openstates.instrument")
        self.token = self._jwt_token()
        self.batch = list()
        self.endpoint = os.environ.get("STATS_ENDPOINT", None)
        self.default_tags = list()
        self.batch_size = 50

    def _jwt_token(self):
        secret = os.environ["JWT_SECRET"]
        return jwt.encode({"id": "openstates"}, secret, algorithm="HS256")

    def send_stats(self, force=False):
        if not self.endpoint:
            self.logger.warning("No stats endpoint defined, not emitting stats")
            return
        batch_len = len(self.batch)
        if (force and batch_len > 0) or batch_len > self.batch_size:
            headers = {"X-JWT-Token": self.token, "Content-Type": "application/json"}
            requests.post(f"{self.endpoint}/batch", json=self.batch, headers=headers)
            self.batch = list()

    def _process_metric(self, metric_type: str, metric: str, tags: list, value: float, sample_rate: float=0):
        """
        Ensure consistent formatting of data objects to add to batch for sending

        returns: None
        """
        tags.extend(self.default_tags)
        tagstr = ",".join([f"{k}={v}" for k, v in list(set(tags))])
        data = {"value": value, "metric": metric, "metric_type": metric_type, "tags": tags}
        # don't add a useless key if we don't need it
        if sample_rate:
            data["sampleRate"] = sample_rate
        self.batch.append(data)
        self.send_stats()

    """
    Wrapper scripts for easier sending
    """

    def send_counter(self, metric: str, tags: list, value: float, sample_rate: float=0):
        self._process_metric("counter", metric, tags, value, sample_rate)

    def send_gauge(self, metric: str, tags: list, value: float):
        self._process_metric("counter", metric, tags, value)

    def send_timing(self, metric: str, tags: list, value: float, sample_rate: float=0):
        self._process_metric("counter", metric, tags, value)

    def send_set(self, metric: str, tags: list, value: float):
        self._process_metric("counter", metric, tags, value)
