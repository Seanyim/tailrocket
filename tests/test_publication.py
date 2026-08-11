import json
import re
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
MANIFEST = json.loads((REPO / "profiles.json").read_text(encoding="utf-8"))
TAILSCALE_RULE = "IP-CIDR,100.64.0.0/10,TAILSCALE,no-resolve"


def section_end(lines, start):
    for index in range(start + 1, len(lines)):
        if re.match(r"^\[[^]]+\]$", lines[index]):
            return index
    return len(lines)


class PublicationTests(unittest.TestCase):
    def test_all_generated_profiles_are_present_and_linked(self):
        readme = (REPO / "README.md").read_text(encoding="utf-8")
        for profile in MANIFEST["profiles"]:
            path = REPO / "profiles" / profile["name"]
            self.assertTrue(path.exists(), profile["name"])
            self.assertIn(f"profiles/{profile['name']}", readme)

    def test_complete_profiles_have_network_overlay_in_general_section(self):
        for profile in MANIFEST["profiles"]:
            path = REPO / "profiles" / profile["name"]
            lines = path.read_text(encoding="utf-8").splitlines()
            if profile["kind"] == "fragment":
                self.assertEqual(lines.count("[Rule]"), 1)
                self.assertNotIn("[General]", lines)
                continue
            general = lines.index("[General]")
            general_end = section_end(lines, general)
            general_lines = lines[general + 1 : general_end]
            self.assertIn("ipv6 = true", general_lines)
            self.assertIn("prefer-ipv6 = true", general_lines)
            self.assertIn("dns-server = system", general_lines)
            self.assertEqual(sum(line.startswith("update-url = ") for line in general_lines), 1)
            self.assertFalse(any(line.startswith("tun-included-routes =") for line in general_lines))
            self.assertFalse(any("100.64.0.0/10" in line for line in general_lines))
            rule = lines.index("[Rule]")
            effective = next(line for line in lines[rule + 1 :] if line.strip() and not line.lstrip().startswith("#"))
            self.assertEqual(effective, TAILSCALE_RULE, profile["name"])
            self.assertEqual(lines.count(TAILSCALE_RULE), 1)

    def test_no_placeholder_or_private_identity_in_public_source_files(self):
        checked = [
            REPO / "README.md",
            REPO / "FIRST_RUN.txt",
            REPO / "custom_rules.conf",
            REPO / "profiles.json",
            REPO / "scripts" / "build_config.py",
            REPO / "scripts" / "build_profiles.py",
            REPO / ".github" / "workflows" / "update-shadowrocket.yml",
        ]
        text = "\n".join(path.read_text(encoding="utf-8") for path in checked)
        self.assertNotRegex(text, r"YOUR_(?:OWNER|REPO)|OWNER/REPO")
        self.assertNotRegex(text, r"\b100\.(?!64\.0\.0/10\b)\d{1,3}\.\d{1,3}\.\d{1,3}\b")
        self.assertNotRegex(text, r"[A-Za-z0-9_-]+\.ts\.net")


if __name__ == "__main__":
    unittest.main()
