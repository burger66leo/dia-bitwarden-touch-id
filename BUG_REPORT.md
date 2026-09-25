# Bug report draft for Dia

**Title:** `chrome.permissions.request({permissions:["nativeMessaging"]})` hangs in a Bitwarden pop-out window, but works in a normal Dia tab

## Environment

- macOS 27.0
- Dia 1.50.1
- Bitwarden Desktop 2026.9.0
- Bitwarden Password Manager extension 2026.9.2 (`nngceckbapebfimnlniiiahkandclblb`)

## Steps to reproduce

1. Install Bitwarden Desktop and the official Bitwarden extension in Dia. Enable Touch ID in Desktop and keep it running and unlocked.
2. Open the extension, go to **Settings → Account security**, and enable **Unlock with biometrics**.
3. Bitwarden opens a pop-out window with **New permission needed**. Click **Continue**.

## Expected result

Dia displays a permission prompt allowing the Bitwarden extension to communicate with native applications. After the user chooses **Allow**, the permission request calls back with `true` and setup can continue.

## Actual result

No Dia permission prompt appears. The Bitwarden dialog stays open. Its call to `chrome.permissions.request({permissions:["nativeMessaging"]})` is reached with a valid user activation, but its callback never runs. `chrome.permissions.contains({permissions:["nativeMessaging"]})` remains `false`. The same permission prompt does appear in Google Chrome.

## Workaround verified

Open the Bitwarden extension page in a **normal Dia tab** and attach a button whose click handler calls `chrome.permissions.request({permissions:["nativeMessaging"]}, callback)`. With a user click, Dia displays its permission prompt, and after **Allow** the callback returns `true`. Dia then persists `nativeMessaging` for the extension. With Bitwarden's native messaging host manifest installed in Dia's `NativeMessagingHosts` directory, biometric unlock works after completing Bitwarden Desktop confirmation.

This points to the permission prompt handling for the Bitwarden pop-out window, rather than a missing `chrome.permissions` API or a missing host manifest. It does not identify the exact failing code inside Dia.

Related: bitwarden/clients#14274 (closed): https://github.com/bitwarden/clients/issues/14274

## Suggested fix

Please ensure runtime optional permission requests initiated from extension pop-out windows display the browser permission prompt and always resolve the callback after the user allows or denies it.
