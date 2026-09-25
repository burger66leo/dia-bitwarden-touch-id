# Bitwarden Touch ID in Dia (macOS)

This is a community workaround for a Dia extension permission prompt that can stall when Bitwarden requests `nativeMessaging` from its pop-out window. It was verified on macOS 27.0, Dia 1.50.1, Bitwarden Desktop 2026.9.0, and Bitwarden extension 2026.9.2. Other versions may behave differently.

The workaround has two parts:

1. Install Bitwarden's native messaging host manifest in Dia's browser directory.
2. Request the extension's optional `nativeMessaging` permission from a normal Dia tab. **You must review and approve Dia's permission prompt yourself.**

The helper never reads vault data, changes your password, edits browser `Secure Preferences`, or changes the Bitwarden extension files.
It accepts only the official Chrome Web Store Bitwarden extension ID; another extension using the same display name will be rejected.

## Requirements

- Dia, Bitwarden Desktop, and the Bitwarden browser extension installed on macOS.
- Touch ID already working in Bitwarden Desktop. Keep Desktop running and unlocked during setup.
- A Chrome native messaging manifest at `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.8bit.bitwarden.json`.
- Python 3 available as `python3`.

## Install the native messaging host

Run from this folder:

```sh
python3 install_host.py
python3 install_host.py --apply
```

The first command checks the app, extension ID, Chrome manifest, and destination without changing anything. The second copies the Chrome manifest into Dia's `NativeMessagingHosts` directory and adds the detected Dia Bitwarden extension ID to `allowed_origins` if needed. It leaves Chrome's file untouched. If Dia already has a different manifest, the helper makes a timestamped backup alongside it before replacing it. Re-running it when the destination is already correct makes no change.

Quit and reopen Dia after installation.

## Grant the extension permission

1. In Dia, open the Bitwarden extension and unlock it if necessary. Keep Bitwarden Desktop open and unlocked.
2. Open the Bitwarden popup page in a **normal Dia tab**. The URL is printed by `install_host.py`; for the Chrome Web Store extension it is usually:

   ```text
   chrome-extension://nngceckbapebfimnlniiiahkandclblb/popup/index.html#/account-security
   ```

3. Open that tab's Developer Tools (`Option-Command-I`) and select **Console**.
4. Paste the contents of [`request-permission.js`](request-permission.js) into the Console and press Enter. It adds a temporary yellow button to this tab. Review the snippet before pasting.
5. Click **Request Bitwarden nativeMessaging permission**. Dia should show a browser permission prompt. Check that it names **Bitwarden Password Manager**, then choose **Allow** if you want this integration.
6. The Console should print `Permission granted: true`. Close or reload the tab to remove the temporary button. The permission itself is saved by Dia.
7. In Bitwarden's normal extension popup, open **Settings → Account security → Unlock with biometrics**. Complete any Bitwarden Desktop confirmation and Touch ID prompt. Finally, lock the extension and verify that Touch ID unlocks it.

The script cannot grant browser permissions: the request must come from the extension page after a user click, and the browser's approval belongs to you. [Chrome's permission API documentation](https://developer.chrome.com/docs/extensions/reference/api/permissions) describes this runtime flow.

## Troubleshooting

- If no browser prompt appears in the normal tab, confirm the tab URL begins with `chrome-extension://` and belongs to Bitwarden; the Console snippet refuses other extension IDs.
- If Dia grants permission but Bitwarden cannot find Desktop, check that `com.8bit.bitwarden.json` exists in Dia's `NativeMessagingHosts` directory, its `path` is an executable `desktop_proxy`, and Desktop is running.
- If the helper reports an unexpected extension ID, stop and verify where that extension came from. This guide supports the official Chrome Web Store build.
- If Bitwarden asks for the permission again after an extension reinstall or profile change, run the helper again and repeat the permission step in the affected Dia profile.
- To undo the host installation, restore the timestamped backup if one was made; otherwise remove only Dia's `com.8bit.bitwarden.json`. Dia's extension permission can be removed by uninstalling the extension from the affected profile.

## Related issue

[Bitwarden issue #14274](https://github.com/bitwarden/clients/issues/14274) reported Dia biometric unlock failures in 2025. The issue is closed, but the permission request from the pop-out window still stalled in the environment tested here. The [bug report draft](BUG_REPORT.md) contains the reproduction details.
