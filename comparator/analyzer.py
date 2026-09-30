"""Compute statistics over a list of PingResults."""
import statistics
from dataclasses import dataclass

from .pinger import PingResult


@dataclass
class HostStats:
    host: str
    port: int
    sent: int
    received: int
    min_ms: float | None
    max_ms: float | None
    avg_ms: float | None
    stddev_ms: float | None
    packet_loss_pct: float

    @property
    def label(self) -> str:
        return f"{self.host}:{self.port}"


def analyze(host: str, port: int, results: list[PingResult]) -> HostStats:
    sent = len(results)
    rtts = [r.rtt_ms for r in results if r.success]
    received = len(rtts)
    loss = round((1 - received / sent) * 100, 1) if sent else 0.0

    if rtts:
        return HostStats(
            host=host, port=port, sent=sent, received=received,
            min_ms=round(min(rtts), 3),
            max_ms=round(max(rtts), 3),
            avg_ms=round(statistics.mean(rtts), 3),
            stddev_ms=round(statistics.stdev(rtts), 3) if len(rtts) > 1 else 0.0,
            packet_loss_pct=loss,
        )
    return HostStats(
        host=host, port=port, sent=sent, received=0,
        min_ms=None, max_ms=None, avg_ms=None, stddev_ms=None,
        packet_loss_pct=100.0,
    )


def rank_by_avg(stats: list[HostStats]) -> list[HostStats]:
    """Sort reachable hosts by average RTT ascending; unreachable last."""
    reachable = sorted([s for s in stats if s.avg_ms is not None], key=lambda s: s.avg_ms)
    unreachable = [s for s in stats if s.avg_ms is None]
    return reachable + unreachable
