import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import urllib.error


REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import build_config  # noqa: E402
import build_profiles  # noqa: E402


class BuildProfilesTests(unittest.TestCase):
    def test_manifest_covers_all_upstream_release_profiles(self):
        manifest = build_profiles.load_manifest()
        names = {profile["name"] for profile in manifest["profiles"]}
        self.assertEqual(len(names), 14)
        self.assertEqual(
            names,
            {
                "lazy.conf", "lazy_group.conf", "sr_ad_only.conf", "sr_adb.conf",
                "sr_backcn.conf", "sr_backcn_ad.conf", "sr_cnip.conf", "sr_cnip_ad.conf",
                "sr_direct_banad.conf", "sr_proxy_banad.conf", "sr_top500_banlist.conf",
                "sr_top500_banlist_ad.conf", "sr_top500_whitelist.conf", "sr_top500_whitelist_ad.conf",
            },
        )

    def test_manifest_has_no_personal_rule_modes(self):
        manifest = build_profiles.load_manifest()
        self.assertTrue(all("mode" not in profile for profile in manifest["profiles"]))

    def test_upstream_manifest_drift_fails_closed(self):
        manifest = build_profiles.load_manifest()
        with self.assertRaisesRegex(ValueError, "not in manifest"):
            build_profiles.validate_upstream_set(
                manifest,
                {profile["name"] for profile in manifest["profiles"]} | {"new_profile.conf"},
            )

    def test_missing_upstream_profile_fails_closed(self):
        manifest = build_profiles.load_manifest()
        names = {profile["name"] for profile in manifest["profiles"]}
        names.pop()
        with self.assertRaisesRegex(ValueError, "missing from upstream"):
            build_profiles.validate_upstream_set(manifest, names)

    def test_upstream_failure_leaves_outputs_untouched(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / "profiles"
            output.mkdir()
            sentinel = output / "old.conf"
            sentinel.write_text("old")
            alias = root / "alias.conf"
            alias.write_text("old alias")
            with patch.object(build_profiles, "upstream_conf_names", side_effect=RuntimeError("rate limited")), patch.object(build_profiles, "_write_stage") as stage:
                with self.assertRaisesRegex(RuntimeError, "rate limited"):
                    build_profiles.build_all(output_dir=output, alias_output=alias)
                stage.assert_not_called()
            self.assertEqual(sentinel.read_text(), "old")
            self.assertEqual(alias.read_text(), "old alias")

    def test_token_is_only_sent_to_https_github_api(self):
        for url, allowed in [("https://api.github.com/repos/x/y/contents", True),
                             ("https://example.com/", False),
                             ("http://api.github.com/", False),
                             ("https://api.github.com.evil.example/", False)]:
            with self.subTest(url=url), patch.dict("os.environ", {"GITHUB_TOKEN": "test-token"}), patch.object(build_profiles.urllib.request, "build_opener") as factory:
                factory.return_value.open.return_value.__enter__.return_value.read.return_value = b"[]"
                build_profiles._request_text(url)
                request = factory.return_value.open.call_args.args[0]
                self.assertEqual(request.get_header("Authorization"), "Bearer test-token" if allowed else None)
                self.assertIsInstance(factory.call_args.args[0], build_profiles._NoRedirect)

    def test_redirect_is_refused(self):
        handler = build_profiles._NoRedirect()
        self.assertIsNone(handler.redirect_request(None, None, 302, "Found", {}, "https://example.com/"))

    def test_fetch_failure_has_bounded_retries(self):
        with patch.object(build_profiles.urllib.request, "build_opener") as factory, patch.object(build_config.time, "sleep") as sleep:
            factory.return_value.open.side_effect = urllib.error.HTTPError("https://api.github.com/", 403, "rate limit exceeded", {}, None)
            with self.assertRaisesRegex(RuntimeError, "after 3 attempts"):
                build_profiles._request_text("https://api.github.com/", attempts=3)
            self.assertEqual(factory.return_value.open.call_count, 3)
            self.assertEqual([call.args[0] for call in sleep.call_args_list], [1, 2])

    def test_complete_profile_has_only_tailscale_overlay(self):
        source = """# source
[General]
ipv6 = false
prefer-ipv6 = false
dns-server = system
bypass-tun = 100.64.0.0/10
[Rule]
FINAL,PROXY
[URL Rewrite]
[MITM]
"""
        output = build_config.patch(
            source,
            "https://pages.example/profiles/lazy_group.conf",
            final_policy="PROXY",
        )
        self.assertIn(build_config.TAILSCALE_RULE, output)
        self.assertNotIn("paypal.com", output)
        self.assertNotIn("amazon.com", output)
        self.assertNotIn("travel.example", output)

    def test_fragment_stays_fragment(self):
        fragment = "[Rule]\nDOMAIN-SUFFIX,ads.example,REJECT\n"
        output = build_config.patch_fragment(fragment)
        self.assertIn("[Rule]", output)
        self.assertNotIn("[General]", output)
        self.assertNotIn(build_config.TAILSCALE_RULE, output)

    def test_atomic_replace_does_not_publish_partial_stage(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output_dir = root / "profiles"
            output_dir.mkdir()
            (output_dir / "old.conf").write_text("old\n", encoding="utf-8")
            alias = root / "sr_top500_custom.conf"
            alias.write_text("old alias\n", encoding="utf-8")
            stage = root / "stage"
            (stage / "profiles").mkdir(parents=True)
            (stage / "profiles" / "new.conf").write_text("new\n", encoding="utf-8")
            (stage / "sr_top500_custom.conf").write_text("new alias\n", encoding="utf-8")

            build_profiles._replace_outputs(stage, output_dir, alias)

            self.assertEqual((output_dir / "new.conf").read_text(encoding="utf-8"), "new\n")
            self.assertFalse((output_dir / "old.conf").exists())
            self.assertEqual(alias.read_text(encoding="utf-8"), "new alias\n")

    def test_manifest_is_json_serialisable_for_readme_generation(self):
        manifest = build_profiles.load_manifest()
        self.assertEqual(json.loads(json.dumps(manifest))["upstream"]["branch"], "release")


if __name__ == "__main__":
    unittest.main()
