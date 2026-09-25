# 在 macOS 的 Dia 使用 Bitwarden Touch ID

**语言：**[English](README.md) · [繁體中文](README.zh-Hant.md) · 简体中文

这是一个社区提供的替代方法，让 Dia 中的官方 Bitwarden 浏览器扩展通过 Bitwarden Desktop 使用 Touch ID 解锁。已在 **macOS 27.0、Dia 1.50.1、Bitwarden Desktop 2026.9.0、Bitwarden 扩展 2026.9.2** 验证；其他版本可能需要调整。

方法分为两部分：

1. 在 Dia 的浏览器目录安装 Bitwarden Native Messaging 主机清单，让 Dia 知道 Bitwarden Desktop 的 `desktop_proxy` 在哪里。
2. 从**普通 Dia 标签页**请求扩展的可选权限 `nativeMessaging`。在上述版本中，Bitwarden 从自动打开的独立窗口发出请求时，Dia 没有显示权限提示，也没有返回结果；从普通标签页发出同样的请求则可以成功。

**浏览器权限提示仍须由你亲自检查并同意。** 此方法不会修改 Dia 程序或 Bitwarden 扩展本身。

## 开始之前

需要具备：

- macOS 上已安装 Dia、Bitwarden Desktop，以及从 **Chrome 网上应用店**安装到 Dia 的官方 Bitwarden Password Manager 扩展。
- Bitwarden Desktop 已启用 Touch ID，且 Touch ID 可以正常解锁。设置期间请让桌面版保持运行、登录并解锁。
- Chrome 的 Bitwarden 主机清单已存在于 `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.8bit.bitwarden.json`。辅助程序会以它为来源，不会修改它。
- 终端可以运行 `python3`。

辅助程序只接受官方扩展 ID `nngceckbapebfimnlniiiahkandclblb`。它会在 Dia 中查找已安装的 ID、核对扩展的本地化名称；即使其他扩展使用相同名称，只要 ID 不同也会被拒绝。

## 快速设置

### 1. 检查本机安装状态

在终端切换到此仓库目录，运行：

```sh
python3 install_host.py
```

这是**只读检查**。它会列出找到的 Dia 应用、数据目录、Bitwarden 扩展 ID、Chrome 清单来源、Dia 清单目标、桌面代理，以及稍后要打开的扩展网址。如果看到 `already correct`，可以跳过下一个命令。

如果看到 `installation needed`，运行：

```sh
python3 install_host.py --apply
```

辅助程序会验证 JSON 和代理程序，按需创建 Dia 的 `NativeMessagingHosts` 目录，并写入 `com.8bit.bitwarden.json`。如果 Dia 原本已有内容不同的清单，会**先**在同一目录建立带时间戳的 `.backup-*` 备份，再替换目标。内容相同时重复运行不会修改文件；Chrome 的来源文件始终不会被编辑。

清单有变化后，请**完全退出 Dia，再重新打开**。

### 2. 从普通 Dia 标签页请求权限

1. 如有需要，先在 Dia 解锁 Bitwarden 扩展。请保持 Bitwarden Desktop 打开并解锁。
2. 在**普通 Dia 标签页**打开扩展的账户安全页面；不要使用工具栏的小弹窗或自动打开的独立窗口。使用辅助程序列出的网址。官方扩展通常是：

   ```text
   chrome-extension://nngceckbapebfimnlniiiahkandclblb/popup/index.html#/account-security
   ```

3. 切到该标签页，按 **Option-Command-I** 打开开发者工具，选择 **Console**。
4. 先阅读 [`request-permission.js`](request-permission.js)，再把完整内容粘贴到 Console 并按 Enter。页面会出现黄色的 **Request Bitwarden nativeMessaging permission** 按钮。代码片段在执行前会检查扩展 ID。
5. 点击黄色按钮。浏览器权限 API 需要这次真正的用户点击。Dia 应显示 **Bitwarden Password Manager** 请求额外权限的提示。核对扩展名称后，如果你同意让它与本机应用通信，选择 **Allow**。
6. Console 应显示 `Permission granted: true`。关闭测试标签页，临时按钮就会消失；Dia 会在该配置文件保存权限。

