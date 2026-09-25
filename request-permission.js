// Run only in the DevTools Console of Bitwarden's extension page in a normal Dia tab.
// This button and script exist only until this page is closed or reloaded.
(() => {
  const expectedId = "nngceckbapebfimnlniiiahkandclblb";
  if (location.protocol !== "chrome-extension:" || chrome.runtime.id !== expectedId) {
    throw new Error("Open the official Bitwarden extension page before running this snippet.");
  }

  if (document.getElementById("dia-bitwarden-permission-button")) return;

  const button = document.createElement("button");
  button.id = "dia-bitwarden-permission-button";
  button.textContent = "Request Bitwarden nativeMessaging permission";
  button.style.cssText =
    "position:fixed;z-index:2147483647;top:8px;right:8px;padding:12px;background:#ffbf00;color:#000;border:1px solid #000;border-radius:6px;cursor:pointer";
  button.addEventListener("click", () => {
    chrome.permissions.request({ permissions: ["nativeMessaging"] }, (granted) => {
      const error = chrome.runtime.lastError?.message;
      console.log("Permission granted:", granted, error ? `Error: ${error}` : "");
      button.textContent = granted ? "Permission granted" : "Permission not granted; retry";
    });
  });
  document.body.appendChild(button);
})();
