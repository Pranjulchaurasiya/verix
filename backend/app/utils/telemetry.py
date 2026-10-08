"""Telemetry and operational metrics tracker for Verix."""

import time
from datetime import datetime, timezone
import threading
from typing import Dict, Any

class TelemetryTracker:
    def __init__(self):
        self._lock = threading.RLock()
        self.start_time = time.time()
        self.total_requests = 0
        self.whitelist_bypasses = 0
        self.insufficient_data_scans = 0
        self.serpapi_calls_attempted = 0
        self.serpapi_calls_succeeded = 0
        self.serpapi_calls_failed = 0
        self.serpapi_credits_saved = 0
        self.fail_closed_stale_served = 0
        self.groq_calls_attempted = 0
        self.groq_calls_succeeded = 0
        self.trust_score_sum = 0
        self.trust_score_count = 0
        self.last_serpapi_failure_time = None
        self.last_serpapi_error = None

    def record_serpapi_cache_hit(self):
        with self._lock:
            self.serpapi_credits_saved += 1

    def record_request(self):
        with self._lock:
            self.total_requests += 1

    def record_whitelist_bypass(self):
        with self._lock:
            self.whitelist_bypasses += 1

    def record_insufficient_data(self):
        with self._lock:
            self.insufficient_data_scans += 1

    def record_serpapi_attempt(self):
        with self._lock:
            self.serpapi_calls_attempted += 1

    def record_serpapi_success(self):
        with self._lock:
            self.serpapi_calls_succeeded += 1

    def record_serpapi_failure(self, error_msg: str = ""):
        with self._lock:
            self.serpapi_calls_failed += 1
            self.last_serpapi_failure_time = datetime.now(timezone.utc).isoformat()
            self.last_serpapi_error = error_msg

    def record_fail_closed_stale(self):
        with self._lock:
            self.fail_closed_stale_served += 1

    def record_trust_score(self, score: int):
        with self._lock:
            if score is not None:
                self.trust_score_sum += score
                self.trust_score_count += 1

    def get_uptime_seconds(self) -> float:
        return round(time.time() - self.start_time, 2)

    def get_serpapi_success_rate(self) -> float:
        with self._lock:
            if self.serpapi_calls_attempted == 0:
                return 100.0
            return round((self.serpapi_calls_succeeded / self.serpapi_calls_attempted) * 100, 2)

    def get_average_trust_score(self) -> float:
        with self._lock:
            if self.trust_score_count == 0:
                return None
            return round(self.trust_score_sum / self.trust_score_count, 1)

    def snapshot(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "uptime_seconds": self.get_uptime_seconds(),
                "total_requests": self.total_requests,
                "whitelist_bypasses": self.whitelist_bypasses,
                "insufficient_data_scans": self.insufficient_data_scans,
                "serpapi_calls_attempted": self.serpapi_calls_attempted,
                "serpapi_calls_succeeded": self.serpapi_calls_succeeded,
                "serpapi_calls_failed": self.serpapi_calls_failed,
                "serpapi_credits_saved": self.serpapi_credits_saved,
                "fail_closed_stale_served": self.fail_closed_stale_served,
                "serpapi_success_rate": self.get_serpapi_success_rate(),
                "average_trust_score": self.get_average_trust_score(),
                "last_serpapi_failure_time": self.last_serpapi_failure_time,
                "last_serpapi_error": self.last_serpapi_error
            }

telemetry = TelemetryTracker()
