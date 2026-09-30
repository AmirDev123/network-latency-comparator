# network-latency-comparator

Compare TCP latency to multiple hosts simultaneously, rank them by average response time, and display detailed statistics — no root/ICMP required.

## Features

- TCP-based latency probing (works without elevated privileges)
- Multiple probes per host with min/max/avg/stddev
- Packet loss percentage per host
- Ranking table sorted by fastest average RTT
- Accepts hosts inline or from a file

## Installation

```bash
pip install -r requirements.txt   # only pytest for tests
```

## Usage

```bash
# Compare multiple hosts
python main.py google.com cloudflare.com 1.1.1.1

# Use port 80 instead of 443, send 10 probes
python main.py google.com cloudflare.com --port 80 --count 10

# Read hosts from a file (one per line)
python main.py --hosts-file hosts.txt

# Custom host:port pairs
python main.py google.com:443 github.com:443 8.8.8.8:53
```

## Example output

```
Pinging 3 host(s), 5 probe(s) each...

  google.com:443  →  12.34ms
  google.com:443  →  11.98ms
  ...

Rank  Host                               Avg ms    Min ms    Max ms    Loss       ±
──────────────────────────────────────────────────────────────────────────────────
1     cloudflare.com:443                  10.21      9.87     11.02    0.0%    0.42ms
2     1.1.1.1:443                         10.88     10.21     11.94    0.0%    0.63ms
3     google.com:443                      12.45     11.98     13.20    0.0%    0.51ms

  Fastest: cloudflare.com:443  (10.21 ms avg)
```

## Running tests

```bash
pytest tests/
```

## Project structure

```
network-latency-comparator/
├── comparator/
│   ├── pinger.py    # TCP ping implementation
│   ├── analyzer.py  # Statistics (min/max/avg/stddev/loss)
│   └── reporter.py  # Table formatting
├── tests/
│   └── test_comparator.py
├── main.py
└── requirements.txt
```
