"""Format and print latency comparison reports."""
from .analyzer import HostStats


def print_report(stats: list[HostStats]) -> None:
    if not stats:
        print("No results to report.")
        return

    print(f"\n{'Rank':<5} {'Host':<35} {'Avg ms':>8}  {'Min ms':>8}  {'Max ms':>8}  {'Loss':>6}  {'±':>7}")
    print("─" * 82)

    for i, s in enumerate(stats, 1):
        if s.avg_ms is not None:
            print(
                f"{i:<5} {s.label:<35} {s.avg_ms:>8.2f}  "
                f"{s.min_ms:>8.2f}  {s.max_ms:>8.2f}  "
                f"{s.packet_loss_pct:>5.1f}%  {s.stddev_ms:>6.2f}ms"
            )
        else:
            print(f"{i:<5} {s.label:<35} {'UNREACHABLE':>8}  {'—':>8}  {'—':>8}  100.0%")

    best = stats[0]
    if best.avg_ms is not None:
        print(f"\n  Fastest: {best.label}  ({best.avg_ms:.2f} ms avg)\n")


def print_progress(host: str, port: int, result) -> None:
    status = f"{result.rtt_ms:.2f}ms" if result.success else f"FAILED ({result.error})"
    print(f"  {host}:{port}  →  {status}")
