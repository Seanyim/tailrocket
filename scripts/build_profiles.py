#!/usr/bin/env python3
"""Safely build every TailRocket profile from the upstream release branch."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

import build_config


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "profiles.json"
DEFAULT_RULES = ROOT / "custom_rules.conf"
ALIAS_SOURCE = "sr_top500_banlist.conf"
ALIAS_NAME = "sr_top500_custom.conf"


def load_manifest(path: Path = DEFAULT_MANIFEST) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    profiles = data.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        raise ValueError("profiles manifest must contain a non-empty profiles list")
    names = [profile.get("name") for profile in profiles]
    if any(not isinstance(name, str) or not name.endswith(".conf") for name in names):
        raise ValueError("every manifest profile must have a .conf name")
    if len(set(names)) != len(names):
        raise ValueError("profiles manifest contains duplicate names")
    required = {"name", "kind", "mode", "title", "use", "ads"}
    for profile in profiles:
        missing = sorted(required - profile.keys())
        if missing:
            raise ValueError(f"profile {profile.get('name', '<unknown>')} is missing: {', '.join(missing)}")
        if profile["kind"] not in {"full", "fragment"}:
            raise ValueError(f"profile {profile['name']} has an unknown kind")
        if profile["mode"] not in {"proxy", "grouped", "none"}:
            raise ValueError(f"profile {profile['name']} has an unknown mode")
        if profile["kind"] == "full" and profile.get("final") not in {"DIRECT", "PROXY"}:
            raise ValueError(f"full profile {profile['name']} must declare DIRECT or PROXY final")
        if profile["kind"] == "fragment" and profile.get("final") is not None:
            raise ValueError(f"fragment profile {profile['name']} cannot declare a final policy")
    return data


def _request_text(url: str, attempts: int = build_config.FETCH_ATTEMPTS) -> str:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "tailrocket-updater/5.0", "Accept": "application/json"},
            )
            token = os.environ.get("GITHUB_TOKEN")
            if token:
                request.add_header("Authorization", f"Bearer {token}")
            with urllib.request.urlopen(request, timeout=45) as response:
                return response.read().decode("utf-8-sig")
        except (OSError, UnicodeDecodeError, ValueError) as error:
            last_error = error
            if attempt < attempts:
                build_config.time.sleep(2 ** (attempt - 1))
    raise RuntimeError(f"unable to fetch {url} after {attempts} attempts: {last_error}") from last_error


def upstream_conf_names(manifest: dict[str, Any]) -> set[str]:
    upstream = manifest["upstream"]
    url = f"https://api.github.com/repos/{upstream['repository']}/contents?ref={upstream['branch']}"
    payload = json.loads(_request_text(url))
    if not isinstance(payload, list):
        raise ValueError("upstream contents API returned a non-list response")
    return {item["name"] for item in payload if item.get("type") == "file" and item.get("name", "").endswith(".conf")}


def validate_upstream_set(manifest: dict[str, Any], actual: set[str]) -> None:
    expected = {profile["name"] for profile in manifest["profiles"]}
    missing = sorted(expected - actual)
    unexpected = sorted(actual - expected)
    if missing or unexpected:
        details = []
        if missing:
            details.append(f"missing from upstream: {', '.join(missing)}")
        if unexpected:
            details.append(f"not in manifest: {', '.join(unexpected)}")
        raise ValueError("upstream .conf manifest changed; " + "; ".join(details))


def _validate_fragment(text: str) -> None:
    lines = build_config._normalise_lines(text)
    if lines.count("[Rule]") != 1:
        raise ValueError("generated ad-only fragment must contain exactly one [Rule]")
    if any(line in {"[General]", "[URL Rewrite]", "[MITM]"} for line in lines):
        raise ValueError("ad-only fragment unexpectedly contains complete-config sections")
    if build_config.TAILSCALE_RULE in lines:
        raise ValueError("ad-only fragment must not contain Tailscale routing")


def _profile_url(base: str, name: str) -> str:
    return f"{base.rstrip('/')}/profiles/{name}"


def _write_stage(
    manifest: dict[str, Any],
    rules_text: str,
    stage: Path,
    pages_base: str,
) -> dict[str, str]:
    upstream = manifest["upstream"]
    raw_base = upstream["raw_base"].rstrip("/")
    stage_profiles = stage / "profiles"
    stage_profiles.mkdir(parents=True, exist_ok=True)
    fetched: dict[str, str] = {}
    generated: dict[str, str] = {}

    for profile in manifest["profiles"]:
        name = profile["name"]
        url = f"{raw_base}/{name}"
        if profile["kind"] == "fragment":
            source = build_config.fetch_text(url)
            output = build_config.patch_fragment(source)
            _validate_fragment(output)
        else:
            source = build_config.fetch(url)
            update_url = _profile_url(pages_base, name)
            output = build_config.patch(
                source,
                rules_text,
                update_url,
                custom_mode=profile["mode"],
                final_policy=profile["final"],
            )
        fetched[name] = source
        generated[name] = output
        (stage_profiles / name).write_text(output, encoding="utf-8", newline="\n")

    alias_source = fetched.get(ALIAS_SOURCE)
    if alias_source is None:
        raise ValueError(f"alias source {ALIAS_SOURCE} is absent from the profile manifest")
    alias_url = f"{pages_base.rstrip('/')}/{ALIAS_NAME}"
    alias_output = build_config.patch(alias_source, rules_text, alias_url, final_policy="DIRECT")
    (stage / ALIAS_NAME).write_text(alias_output, encoding="utf-8", newline="\n")
    generated[ALIAS_NAME] = alias_output
    return generated


def _replace_outputs(stage: Path, output_dir: Path, alias_output: Path) -> None:
    """Replace generated files only after every profile passed validation."""

    output_dir.parent.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    staged_profiles = stage / "profiles"
    expected = {path.name for path in staged_profiles.glob("*.conf")}
    for stale in output_dir.glob("*.conf"):
        if stale.name not in expected:
            stale.unlink()
    for staged in sorted(staged_profiles.glob("*.conf")):
        staged.replace(output_dir / staged.name)
    alias_output.parent.mkdir(parents=True, exist_ok=True)
    (stage / ALIAS_NAME).replace(alias_output)


def build_all(
    *,
    manifest_path: Path = DEFAULT_MANIFEST,
    rules_path: Path = DEFAULT_RULES,
    output_dir: Path | None = None,
    alias_output: Path | None = None,
    pages_base: str = "https://seanyim.github.io/tailrocket",
    verify_upstream: bool = True,
) -> dict[str, str]:
    manifest = load_manifest(manifest_path)
    if output_dir is None:
        output_dir = ROOT / "profiles"
    if alias_output is None:
        alias_output = ROOT / ALIAS_NAME
    rules_text = rules_path.read_text(encoding="utf-8")

    if verify_upstream:
        validate_upstream_set(manifest, upstream_conf_names(manifest))

    with tempfile.TemporaryDirectory(prefix="tailrocket-build-", dir=str(ROOT.parent)) as temp_dir:
        stage = Path(temp_dir)
        generated = _write_stage(manifest, rules_text, stage, pages_base)
        _replace_outputs(stage, output_dir, alias_output)
    return generated


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "profiles")
    parser.add_argument("--alias-output", type=Path, default=ROOT / ALIAS_NAME)
    parser.add_argument("--pages-base", required=True)
    parser.add_argument("--skip-upstream-set", action="store_true")
    args = parser.parse_args()

    generated = build_all(
        manifest_path=args.manifest,
        rules_path=args.rules,
        output_dir=args.output_dir,
        alias_output=args.alias_output,
        pages_base=args.pages_base,
        verify_upstream=not args.skip_upstream_set,
    )
    print(f"Built {len(generated)} TailRocket configurations.")
    for name in sorted(generated):
        print(f"  {name}")


if __name__ == "__main__":
    main()
