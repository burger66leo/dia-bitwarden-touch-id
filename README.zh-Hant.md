# 在 macOS 的 Dia 使用 Bitwarden Touch ID

**語言：**[English](README.md) · 繁體中文 · [简体中文](README.zh-Hans.md)

這是一個社群提供的替代做法，讓 Dia 中的官方 Bitwarden 瀏覽器擴充套件透過 Bitwarden Desktop 使用 Touch ID 解鎖。已在 **macOS 27.0、Dia 1.50.1、Bitwarden Desktop 2026.9.0、Bitwarden 擴充套件 2026.9.2** 驗證；其他版本可能需要調整。

做法分成兩部分：

1. 在 Dia 的瀏覽器目錄安裝 Bitwarden Native Messaging 主機清單，讓 Dia 知道 Bitwarden Desktop 的 `desktop_proxy` 在哪裡。
2. 從**一般 Dia 分頁**要求擴充套件的選用權限 `nativeMessaging`。在上述版本中，Bitwarden 從自動開啟的獨立視窗提出請求時，Dia 沒有顯示權限提示，也沒有回傳結果；從一般分頁提出同樣請求則能成功。

**瀏覽器的權限提示仍須由你親自檢查並同意。** 此方法不會修改 Dia 程式或 Bitwarden 擴充套件本身。

## 開始之前

需要具備：

- macOS 上已安裝 Dia、Bitwarden Desktop，以及從 **Chrome 線上應用程式商店**安裝到 Dia 的官方 Bitwarden Password Manager 擴充套件。
- Bitwarden Desktop 已啟用 Touch ID，且 Touch ID 能正常解鎖。設定期間請讓桌面版保持執行、登入並解鎖。
- Chrome 的 Bitwarden 主機清單已存在於 `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.8bit.bitwarden.json`。輔助程式會以它為來源，不會修改它。
- 終端機可執行 `python3`。

輔助程式只接受官方擴充套件 ID `nngceckbapebfimnlniiiahkandclblb`。它會在 Dia 中尋找已安裝的 ID、核對擴充套件的本地化名稱；即使其他擴充套件使用相同名稱，只要 ID 不同也會拒絕。

## 快速設定

### 1. 檢查本機安裝狀態

在終端機切換到此儲存庫目錄，執行：

```sh
python3 install_host.py
```

這是**唯讀檢查**。它會列出找到的 Dia 應用程式、資料目錄、Bitwarden 擴充套件 ID、Chrome 清單來源、Dia 清單目標、桌面代理，以及稍後要開啟的擴充套件網址。如果看到 `already correct`，可以跳過下一個指令。

如果看到 `installation needed`，執行：

```sh
python3 install_host.py --apply
```

輔助程式會驗證 JSON 和代理程式，視需要建立 Dia 的 `NativeMessagingHosts` 目錄，並寫入 `com.8bit.bitwarden.json`。如果 Dia 原本已有不同內容的清單，會**先**在同一目錄建立帶時間戳記的 `.backup-*` 備份，再取代目標。內容相同時重複執行不會修改檔案；Chrome 的來源檔案永遠不會被編輯。

清單有變動後，請**完全結束 Dia，再重新開啟**。

### 2. 從一般 Dia 分頁要求權限

1. 如有需要，先在 Dia 解鎖 Bitwarden 擴充套件。Bitwarden Desktop 請保持開啟並解鎖。
2. 在**一般 Dia 分頁**開啟擴充套件的帳戶安全頁面；不要使用工具列的小彈窗或自動開啟的獨立視窗。使用輔助程式列出的網址。官方擴充套件通常是：

   ```text
   chrome-extension://nngceckbapebfimnlniiiahkandclblb/popup/index.html#/account-security
   ```

3. 切到該分頁，按 **Option-Command-I** 開啟開發者工具，選擇 **Console**。
4. 先閱讀 [`request-permission.js`](request-permission.js)，再把完整內容貼進 Console 並按 Enter。頁面會出現黃色的 **Request Bitwarden nativeMessaging permission** 按鈕。片段在執行前會檢查擴充套件 ID。
5. 點擊黃色按鈕。瀏覽器權限 API 需要這次真正的使用者點擊。Dia 應顯示 **Bitwarden Password Manager** 要求額外權限的提示。核對擴充套件名稱後，若你同意讓它與本機應用程式通信，選擇 **Allow**。
6. Console 應顯示 `Permission granted: true`。關閉測試分頁，暫時按鈕便會消失；Dia 會在該設定檔保存權限。

