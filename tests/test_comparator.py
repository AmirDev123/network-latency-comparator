import unittest
from unittest.mock import MagicMock, patch

from comparator.analyzer import HostStats, analyze, rank_by_avg
from comparator.pinger import PingResult, tcp_ping


def _ok(rtt: float) -> PingResult:
    return PingResult("host", 443, rtt)


def _fail() -> PingResult:
    return PingResult("host", 443, None, "Connection refused")


class TestPingResult(unittest.TestCase):
    def test_success_flag(self):
        self.assertTrue(_ok(10.0).success)
        self.assertFalse(_fail().success)


class TestTcpPing(unittest.TestCase):
    @patch("comparator.pinger.socket.create_connection")
    def test_successful_ping(self, mock_conn):
        mock_conn.return_value.__enter__ = MagicMock(return_value=None)
        mock_conn.return_value.__exit__ = MagicMock(return_value=False)
        result = tcp_ping("example.com", 443)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.rtt_ms)
        self.assertGreaterEqual(result.rtt_ms, 0)

    @patch("comparator.pinger.socket.create_connection")
    def test_failed_ping(self, mock_conn):
        mock_conn.side_effect = OSError("Connection refused")
        result = tcp_ping("192.0.2.1", 9999)
        self.assertFalse(result.success)
        self.assertIsNone(result.rtt_ms)
        self.assertIsNotNone(result.error)


class TestAnalyzer(unittest.TestCase):
    def test_basic_stats(self):
        results = [_ok(10.0), _ok(20.0), _ok(30.0)]
        stats = analyze("host", 443, results)
        self.assertEqual(stats.sent, 3)
        self.assertEqual(stats.received, 3)
        self.assertAlmostEqual(stats.min_ms, 10.0)
        self.assertAlmostEqual(stats.max_ms, 30.0)
        self.assertAlmostEqual(stats.avg_ms, 20.0)
        self.assertAlmostEqual(stats.packet_loss_pct, 0.0)

    def test_packet_loss(self):
        results = [_ok(10.0), _fail(), _fail(), _ok(20.0)]
        stats = analyze("host", 443, results)
        self.assertEqual(stats.received, 2)
        self.assertAlmostEqual(stats.packet_loss_pct, 50.0)

    def test_all_failed(self):
        results = [_fail(), _fail()]
        stats = analyze("host", 443, results)
        self.assertIsNone(stats.avg_ms)
        self.assertAlmostEqual(stats.packet_loss_pct, 100.0)

    def test_rank_by_avg(self):
        s1 = HostStats("a", 443, 5, 5, 50.0, 60.0, 55.0, 1.0, 0.0)
        s2 = HostStats("b", 443, 5, 5, 10.0, 20.0, 15.0, 1.0, 0.0)
        s3 = HostStats("c", 443, 5, 0, None, None, None, None, 100.0)
        ranked = rank_by_avg([s1, s2, s3])
        self.assertEqual(ranked[0].host, "b")
        self.assertEqual(ranked[1].host, "a")
        self.assertEqual(ranked[2].host, "c")

    def test_single_ping_stddev_is_zero(self):
        stats = analyze("host", 443, [_ok(42.0)])
        self.assertAlmostEqual(stats.stddev_ms, 0.0)


if __name__ == "__main__":
    unittest.main()