终端辅助程序不能代替这一步。权限必须由扩展页面发起，并在 Dia 自己的界面中由你同意。可参阅 [Chrome 的运行时权限 API 文档](https://developer.chrome.com/docs/extensions/reference/api/permissions)。

### 3. 完成 Bitwarden 设置并验证

1. 在 Dia 打开 Bitwarden 的普通扩展弹窗。
2. 进入 **Settings → Account security → Unlock with biometrics**，完成 Bitwarden Desktop 的确认和 Touch ID 提示。如果扩展在设置期间锁定，先解锁，再重试该选项。
3. 锁定扩展，然后使用 **Unlock with biometrics**。实际通过 Touch ID 成功解锁才算完整验证；仅看到浏览器权限已授予，还不能证明桌面版配对成功。

## 辅助程序会改动什么

| 项目 | 行为 |
| --- | --- |
| Chrome 的 `com.8bit.bitwarden.json` | 只读取 |
| Dia 的 `NativeMessagingHosts/com.8bit.bitwarden.json` | 使用 `--apply` 时创建或替换 |
| Dia 原有的主机清单 | 替换前在同一目录备份 |
| Dia 的扩展权限 | 只能在你点击后，通过 Dia 的提示授予 |
| Bitwarden 密码库、扩展文件、浏览器 `Secure Preferences` | 辅助程序不读取或修改 |

辅助程序会复制 Chrome 清单的字段；只有当 Dia 中找到的 Bitwarden 扩展来源未列于 `allowed_origins` 时才补上。它还会确认清单指向可执行的 `desktop_proxy`。它**不会**复制 Chrome 的扩展授权状态：权限属于各浏览器配置文件。

安装位置不标准时，可运行 `python3 install_host.py --help` 查看 `--dia-app`、`--dia-data` 和 `--chrome-manifest`。使用 `--apply` 前请仔细核对路径。

## 故障排查

| 情况 | 检查方法 |
| --- | --- |
| `No installed Bitwarden extension was found` | 先在 Dia 安装官方扩展，再重新检查。 |
| `unexpected ID` | 停下来确认扩展来源。本指南只支持官方 Chrome 网上应用店的 ID。 |
| 找不到 Chrome 清单或 `desktop_proxy` | 打开 Bitwarden Desktop，确认其浏览器集成已安装 Chrome 清单。辅助程序需要有效的 Chrome 来源。 |
| Dia 仍不显示权限提示 | 确认网址以 `chrome-extension://` 开头，而且打开在**普通标签页**。在该标签页 Console 运行代码片段，再点击黄色按钮；直接在 Console 粘贴 `chrome.permissions.request(...)` 不会提供所需的用户点击。 |
| Console 显示 `Permission granted: false` | 重试并核对提示上的选择。不要编辑 `Secure Preferences` 强行授权。 |
| 已授权但找不到 Desktop | 检查 Dia 主机清单是否存在、`path` 是否指向可执行的 `desktop_proxy`，以及桌面版是否运行且已解锁。修改清单后请完全重启 Dia。 |
| 一个 Dia 配置文件成功，另一个不行 | 浏览器权限按配置文件保存。请在出问题的配置文件重新执行标签页授权步骤。 |

## 还原主机清单

辅助程序唯一的持久文件改动是 Dia 的 `com.8bit.bitwarden.json`。

- 如果辅助程序列出备份路径，完全退出 Dia 后，将**该备份**还原为 Dia 的 `NativeMessagingHosts/com.8bit.bitwarden.json`。
- 如果安装前 Dia 没有此主机清单，完全退出 Dia 后，只移除 Dia 的 `com.8bit.bitwarden.json`。
- 重新打开 Dia。不要删除 Bitwarden 密码库文件、Chrome 来源清单或浏览器配置文件。

`nativeMessaging` 权限另由 Dia 保存在对应配置文件。辅助程序不会改动该权限；还原主机清单也不会撤销它。

## 为什么这只是替代方法

在验证环境中，Bitwarden 独立窗口已在有效的用户点击下调用 `chrome.permissions.request({ permissions: ["nativeMessaging"] })`，但 Dia 未显示权限提示，也未调用回调。普通标签页上的按钮调用**相同 API**，用户同意后 Dia 返回 `true`。这将观察到的问题缩小到 Dia 对该窗口／请求流程的处理；我们尚未定位 Dia 内部的确切代码。

[Bitwarden issue #14274](https://github.com/bitwarden/clients/issues/14274) 在 2025 年报告过 Dia 的生物识别解锁失效，该 issue 已关闭。简短的复现报告见 [`BUG_REPORT.md`](BUG_REPORT.md)。
