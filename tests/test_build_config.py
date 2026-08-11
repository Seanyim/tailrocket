import sys
import unittest
from pathlib import Path
from unittest.mock import patch as mock_patch
from urllib.error import URLError


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import build_config  # noqa: E402


UPSTREAM = """# upstream
[General]
ipv6 = false
prefer-ipv6 = false
dns-server = https://example.invalid/dns
bypass-tun = 10.0.0.0/8,100.64.0.0/10,192.168.0.0/16
tun-excluded-routes = 100.64.0.0/10,fc00::/7
tun-included-routes = 100.64.0.0/10
update-url = https://upstream.invalid/config.conf

[Rule]
DOMAIN-SUFFIX,upstream.example,DIRECT
FINAL,direct

[URL Rewrite]
^https?://example.invalid https://example.com 302

[MITM]
hostname = example.com
"""

CUSTOM_RULES = """# personal rules
IP-CIDR,100.64.0.0/10,TAILSCALE,no-resolve
DOMAIN-SUFFIX,booking.com,PROXY
"""


class _Response:
    def __init__(self, text: str):
        self.text = text

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self):
        return self.text.encode("utf-8")


class BuildConfigTests(unittest.TestCase):
    def test_patch_replaces_settings_and_removes_conflicting_routes(self):
        output = build_config.patch(UPSTREAM, CUSTOM_RULES, "https://raw.example/repo/main/config.conf")

        self.assertIn("ipv6 = true", output)
        self.assertIn("prefer-ipv6 = true", output)
        self.assertIn("dns-server = system", output)
        self.assertNotIn("tun-included-routes =", output)
        general = output.split("[Rule]", 1)[0]
        self.assertNotIn("100.64.0.0/10", general)
        self.assertEqual(output.count(build_config.TAILSCALE_RULE), 1)
        self.assertLess(output.index(build_config.TAILSCALE_RULE), output.index("DOMAIN-SUFFIX,upstream.example"))
        self.assertIn("FINAL,direct", output)
        self.assertIn("[URL Rewrite]", output)
        self.assertIn("[MITM]", output)

    def test_update_url_is_replaced_once(self):
        output = build_config.patch(UPSTREAM, CUSTOM_RULES, "https://raw.example/repo/main/config.conf")
        self.assertEqual(output.count("update-url = https://raw.example/repo/main/config.conf"), 1)
        self.assertNotIn("upstream.invalid", output)

    def test_duplicate_tailscale_rule_is_rejected(self):
        duplicate = CUSTOM_RULES + build_config.TAILSCALE_RULE + "\n"
        with self.assertRaisesRegex(ValueError, "exactly one Tailscale"):
            build_config.patch(UPSTREAM, duplicate, "https://raw.example/repo/main/config.conf")

    def test_missing_required_section_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "missing required sections"):
            build_config.patch(UPSTREAM.replace("[MITM]", "[Missing]"), CUSTOM_RULES, "https://raw.example/repo/main/config.conf")

    def test_fetch_retries_transient_error(self):
        with mock_patch.object(
            build_config.urllib.request,
            "urlopen",
            side_effect=[URLError("temporary"), _Response(UPSTREAM)],
        ) as urlopen, mock_patch.object(build_config.time, "sleep") as sleep:
            result = build_config.fetch("https://upstream.invalid/config.conf", attempts=2)

        self.assertEqual(result, UPSTREAM)
        self.assertEqual(urlopen.call_count, 2)
        sleep.assert_called_once_with(1)


if __name__ == "__main__":
    unittest.main()
