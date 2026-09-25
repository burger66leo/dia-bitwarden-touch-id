#!/usr/bin/env python3
"""Check or install Bitwarden's Chrome native messaging manifest for Dia."""

import argparse
import datetime as dt
import json
import os
import plistlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HOST_NAME = "com.8bit.bitwarden"
EXTENSION_NAME = "Bitwarden Password Manager"
DEFAULT_ID = "nngceckbapebfimnlniiiahkandclblb"
BITWARDEN_TEAM_ID = "LTZ2PFU5D6"
ID_PATTERN = re.compile(r"[a-p]{32}")


def fail(message: str) -> None:
    raise SystemExit(f"Error: {message}")


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        fail(f"Cannot read valid JSON from {path}: {exc}")
    if not isinstance(value, dict):
        fail(f"Expected a JSON object in {path}")
    return value


def find_dia_app(override: Path | None) -> Path:
    candidates = [override] if override else [
        Path("/Applications/Dia.app"),
        Path.home() / "Applications/Dia.app",
    ]
    for app in candidates:
        if app is None:
            continue
        try:
            with (app / "Contents/Info.plist").open("rb") as stream:
                info = plistlib.load(stream)
        except (OSError, ValueError):
            continue
        if info.get("CFBundleIdentifier") == "company.thebrowser.dia":
            return app
    fail("Dia.app was not found in /Applications or ~/Applications (or --dia-app).")


def localized_name(version_dir: Path, manifest: dict) -> str:
    name = manifest.get("name", "")
    if not isinstance(name, str):
        return ""
    if not (name.startswith("__MSG_") and name.endswith("__")):
        return name
    key = name[6:-2]
    locale = manifest.get("default_locale", "en")
    messages_path = version_dir / "_locales" / locale / "messages.json"
    if not messages_path.is_file():
        return ""
    messages = read_json(messages_path)
    for actual_key, value in messages.items():
        if actual_key.lower() == key.lower() and isinstance(value, dict):
            return value.get("message", "")
    return ""


def find_extension_ids(dia_data: Path) -> list[str]:
    ids: set[str] = set()
    user_data = dia_data / "User Data"
    if not user_data.is_dir():
        fail(f"Dia user data was not found: {user_data}")
    for profile in user_data.iterdir():
        extensions = profile / "Extensions"
        if not extensions.is_dir():
            continue
        for extension in extensions.iterdir():
            if not extension.is_dir() or not ID_PATTERN.fullmatch(extension.name):
                continue
            for version_dir in extension.iterdir():
                path = version_dir / "manifest.json"
                if not path.is_file():
                    continue
                manifest = read_json(path)
                if localized_name(version_dir, manifest) == EXTENSION_NAME:
                    ids.add(extension.name)
    if not ids:
        fail("No installed Bitwarden extension was found in Dia profiles.")
    if ids != {DEFAULT_ID}:
        fail(
            "Found a Bitwarden-named extension with an unexpected ID. "
            f"For safety, this helper supports only the official Chrome Web Store ID {DEFAULT_ID}. "
            f"Detected: {', '.join(sorted(ids))}"
        )
    return sorted(ids)


