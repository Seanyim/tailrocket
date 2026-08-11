#!/usr/bin/env python3
"""Build the managed Shadowrocket configuration from the upstream release."""

from __future__ import annotations

import argparse
import re
import time
import urllib.request
from pathlib import Path
from urllib.error import HTTPError, URLError


TAILSCALE_V4 = "100.64.0.0/10"
TAILSCALE_RULE = "IP-CIDR,100.64.0.0/10,TAILSCALE,no-resolve"
REQUIRED_SECTIONS = ("[General]", "[Rule]", "[URL Rewrite]", "[MITM]")
FETCH_ATTEMPTS = 3


def _has_section(lines: list[str], section: str) -> bool:
    return section in lines


def _validate_upstream(text: str) -> None:
    lines = text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    missing = [section for section in REQUIRED_SECTIONS if not _has_section(lines, section)]
    if missing:
        raise ValueError(f"upstream config is missing required sections: {', '.join(missing)}")
    if lines.index("[General]") >= lines.index("[Rule]"):
        raise ValueError("upstream config has [General] after [Rule]")


def fetch(url: str, attempts: int = FETCH_ATTEMPTS) -> str:
    """Fetch and minimally validate an upstream config, retrying transient errors."""

    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "shadowrocket-custom-updater/4.0"},
            )
            with urllib.request.urlopen(request, timeout=45) as response:
                text = response.read().decode("utf-8-sig")
            if not text.strip():
                raise ValueError("upstream response was empty")
            _validate_upstream(text)
            return text
        except (HTTPError, URLError, TimeoutError, OSError, UnicodeDecodeError, ValueError) as error:
            last_error = error
            if attempt < attempts:
                time.sleep(2 ** (attempt - 1))
    raise RuntimeError(f"unable to fetch a valid upstream config after {attempts} attempts: {last_error}") from last_error


def csv_items(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def set_key(lines: list[str], key: str, value: str) -> list[str]:
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*=")
    output: list[str] = []
    found = False
    for line in lines:
        if pattern.match(line):
            if not found:
                output.append(f"{key} = {value}")
                found = True
        else:
            output.append(line)
    if not found:
        while output and not output[-1].strip():
            output.pop()
        output += [f"{key} = {value}", ""]
    return output


def remove_key(lines: list[str], key: str) -> list[str]:
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*=")
    return [line for line in lines if not pattern.match(line)]


def remove_route(lines: list[str], key: str, route: str) -> list[str]:
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*=\s*(.*)$")
    output: list[str] = []
    for line in lines:
        match = pattern.match(line)
        if not match:
            output.append(line)
            continue
        values = [item for item in csv_items(match.group(1)) if item != route]
        output.append(f"{key} = {','.join(values)}")
    return output


def _general_and_rules(lines: list[str]) -> tuple[list[str], list[str]]:
    general_index = lines.index("[General]")
    rule_index = lines.index("[Rule]")
    return lines[general_index + 1 : rule_index], lines[rule_index + 1 :]


def validate_config(text: str, update_url: str, custom_rules: str) -> None:
    """Reject output that would silently lose routing or upstream sections."""

    lines = text.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    missing = [section for section in REQUIRED_SECTIONS if lines.count(section) != 1]
    if missing:
        raise ValueError(f"generated config must contain each required section once: {', '.join(missing)}")

    general, rules = _general_and_rules(lines)
    expected_keys = {
        "ipv6": "true",
        "prefer-ipv6": "true",
        "dns-server": "system",
        "update-url": update_url,
    }
    for key, value in expected_keys.items():
        matches = [line.strip() for line in general if re.match(rf"^{re.escape(key)}\s*=", line)]
        if matches != [f"{key} = {value}"]:
            raise ValueError(f"generated config has invalid {key}: {matches}")

    for line in general:
        if re.match(r"^\s*tun-included-routes\s*=", line):
            raise ValueError("generated config must not contain tun-included-routes")
        for key in ("bypass-tun", "tun-excluded-routes"):
            match = re.match(rf"^\s*{key}\s*=\s*(.*)$", line)
            if match and TAILSCALE_V4 in csv_items(match.group(1)):
                raise ValueError(f"{TAILSCALE_V4} remains in {key}")

    if rules.count(TAILSCALE_RULE) != 1:
        raise ValueError("generated config must contain exactly one Tailscale IPv4 rule")
    custom_lines = custom_rules.strip().splitlines()
    rule_body = list(rules)
    while rule_body and not rule_body[0].strip():
        rule_body.pop(0)
    if rule_body[: len(custom_lines)] != custom_lines:
        raise ValueError("custom rules are not at the top of [Rule]")
    if not any(re.match(r"^FINAL\s*,\s*DIRECT\s*$", line, re.IGNORECASE) for line in rules):
        raise ValueError("generated config lost the upstream FINAL,DIRECT rule")


def patch(src: str, custom_rules: str, update_url: str) -> str:
    lines = src.replace("\r\n", "\n").replace("\r", "\n").splitlines()
    _validate_upstream(src)
    general_index = lines.index("[General]")
    rule_index = lines.index("[Rule]")
    prefix = lines[: general_index + 1]
    general = lines[general_index + 1 : rule_index]
    tail = lines[rule_index + 1 :]

    general = set_key(general, "ipv6", "true")
    general = set_key(general, "prefer-ipv6", "true")
    general = set_key(general, "dns-server", "system")
    general = remove_route(general, "bypass-tun", TAILSCALE_V4)
    general = remove_route(general, "tun-excluded-routes", TAILSCALE_V4)
    general = remove_key(general, "tun-included-routes")
    general = [line for line in general if not re.match(r"^\s*update-url\s*=", line)]
    while general and not general[-1].strip():
        general.pop()
    general += [f"update-url = {update_url}", ""]

    banner = [
        "",
        "# ============================================================================",
        "# CUSTOM MANAGED SETTINGS",
        "# SPDX-License-Identifier: CC-BY-SA-4.0",
        "# Derived from Johnshall/Shadowrocket-ADBlock-Rules-Forever (release).",
        "# IPv6: ON; IPv6 preferred: ON; DNS: system DNS.",
        "# Tailscale: validated minimal IPv4 routing; no forced TUN route or DERP.",
        "# ============================================================================",
        "",
    ]
    output = "\n".join(
        prefix
        + banner
        + general
        + ["[Rule]", ""]
        + custom_rules.strip().splitlines()
        + [""]
        + tail
    ).rstrip() + "\n"
    validate_config(output, update_url, custom_rules)
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", required=True)
    parser.add_argument("--rules", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--update-url", required=True)
    args = parser.parse_args()

    source = fetch(args.upstream)
    rules = Path(args.rules).read_text(encoding="utf-8")
    output = patch(source, rules, args.update_url)
    Path(args.output).write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
