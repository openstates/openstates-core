from ast import literal_eval
import logging
import logging.config
import os
import time
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client.client.write.point import Point
from influxdb_client.domain.write_precision import WritePrecision
from typing import List, Dict

from .. import settings

"""
Using these functions would look like:

from utils.instrument import Instrumentation
stats = Instrumentation()
stats.write_stats([{"metric": "objects", "fields"{ "scraped": 10}, "tags": {"jurisdiction": "ca"}])
stats.close()
"""


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
        token: str = os.environ.get("OPENSTATES_STATS_AUTH_TOKEN", "")
        self._batch: List[Dict] = list()
        self.prefix: str = os.environ.get("STATS_PREFIX", "openstates_")
        self.endpoint: str = os.environ.get("STATS_ENDPOINT", "")
        self.bucket: str = os.environ.get("STATS_BUCKET", "openstates")
        if self.endpoint.endswith("/"):
            self.endpoint = self.endpoint.strip("/")
        client = InfluxDBClient(
            url=self.endpoint,
            token=token,
            org="openstates",
            enable_gzip=True,
        )
        self.write_api = client.write_api(write_options=SYNCHRONOUS)
        self.batch_size: int = int(os.environ.get("STATS_BATCH_SIZE", 50))
        self.logger.debug(
            f"Stats emission to {self.endpoint} configured with batch size: {self.batch_size}"
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
            points = []
            for m in self._batch:
                if self.prefix:
                    p = Point(f"{self.prefix}{m['metric']}")
                else:
                    p = Point(m["metric"])
                p.time(m["timestamp"], WritePrecision.S)
                """
                use list comprehensions 'cause they're technically faster than for loops
                But this is simply turning a dictionary of k=v pairs into tags/fields
                in the point object
                """
                [p.tag(t, v) for t, v in m.get("tags", {}).items()]
                [p.field(f, v) for f, v in m["fields"].items()]
                points.append(p)
            self.logger.debug(f"Sending stats batch: {self._batch}")
            try:
                self.write_api.write(self.bucket, record=points)
                self._batch = list()
            except Exception as e:
                self.logger.warning(
                    f"Failed to write {len(self._batch)} stats to {self.endpoint} :: {e}"
                )

    def write_stats(
        self,
        metrics: List[Dict],
    ) -> None:
        """
        Ensure consistent formatting of data objects to add to batch for sending
        Primarily, we'll force a timestamp on every metric in a consistent manner
        """
        if not self.enabled:
            return
        ts = int(time.time())
        for m in metrics:
            m["timestamp"] = ts
            self._batch.append(m)
        """
        we attempt to send (without forcing) after
        adding each stat to make sure we emit
        batches as quickly as we can, without
        overloading the write endpoint with tiny writes
        """
        self._send_stats()

    def close(self) -> None:
        """
        "Shut down" our instrumentation connection
        Currently just forces any batched stats out
        Keep as a wrapper script for later extensibility
        """
        if not self.enabled:
            return
        self._send_stats(force=True)
