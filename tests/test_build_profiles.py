import json
import sys
import tempfile
import unittest
from pathlib import Path


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

    def test_manifest_keeps_semantic_modes_explicit(self):
        manifest = build_profiles.load_manifest()
        modes = {profile["name"]: profile["mode"] for profile in manifest["profiles"]}
        self.assertEqual(modes["lazy_group.conf"], "grouped")
        self.assertEqual(modes["sr_ad_only.conf"], "none")
        self.assertEqual(modes["sr_backcn.conf"], "none")
        self.assertEqual(modes["sr_top500_banlist.conf"], "proxy")

    def test_upstream_manifest_drift_fails_closed(self):
        manifest = build_profiles.load_manifest()
        with self.assertRaisesRegex(ValueError, "not in manifest"):
            build_profiles.validate_upstream_set(
                manifest,
                build_profiles.upstream_conf_names(manifest) | {"new_profile.conf"},
            )

    def test_grouped_overlay_preserves_named_groups(self):
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
        rules = """DOMAIN-SUFFIX,paypal.com,PROXY
DOMAIN-SUFFIX,amazon.com,PROXY
DOMAIN-SUFFIX,travel.example,PROXY
"""
        output = build_config.patch(
            source,
            rules,
            "https://pages.example/profiles/lazy_group.conf",
            custom_mode="grouped",
            final_policy="PROXY",
        )
        self.assertIn("DOMAIN-SUFFIX,paypal.com,PayPal", output)
        self.assertIn("DOMAIN-SUFFIX,amazon.com,Amazon", output)
        self.assertIn("DOMAIN-SUFFIX,travel.example,PROXY", output)

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
