# Bitwarden Touch ID in Dia on macOS

**Languages:** English · [繁體中文](README.zh-Hant.md) · [简体中文](README.zh-Hans.md)

This community workaround helps the official Bitwarden browser extension use Bitwarden Desktop for Touch ID unlock in Dia. It was verified on **macOS 27.0, Dia 1.50.1, Bitwarden Desktop 2026.9.0, and Bitwarden extension 2026.9.2**. It may need adjustment for other versions.

The workaround has two parts:

1. Install Bitwarden's native messaging host manifest in Dia's browser directory. This tells Dia where to find Bitwarden Desktop's `desktop_proxy`.
2. Request the extension's optional `nativeMessaging` permission from a **normal browser tab**. In the tested version, Bitwarden's automatic request from its pop-out window hung without a Dia permission prompt or callback. The same request from a normal tab showed Dia's prompt and succeeded.

**You review and approve the browser permission prompt yourself.** Nothing here changes Dia's code or Bitwarden's extension package.

## Before you start

You need:

- Dia, Bitwarden Desktop, and the **official Chrome Web Store Bitwarden Password Manager extension** installed in Dia.
- Touch ID already enabled and working in Bitwarden Desktop. Keep Desktop running, signed in, and unlocked during setup.
- A Chrome Bitwarden native messaging manifest at `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.8bit.bitwarden.json`. This helper uses it as the source and does not modify it.
- Python 3.10 or newer available as `python3`.

The helper accepts only the official extension ID `nngceckbapebfimnlniiiahkandclblb`. It discovers the installed ID in Dia, checks the extension's localized name, and rejects a different ID even if it uses the same name.

## Quick start

### 1. Check the local installation

In Terminal, change to this repository's directory and run:

```sh
python3 install_host.py
```

This is a **read-only check**. It prints the detected Dia application, Dia data directory, Bitwarden extension ID, Chrome source manifest, Dia destination, desktop proxy, and the extension URL to use later. If it says `already correct`, skip the next command.

If it says `installation needed`, run:

```sh
python3 install_host.py --apply
```

The helper validates the JSON and proxy, creates Dia's `NativeMessagingHosts` directory if needed, and writes `com.8bit.bitwarden.json` there. If a different Dia manifest already exists, it saves a timestamped `.backup-*` copy beside it **before** replacing it. A second run with the same contents makes no change. The Chrome source file is never edited.

**Quit Dia completely and reopen it** after changing the manifest.

### 2. Request permission from a normal Dia tab

1. In Dia, unlock the Bitwarden extension if necessary. Keep Bitwarden Desktop open and unlocked.
2. Open the extension's account security page in a **normal Dia tab**, not its toolbar popup or pop-out window. Use the URL printed by the helper. For the official extension it is:

   ```text
   chrome-extension://nngceckbapebfimnlniiiahkandclblb/popup/index.html#/account-security
   ```

3. With that tab active, open Developer Tools using **Option-Command-I** and select **Console**.
4. Read [`request-permission.js`](request-permission.js), then paste its entire contents into the Console and press Enter. It adds a yellow **Request Bitwarden nativeMessaging permission** button to the page. The snippet checks the extension ID before doing anything.
5. Click the yellow button. This actual user click is required by the browser's permission API. Dia should show a prompt saying **Bitwarden Password Manager** has requested additional permissions. Check the extension name, then choose **Allow** if you want to connect it to native applications.
6. The Console should show `Permission granted: true`. Close the test tab; the temporary button disappears. Dia retains the permission in that profile.

