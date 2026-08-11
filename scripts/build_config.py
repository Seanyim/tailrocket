#!/usr/bin/env python3
"""Patch one Shadowrocket configuration with the TailRocket overlay."""

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


def _normalise_lines(text: str) -> list[str]:
    return [line.rstrip() for line in text.replace("\r\n", "\n").replace("\r", "\n").splitlines()]


def _has_section(lines: list[str], section: str) -> bool:
    return lines.count(section) == 1


def _validate_upstream(text: str, required_sections: tuple[str, ...] = REQUIRED_SECTIONS) -> None:
    lines = _normalise_lines(text)
    missing = [section for section in required_sections if not _has_section(lines, section)]
    if missing:
        raise ValueError(f"upstream config is missing required sections: {', '.join(missing)}")
    if "[General]" in required_sections and lines.index("[General]") >= lines.index("[Rule]"):
        raise ValueError("upstream config has [General] after [Rule]")


def fetch(
    url: str,
    attempts: int = FETCH_ATTEMPTS,
    required_sections: tuple[str, ...] = REQUIRED_SECTIONS,
) -> str:
    """Fetch and minimally validate an upstream config, retrying transient errors."""

    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "tailrocket-updater/5.0"},
            )
            with urllib.request.urlopen(request, timeout=45) as response:
                text = response.read().decode("utf-8-sig")
            if not text.strip():
                raise ValueError("upstream response was empty")
            _validate_upstream(text, required_sections)
            return text
        except (HTTPError, URLError, TimeoutError, OSError, UnicodeDecodeError, ValueError) as error:
            last_error = error
            if attempt < attempts:
                time.sleep(2 ** (attempt - 1))
    raise RuntimeError(f"unable to fetch a valid upstream config after {attempts} attempts: {last_error}") from last_error


def fetch_text(url: str, attempts: int = FETCH_ATTEMPTS) -> str:
    """Fetch text that is validated by the caller, such as an ad-only fragment."""

    return fetch(url, attempts=attempts, required_sections=("[Rule]",))


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
    general_end = _next_section_index(lines, general_index)
    return lines[general_index + 1 : general_end], lines[rule_index + 1 :]


def _next_section_index(lines: list[str], start: int) -> int:
    for index in range(start + 1, len(lines)):
        if re.match(r"^\[[^]]+\]$", lines[index]):
            return index
    return len(lines)


def _strip_tailscale_rule(custom_rules: str) -> list[str]:
    """Keep old custom_rules.conf files compatible while owning the route here."""

    lines = _normalise_lines(custom_rules)
    count = sum(line.strip() == TAILSCALE_RULE for line in lines)
    if count > 1:
        raise ValueError("custom rules violate exactly one Tailscale IPv4 rule")
    return [line for line in lines if line.strip() != TAILSCALE_RULE]


def _rule_lines(custom_rules: str, mode: str) -> list[str]:
    lines = _strip_tailscale_rule(custom_rules)
    if mode not in {"proxy", "grouped", "none"}:
        raise ValueError(f"unknown custom rule mode: {mode}")
    if mode == "none":
        return []
    if mode == "proxy":
        return lines

    rewritten: list[str] = []
    for line in lines:
        if line.startswith("DOMAIN-SUFFIX,") and line.endswith(",PROXY"):
            if line.casefold().startswith("domain-suffix,paypal.com,"):
                line = line[:-len(",PROXY")] + ",PayPal"
            elif line.casefold().startswith("domain-suffix,amazon.com,"):
                line = line[:-len(",PROXY")] + ",Amazon"
        rewritten.append(line)
    return rewritten


def _clean_rule_prefix(lines: list[str]) -> list[str]:
    output = list(lines)
    while output and not output[0].strip():
        output.pop(0)
    return output


def _expected_final(final_policy: str) -> str:
    return f"FINAL,{final_policy}".casefold()


def validate_config(
    text: str,
    update_url: str,
    custom_rules: str,
    *,
    custom_mode: str = "proxy",
    final_policy: str = "DIRECT",
    required_sections: tuple[str, ...] = REQUIRED_SECTIONS,
) -> None:
    """Reject output that would silently lose routing or upstream sections."""

    lines = _normalise_lines(text)
    missing = [section for section in required_sections if lines.count(section) != 1]
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
    effective_custom = _rule_lines(custom_rules, custom_mode)
    rule_body = _clean_rule_prefix(rules)
    expected_prefix = [TAILSCALE_RULE] + effective_custom
    if rule_body[: len(expected_prefix)] != expected_prefix:
        raise ValueError("generated custom rules are not at the top of [Rule]")
    if not any(line.strip().casefold() == _expected_final(final_policy) for line in rules):
        raise ValueError(f"generated config lost the upstream {final_policy} final rule")


def patch(
    src: str,
    custom_rules: str,
    update_url: str,
    *,
    custom_mode: str = "proxy",
    final_policy: str = "DIRECT",
) -> str:
    """Patch one complete config; the original three-argument CLI remains valid."""

    lines = _normalise_lines(src)
    _validate_upstream(src)
    general_index = lines.index("[General]")
    general_end = _next_section_index(lines, general_index)
    rule_index = lines.index("[Rule]")
    before_general = lines[:general_index]
    general = lines[general_index + 1 : general_end]
    between_general_and_rule = lines[general_end:rule_index]
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
        "# ============================================================================",
        "# TailRocket managed overlay",
        "# SPDX-License-Identifier: CC-BY-SA-4.0",
        "# Derived from Johnshall/Shadowrocket-ADBlock-Rules-Forever (release).",
        "# IPv6: ON; IPv6 preferred: ON; DNS: system DNS.",
        "# Tailscale: validated minimal IPv4 routing; no forced TUN route or DERP.",
        "# ============================================================================",
        "",
    ]
    custom = _rule_lines(custom_rules, custom_mode)
    output = "\n".join(
        before_general
        + banner
        + ["[General]"]
        + general
        + between_general_and_rule
        + ["[Rule]", ""]
    )
    output += "\n".join([TAILSCALE_RULE] + custom + [""] + tail)
    output = output.rstrip() + "\n"
    validate_config(
        output,
        update_url,
        custom_rules,
        custom_mode=custom_mode,
        final_policy=final_policy,
    )
    return output


def patch_fragment(src: str) -> str:
    """Add provenance to an ad-only rule fragment without changing its semantics."""

    lines = _normalise_lines(src)
    if lines.count("[Rule]") != 1:
        raise ValueError("ad-only fragment must contain exactly one [Rule] section")
    header = [
        "# TailRocket compatibility overlay for the upstream ad-only fragment.",
        "# SPDX-License-Identifier: CC-BY-SA-4.0",
        "# Source: Johnshall/Shadowrocket-ADBlock-Rules-Forever (release).",
        "",
    ]
    return "\n".join(header + lines).rstrip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upstream", required=True)
    parser.add_argument("--rules", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--update-url", required=True)
    parser.add_argument("--custom-mode", choices=("proxy", "grouped", "none"), default="proxy")
    parser.add_argument("--final-policy", choices=("DIRECT", "PROXY"), default="DIRECT")
    args = parser.parse_args()

    source = fetch(args.upstream)
    rules = Path(args.rules).read_text(encoding="utf-8")
    output = patch(
        source,
        rules,
        args.update_url,
        custom_mode=args.custom_mode,
        final_policy=args.final_policy,
    )
    Path(args.output).write_text(output, encoding="utf-8")


if __name__ == "__main__":
    main()
