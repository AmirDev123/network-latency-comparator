#!/usr/bin/env python3
"""
Network Latency Comparator — measure and compare TCP latency to multiple hosts.

Usage:
    python main.py google.com cloudflare.com 1.1.1.1
    python main.py google.com cloudflare.com --port 80 --count 10
    python main.py --hosts-file hosts.txt
"""
import argparse
import sys

from comparator.analyzer import analyze, rank_by_avg
from comparator.pinger import multi_ping
from comparator.reporter import print_progress, print_report


def run(hosts: list[tuple[str, int]], count: int, timeout: float) -> None:
    all_stats = []
    print(f"\nPinging {len(hosts)} host(s), {count} probe(s) each...\n")

    for host, port in hosts:
        results = []
        for r in multi_ping(host, port, count, timeout):
            print_progress(host, port, r)
            results.append(r)
        all_stats.append(analyze(host, port, results))
        print()

    ranked = rank_by_avg(all_stats)
    print_report(ranked)


def parse_host(s: str, default_port: int) -> tuple[str, int]:
    if ":" in s and not s.startswith("["):
        parts = s.rsplit(":", 1)
        try:
            return parts[0], int(parts[1])
        except ValueError:
            pass
    return s, default_port


def main():
    parser = argparse.ArgumentParser(description="Network Latency Comparator")
    parser.add_argument("hosts", nargs="*", help="Hosts to compare (host or host:port)")
    parser.add_argument("--port", type=int, default=443, help="Default TCP port (default: 443)")
    parser.add_argument("--count", type=int, default=5, help="Probes per host")
    parser.add_argument("--timeout", type=float, default=5.0, help="Timeout per probe (seconds)")
    parser.add_argument("--hosts-file", help="File with one host per line")
    args = parser.parse_args()

    host_strs: list[str] = list(args.hosts)
    if args.hosts_file:
        try:
            with open(args.hosts_file) as f:
                host_strs += [line.strip() for line in f if line.strip() and not line.startswith("#")]
        except OSError as exc:
            sys.exit(f"Cannot read hosts file: {exc}")

    if not host_strs:
        parser.print_help()
        sys.exit(1)

    hosts = [parse_host(h, args.port) for h in host_strs]
    run(hosts, args.count, args.timeout)


if __name__ == "__main__":
    main()
