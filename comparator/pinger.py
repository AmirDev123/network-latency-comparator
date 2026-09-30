"""
TCP-based latency measurement (no root required).
Connects to host:port and measures round-trip time.
"""
import socket
import time
from dataclasses import dataclass


@dataclass
class PingResult:
    host: str
    port: int
    rtt_ms: float | None
    error: str | None = None

    @property
    def success(self) -> bool:
        return self.rtt_ms is not None


def tcp_ping(host: str, port: int = 443, timeout: float = 5.0) -> PingResult:
    t0 = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            rtt = (time.perf_counter() - t0) * 1000
        return PingResult(host, port, round(rtt, 3))
    except OSError as exc:
        rtt = (time.perf_counter() - t0) * 1000
        return PingResult(host, port, None, str(exc))


def multi_ping(host: str, port: int = 443, count: int = 5, timeout: float = 5.0) -> list[PingResult]:
    return [tcp_ping(host, port, timeout) for _ in range(count)]