終端機輔助程式無法代替這一步。權限必須由擴充套件頁面提出，並在 Dia 自己的介面中由你同意。可參閱 [Chrome 的執行階段權限 API 文件](https://developer.chrome.com/docs/extensions/reference/api/permissions)。

### 3. 完成 Bitwarden 設定並驗證

1. 在 Dia 開啟 Bitwarden 的一般擴充套件彈窗。
2. 進入 **Settings → Account security → Unlock with biometrics**，完成 Bitwarden Desktop 的確認及 Touch ID 提示。如擴充套件在設定期間鎖定，先解鎖，再重試該選項。
3. 鎖定擴充套件，接著使用 **Unlock with biometrics**。實際以 Touch ID 成功解鎖才算完整驗證；僅看到瀏覽器權限已授予，還不能證明桌面版配對成功。

## 輔助程式會改動什麼

| 項目 | 行為 |
| --- | --- |
| Chrome 的 `com.8bit.bitwarden.json` | 只讀取 |
| Dia 的 `NativeMessagingHosts/com.8bit.bitwarden.json` | 使用 `--apply` 時建立或取代 |
| Dia 原有的主機清單 | 取代前在同一目錄備份 |
| Dia 的擴充套件權限 | 只能在你點擊後，透過 Dia 的提示授予 |
| Bitwarden 密碼庫、擴充套件檔案、瀏覽器 `Secure Preferences` | 輔助程式不讀取或修改 |

輔助程式會複製 Chrome 清單的欄位；只有當 Dia 中找到的 Bitwarden 擴充套件來源未列於 `allowed_origins` 時才補上。它也會確認清單指向可執行的 `desktop_proxy`。它**不會**複製 Chrome 的擴充套件授權狀態：權限屬於各瀏覽器設定檔。

安裝位置不標準時，可執行 `python3 install_host.py --help` 查看 `--dia-app`、`--dia-data` 和 `--chrome-manifest`。使用 `--apply` 前請仔細核對路徑。

## 疑難排解

| 狀況 | 檢查方式 |
| --- | --- |
| `No installed Bitwarden extension was found` | 先在 Dia 安裝官方擴充套件，再重新檢查。 |
| `unexpected ID` | 停下來確認擴充套件來源。本指南只支援官方 Chrome 線上應用程式商店的 ID。 |
| 找不到 Chrome 清單或 `desktop_proxy` | 開啟 Bitwarden Desktop，確認其瀏覽器整合已安裝 Chrome 清單。輔助程式需要有效的 Chrome 來源。 |
| Dia 仍不顯示權限提示 | 確認網址以 `chrome-extension://` 開頭，而且開在**一般分頁**。在該分頁 Console 執行片段，再點擊黃色按鈕；直接在 Console 貼上 `chrome.permissions.request(...)` 不會提供所需的使用者點擊。 |
| Console 顯示 `Permission granted: false` | 重試並核對提示上的選擇。不要編輯 `Secure Preferences` 強行授權。 |
| 已授權但找不到 Desktop | 檢查 Dia 主機清單是否存在、`path` 是否指向可執行的 `desktop_proxy`，以及桌面版是否執行且已解鎖。變更清單後請完全重啟 Dia。 |
| 一個 Dia 設定檔成功，另一個不行 | 瀏覽器權限按設定檔儲存。請在出問題的設定檔重新執行分頁授權步驟。 |

## 還原主機清單

輔助程式唯一的持久檔案變更是 Dia 的 `com.8bit.bitwarden.json`。

- 如果輔助程式列出備份路徑，完全結束 Dia 後，將**該備份**還原為 Dia 的 `NativeMessagingHosts/com.8bit.bitwarden.json`。
- 如果安裝前 Dia 沒有此主機清單，完全結束 Dia 後，只移除 Dia 的 `com.8bit.bitwarden.json`。
- 重新開啟 Dia。不要刪除 Bitwarden 密碼庫檔案、Chrome 來源清單或瀏覽器設定檔。

`nativeMessaging` 權限另由 Dia 保存在對應設定檔。輔助程式不會更動該權限；還原主機清單也不會撤銷它。

## 為什麼這只是替代做法

在驗證環境中，Bitwarden 獨立視窗已於有效的使用者點擊下呼叫 `chrome.permissions.request({ permissions: ["nativeMessaging"] })`，但 Dia 未顯示權限提示，也未呼叫回調。一般分頁上的按鈕呼叫**相同 API**，使用者同意後 Dia 回傳 `true`。這將觀察到的問題縮小到 Dia 對該視窗／請求流程的處理；我們尚未定位 Dia 內部的確切程式碼。

[Bitwarden issue #14274](https://github.com/bitwarden/clients/issues/14274) 在 2025 年回報過 Dia 的生物識別解鎖失效，該 issue 已關閉。簡短的重現報告見 [`BUG_REPORT.md`](BUG_REPORT.md)。