def validate_source(source: Path) -> dict:
    manifest = read_json(source)
    if manifest.get("name") != HOST_NAME or manifest.get("type") != "stdio":
        fail("Chrome's manifest is not the expected Bitwarden native messaging host.")
    binary = manifest.get("path")
    if not isinstance(binary, str) or not Path(binary).is_absolute():
        fail("Chrome's manifest must point to an absolute desktop_proxy path.")
    binary_path = Path(binary)
    if binary_path.name != "desktop_proxy":
        fail("Chrome's manifest does not point to a Bitwarden desktop_proxy binary.")
    if not binary_path.is_file() or not os.access(binary, os.X_OK):
        fail(f"The desktop_proxy in Chrome's manifest is not executable: {binary}")
    resolved_binary = binary_path.resolve()
    if len(resolved_binary.parents) < 3:
        fail("The desktop_proxy is not inside a Bitwarden.app bundle.")
    app = resolved_binary.parents[2]
    if (resolved_binary.parent.name != "MacOS" or
            resolved_binary.parent.parent.name != "Contents" or
            app.name != "Bitwarden.app"):
        fail("The desktop_proxy is not inside a Bitwarden.app bundle.")
    try:
        with (app / "Contents/Info.plist").open("rb") as stream:
            app_info = plistlib.load(stream)
    except (OSError, ValueError) as exc:
        fail(f"Cannot read Bitwarden.app metadata: {exc}")
    if app_info.get("CFBundleIdentifier") != "com.bitwarden.desktop":
        fail("The desktop_proxy is not inside the official Bitwarden Desktop app.")
    try:
        verification = subprocess.run(
            ["codesign", "--verify", "--strict", str(resolved_binary)],
            capture_output=True, text=True, timeout=30, check=False,
        )
        signature = subprocess.run(
            ["codesign", "-dv", "--verbose=2", str(resolved_binary)],
            capture_output=True, text=True, timeout=30, check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        fail(f"Could not verify Bitwarden's code signature: {exc}")
    details = signature.stdout + signature.stderr
    if (verification.returncode != 0 or signature.returncode != 0 or
            f"TeamIdentifier={BITWARDEN_TEAM_ID}" not in details or
            "Identifier=com.bitwarden.desktop" not in details):
        fail("The desktop_proxy is not validly signed by Bitwarden Inc.")
    origins = manifest.get("allowed_origins")
    if not isinstance(origins, list) or not all(isinstance(x, str) for x in origins):
        fail("Chrome's manifest has no valid allowed_origins list.")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Back up and install the manifest")
    parser.add_argument("--dia-app", type=Path, help="Dia.app location (auto-detected by default)")
    parser.add_argument("--dia-data", type=Path, help="Dia Application Support directory")
    parser.add_argument("--chrome-manifest", type=Path, help="Chrome Bitwarden host manifest")
    args = parser.parse_args()

    home = Path.home()
    dia_app = find_dia_app(args.dia_app)
    dia_data = args.dia_data or home / "Library/Application Support/Dia"
    source = args.chrome_manifest or home / "Library/Application Support/Google/Chrome/NativeMessagingHosts/com.8bit.bitwarden.json"
    target = dia_data / "NativeMessagingHosts/com.8bit.bitwarden.json"
    ids = find_extension_ids(dia_data)
    manifest = validate_source(source)

    for extension_id in ids:
        origin = f"chrome-extension://{extension_id}/"
        if origin not in manifest["allowed_origins"]:
            manifest["allowed_origins"].append(origin)

    print(f"Dia app: {dia_app}")
    print(f"Dia data: {dia_data}")
    print(f"Bitwarden extension ID(s): {', '.join(ids)}")
    print(f"Chrome source: {source}")
    print(f"Dia destination: {target}")
    print(f"Desktop proxy: {manifest['path']}")
    print(f"Open this URL in a normal Dia tab: chrome-extension://{ids[0]}/popup/index.html#/account-security")

    if target.is_symlink():
        fail("Dia's existing host file is a symlink. Inspect it manually before replacing it.")
    if target.is_file() and read_json(target) == manifest:
        print("Status: Dia's manifest is already correct; no changes needed.")
        return
    if target.exists() and not target.is_file():
        fail("Dia's destination exists but is not a regular file.")
    if not args.apply:
        print("Status: installation needed. Re-run with --apply to back up and install.")
        return

    target.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    if target.exists():
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        backup = target.with_name(f"{target.name}.backup-{stamp}")
        shutil.copy2(target, backup)
        print(f"Backup: {backup}")

    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=target.parent,
                                         prefix=".bitwarden-host-", suffix=".json", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(manifest, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o644)
        os.replace(temporary, target)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    if read_json(target) != manifest:
        fail("Installed manifest did not verify. Restore the backup if needed.")
    print("Installed and verified. Quit and reopen Dia before requesting permission.")


if __name__ == "__main__":
    main()
