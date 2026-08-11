# TailRocket

TailRocket 是一个由 GitHub Actions 自动构建的 Shadowrocket 完整配置：跟踪 Johnshall 上游规则，同时保留 IPv4 Tailscale 分流、IPv6 优先、系统 DNS 和个人代理规则。

仓库不包含代理节点、订阅地址、Tailnet 身份或任何凭据；Finance/Payment 规则只决定流量进入你当前选择的 `PROXY` 策略，实际隐私和出口取决于该策略对应的节点。

## 已验证的 Tailscale 处理

配置只对 Tailscale IPv4 做最小处理：

- 从 `bypass-tun` 和 `tun-excluded-routes` 移除 `100.64.0.0/10`；
- 在 `[Rule]` 最前面加入 `IP-CIDR,100.64.0.0/10,TAILSCALE,no-resolve`；
- 不设置 `tun-included-routes`；
- 不强制 DERP、Tailscale IPv6 路由或 `*.ts.net`。

手机 SSH 的实际验证路径是：`Termius → 100.x Tailscale 地址 → Shadowrocket TAILSCALE → Windows OpenSSH`。历史上的 TCP timeout 直接原因是 Windows 当时没有运行 `sshd`；这不是本仓库能够替代的 Windows 服务安装步骤。

## 默认网络设置

```ini
ipv6 = true
prefer-ipv6 = true
dns-server = system
```

也就是启用 IPv6、优先 IPv6，并使用 iOS/当前网络提供的系统 DNS。IPv6 优先不是速度保证；如果你的代理节点或目标站点 IPv6 路径质量较差，应在本地测试后再调整。

## 个人规则

`custom_rules.conf` 会被插入生成配置的 `[Rule]` 顶部，当前包含：

- Travel/Booking：Booking、Agoda、Expedia、Airbnb、Trip、Skyscanner、Klook 等；
- Finance/Payment：Schwab、IBKR、TradingView、Bloomberg、PayPal、Wise 等；
- Shopping：Amazon、eBay、Walmart、Best Buy 等。

以后只编辑 `custom_rules.conf`，不要手改 `sr_top500_custom.conf`；下一次 Action 运行会重新生成完整文件。

## 使用方式

1. 将本仓库设为 GitHub Public，默认分支使用 `main`。
2. 在 **Actions → Update Shadowrocket custom config → Run workflow** 手动运行一次。
3. 等 Action 提交生成文件后，在 Shadowrocket 的配置订阅中使用：

   `https://raw.githubusercontent.com/YOUR_OWNER/YOUR_REPO/main/sr_top500_custom.conf`

4. 以后订阅这个地址即可；Action 每 6 小时检查上游，有变化才提交。

生成文件中的 `update-url` 会由 Action 自动写成当前仓库地址，初始 ZIP 中的 `OWNER/REPO` 只是占位符。若组织策略禁止 GitHub Actions 写入仓库，请在仓库的 Actions 设置中允许 `Read and write permissions`，或改用具备同等权限的工作流策略。

## 上游与许可

生成配置衍生自 [Johnshall/Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever) 的 `release` 分支，并保留其来源说明。上游项目声明采用 [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)，因此规则、生成配置和相关文档按 CC BY-SA 4.0 发布。

本仓库原创的 Python 自动化脚本按 MIT 发布，详见 [`LICENSE-MIT`](LICENSE-MIT) 和 [`LICENSES/CC-BY-SA-4.0.txt`](LICENSES/CC-BY-SA-4.0.txt)。

Johnshall 的规则是纯文本分流/过滤规则，不提供代理服务或翻墙能力；使用前请确认上游规则和你所选代理节点符合当地法律及服务条款。