The Terminal helper cannot perform this step. Browser permissions must be requested from the extension page and approved in Dia's own UI. See [Chrome's runtime permission API](https://developer.chrome.com/docs/extensions/reference/api/permissions).

### 3. Finish setup in Bitwarden and verify

1. Open Bitwarden's normal extension popup in Dia.
2. Go to **Settings → Account security → Unlock with biometrics**. Follow any Bitwarden Desktop confirmation or Touch ID prompt. If the extension locks during setup, unlock it and try the setting again.
3. Lock the extension, then use its **Unlock with biometrics** option. A successful Touch ID unlock is the end-to-end check; a saved browser permission alone does not prove Desktop pairing works.

## What the helper changes

| Item | Action |
| --- | --- |
| Chrome's `com.8bit.bitwarden.json` | Read only |
| Dia's `NativeMessagingHosts/com.8bit.bitwarden.json` | Created or replaced by `--apply` |
| Existing Dia host manifest | Backed up next to the destination before replacement |
| Dia extension permission | Granted only through Dia's prompt after your click |
| Bitwarden vault, extension package, browser `Secure Preferences` | Not read or modified by the helper |

The helper copies Chrome's manifest fields and adds the detected Dia Bitwarden extension origin to `allowed_origins` only if it is missing. It verifies that `desktop_proxy` is executable, belongs to `Bitwarden.app`, and has a valid Bitwarden Inc. macOS code signature. It does **not** copy Chrome's extension permission state: permissions belong to each browser profile.

For nonstandard install locations, run `python3 install_host.py --help` to see `--dia-app`, `--dia-data`, and `--chrome-manifest`. Check the paths carefully before using `--apply`.

## Security and privacy

- The `chrome-extension://...` URL is a page **inside the installed Bitwarden extension**, not a website or a link to your vault. Its ID is the public ID of the official Chrome Web Store extension, not a personal identifier.
- The helper uses only local files and macOS `codesign`; it makes no network requests. The GitHub repository does not include your vault, local manifests, backups, email address, or full home-directory path.
- The `nativeMessaging` permission lets the Bitwarden extension communicate with a registered local program. The host manifest's `allowed_origins` limits which extension IDs can start this host. This is a meaningful permission: approve it only for the official extension and a validly signed Bitwarden Desktop app.
- Pasting JavaScript into a password manager's DevTools Console is powerful. Read the exact snippet before running it and re-check it if you return to this repository later. The snippet only checks the extension ID, adds a temporary button, and requests the permission after your click; it does not read vault items or send data to a server.
- The helper treats Chrome's manifest as input and validates the target binary's signature. If either your local Chrome manifest or the app bundle looks suspicious, stop rather than bypassing a validation error.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| `No installed Bitwarden extension was found` | Install the official extension in Dia, then rerun the check. |
| `unexpected ID` | Stop and verify the extension's source. This guide supports the official Chrome Web Store ID only. |
| Chrome manifest or `desktop_proxy` missing | Open Bitwarden Desktop and check that its browser integration has installed the Chrome manifest. This helper needs a valid Chrome source. |
| Dia still does not show a permission prompt | Confirm the URL starts with `chrome-extension://` and is open as a **normal tab**. Run the snippet in that tab's Console and click the yellow button; pasting `chrome.permissions.request(...)` directly into Console does not provide the required user click. |
| Console reports `Permission granted: false` | Retry the prompt and check your choice. Do not edit `Secure Preferences` to force a grant. |
| Permission granted, but Desktop is not found | Confirm the Dia host manifest exists, its `path` points to an executable `desktop_proxy`, and Bitwarden Desktop is running and unlocked. Quit and reopen Dia after a manifest change. |
| Setup works in one Dia profile but not another | Browser permissions are profile-specific. Open the Bitwarden page in the affected profile and repeat the permission step there. |

## Undo the host installation

The helper's only persistent file change is Dia's `com.8bit.bitwarden.json`.

- If the helper printed a backup path, restore **that** backup to Dia's `NativeMessagingHosts/com.8bit.bitwarden.json` after quitting Dia.
- If no Dia host file existed before installation, remove only Dia's `com.8bit.bitwarden.json` after quitting Dia.
- Reopen Dia. Do not delete Bitwarden vault files, the Chrome source manifest, or browser profile files.

The separate `nativeMessaging` permission is stored by Dia in the affected profile. This helper does not alter it, and restoring the host file does not revoke it.

## Why this is a workaround

In the tested environment, Bitwarden's pop-out window invoked `chrome.permissions.request({ permissions: ["nativeMessaging"] })` with a valid user gesture, but Dia did not display a permission prompt or call the callback. The normal-tab button invoked the **same API** and Dia returned `true` after the user approved it. This narrows the observed problem to Dia's handling of that window/request flow; it does not identify a specific line of Dia code.

[Bitwarden issue #14274](https://github.com/bitwarden/clients/issues/14274) reported Dia biometric unlock failures in 2025. The issue is closed. See [`BUG_REPORT.md`](BUG_REPORT.md) for a concise reproduction report.
