# TailRocket

[![Update TailRocket profiles](https://github.com/Seanyim/tailrocket/actions/workflows/update-shadowrocket.yml/badge.svg)](https://github.com/Seanyim/tailrocket/actions/workflows/update-shadowrocket.yml)
[![License: MIT](https://img.shields.io/badge/automation-MIT-blue.svg)](LICENSE-MIT)
[![Rules: CC BY-SA 4.0](https://img.shields.io/badge/rules-CC%20BY--SA%204.0-lightgrey.svg)](LICENSES/CC-BY-SA-4.0.txt)

TailRocket 是一组面向 Shadowrocket 的自动更新配置。它以 [Johnshall/Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever) 的 `release` 分支为上游，在保留每个配置原本用途的前提下，提供：

- 已验证的 Tailscale IPv4 最小分流；
- IPv6 开启并优先使用 IPv6；
- 使用系统 DNS；
- Travel、Finance、Shopping 个人规则（仅在适合的出海配置中启用）；
- GitHub Actions 每 6 小时安全重建；
- GitHub Pages 网页订阅和 GitHub Raw 备用订阅。

TailRocket 只提供 Shadowrocket 规则和配置文本，不提供代理节点、订阅服务、Tailscale 设备或 SSH 服务。

## 先用起来：直接粘贴网页订阅地址

不需要先下载 `.conf` 文件。推荐在 Shadowrocket 中直接添加网页地址：

1. 打开 Shadowrocket，进入 **配置**；
2. 点击右上角 **+**；
3. 将下面的 Pages 地址粘贴到 URL；
4. 点击下载，选中刚下载的配置并启用。

如果在 Safari 中打开地址后看到的是纯文本，这是正常的；复制完整地址到 Shadowrocket 即可。Pages 暂时不可用时，可以使用同一行的 Raw 地址。

### 推荐配置

最适合作为普通出海规则起点的是无广告版黑名单配置：

- Pages：<https://seanyim.github.io/tailrocket/profiles/sr_top500_banlist.conf>
- Raw：<https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_top500_banlist.conf>

保留旧版兼容地址的用户可以继续使用：

- Pages：<https://seanyim.github.io/tailrocket/sr_top500_custom.conf>
- Raw：<https://raw.githubusercontent.com/Seanyim/tailrocket/main/sr_top500_custom.conf>

## 配置选择表

下面的地址都是可以直接粘贴到 Shadowrocket 的订阅地址。`个人规则` 表示是否加入本仓库的 Travel、Finance、Shopping 规则；所有完整配置都会加入 Tailscale、IPv6、系统 DNS和自更新地址。

| 配置 | 适合场景 | 未匹配请求 | 去广告 | 个人规则 | Pages | Raw |
| --- | --- | --- | --- | --- | --- | --- |
| `sr_top500_banlist.conf` | 推荐的轻量黑名单 | 直连 | 否 | 是 | [订阅](https://seanyim.github.io/tailrocket/profiles/sr_top500_banlist.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_top500_banlist.conf) |
| `sr_top500_banlist_ad.conf` | 黑名单 + 广告过滤 | 直连 | 是 | 是 | [订阅](https://seanyim.github.io/tailrocket/profiles/sr_top500_banlist_ad.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_top500_banlist_ad.conf) |
| `sr_top500_whitelist.conf` | 严格白名单 | 代理 | 否 | 是 | [订阅](https://seanyim.github.io/tailrocket/profiles/sr_top500_whitelist.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_top500_whitelist.conf) |
| `sr_top500_whitelist_ad.conf` | 白名单 + 广告过滤 | 代理 | 是 | 是 | [订阅](https://seanyim.github.io/tailrocket/profiles/sr_top500_whitelist_ad.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_top500_whitelist_ad.conf) |
| `sr_cnip.conf` | 中国直连、海外代理 | 代理 | 否 | 是 | [订阅](https://seanyim.github.io/tailrocket/profiles/sr_cnip.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_cnip.conf) |
| `sr_cnip_ad.conf` | 中国直连、海外代理 + 广告过滤 | 代理 | 是 | 是 | [订阅](https://seanyim.github.io/tailrocket/profiles/sr_cnip_ad.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_cnip_ad.conf) |
| `sr_proxy_banad.conf` | 全局代理 + 广告过滤 | 代理 | 是 | 是 | [订阅](https://seanyim.github.io/tailrocket/profiles/sr_proxy_banad.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_proxy_banad.conf) |
| `sr_direct_banad.conf` | 全局直连，仅过滤广告 | 直连 | 是 | 否 | [订阅](https://seanyim.github.io/tailrocket/profiles/sr_direct_banad.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_direct_banad.conf) |
| `sr_backcn.conf` | 海外使用，访问中国服务 | 直连 | 否 | 否 | [订阅](https://seanyim.github.io/tailrocket/profiles/sr_backcn.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_backcn.conf) |
| `sr_backcn_ad.conf` | 回国 + 广告过滤 | 直连 | 是 | 否 | [订阅](https://seanyim.github.io/tailrocket/profiles/sr_backcn_ad.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_backcn_ad.conf) |
| `lazy.conf` | 懒人配置 | 代理 | 否 | 是 | [订阅](https://seanyim.github.io/tailrocket/profiles/lazy.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/lazy.conf) |
| `lazy_group.conf` | 懒人配置 + 地区/服务策略组 | 代理 | 否 | 分组适配 | [订阅](https://seanyim.github.io/tailrocket/profiles/lazy_group.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/lazy_group.conf) |
| `sr_adb.conf` | 上游旧版黑名单兼容 | 直连 | 是 | 是 | [订阅](https://seanyim.github.io/tailrocket/profiles/sr_adb.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_adb.conf) |
| `sr_ad_only.conf` | 与其他配置组合的广告片段 | 不适用 | 是 | 否 | [订阅](https://seanyim.github.io/tailrocket/profiles/sr_ad_only.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_ad_only.conf) |

### 如何选择

- 不确定时，先用 `sr_top500_banlist.conf`；它对未知网站默认直连，通常比白名单更容易开始排查。
- 想过滤 App 和网页广告，选择同名的 `_ad` 版本，但广告过滤不保证百分之百覆盖，尤其是视频广告。
- 想让未知海外网站也走代理，选择 `sr_top500_whitelist.conf` 或 `_ad` 版本。
- 只想把中国网站直连、其他网站交给代理，选择 `sr_cnip.conf` 或 `_ad` 版本。
- 海外访问中国服务，选择 `sr_backcn.conf` 或 `_ad` 版本；这两份不会加入个人出海代理规则，以免改变“回国”用途。
- `sr_ad_only.conf` 没有 `[General]`，不能单独承担 Tailscale、IPv6 或 DNS 设置，只能作为规则片段组合使用。

## TailRocket 做了什么

### Tailscale：只处理 IPv4 的最小路由

完整配置会执行以下三件事：

```ini
ipv6 = true
prefer-ipv6 = true
dns-server = system
```

并在 `[Rule]` 顶部加入且只加入一次：

```ini
IP-CIDR,100.64.0.0/10,TAILSCALE,no-resolve
```

同时从 `bypass-tun` 或 `tun-excluded-routes` 删除 `100.64.0.0/10`，删除 `tun-included-routes`。TailRocket 不强制 DERP，不添加 Tailscale IPv6 路由，不匹配 `*.ts.net`，也不写入任何真实 Tailnet 地址或设备名。

IPv6 优先不是速度保证。如果你的代理节点或目标网站 IPv6 路径质量不好，请在本地测试后再决定是否关闭。

### 个人规则

适合出海的配置会在上游规则前加入：

- Travel/Booking：Booking、Agoda、Expedia、Airbnb、Trip、Skyscanner、Klook 等；
- Finance/Payment：Schwab、IBKR、Fidelity、TradingView、Bloomberg、PayPal、Wise 等；
- Shopping：Amazon、eBay、Walmart、Best Buy、Target、Costco 等。

这些规则只决定流量进入哪个策略。Finance/Payment 流量最终经过哪个国家或地区的出口，取决于你在 Shadowrocket 中选择的 `PROXY` 节点；本仓库不提供节点，也不保证某个金融服务一定允许某个出口地区。

`lazy_group.conf` 会保留上游的 `PayPal` 和 `Amazon` 策略组：PayPal/Amazon 域名使用对应组，其他个人域名使用 `PROXY`。回国和全直连配置不插入这些个人强制代理规则，因为那会改变配置的核心用途。

## 自动更新是怎样工作的

```text
Johnshall release 分支
          │
          ▼
GitHub Actions 每 6 小时检查 14 个上游配置
          │
          ▼
清单校验 → 下载重试 → 逐份增强 → 全部验证
          │                         │
          │ 任一份失败              │ 全部通过且有变化
          ▼                         ▼
保留旧成品并报错              一次提交全部 profiles
                                    │
                                    ▼
                         GitHub Pages + GitHub Raw
```

服务器端自动更新和 Shadowrocket 客户端刷新是两件事：

1. GitHub Actions 负责更新仓库中的配置文件；
2. Shadowrocket 需要重新刷新远程配置，或者使用客户端自身的自动更新功能（具体开关名称随版本可能不同）。

每份完整配置的 `update-url` 会指向对应的 Pages 地址。若 Pages 刚启用或刚发布更新，先等待 GitHub Pages 完成部署；Raw 地址可以作为即时备用。

仓库更新失败时不会覆盖上一版成品。上游新增、删除或改名配置也会让工作流失败，等待人工确认其语义后再加入清单。

## 自定义规则

只编辑 [`custom_rules.conf`](custom_rules.conf)，不要直接编辑 `profiles/*.conf` 或 `sr_top500_custom.conf`。下一次工作流会从上游重新下载并覆盖生成文件。

规则写法使用 Shadowrocket 格式，例如：

```ini
DOMAIN-SUFFIX,example.com,PROXY
DOMAIN-SUFFIX,internal.example,DIRECT
```

不要把真实节点、订阅地址、Tailnet 地址、设备名、账号或密码提交到 Public 仓库。Tailscale 规则由构建器统一插入，不需要手动加入 `custom_rules.conf`。

## Windows SSH 与 Tailscale 的边界

手机 SSH 成功验证的路径是：

```text
Termius → Windows 的 100.x Tailscale 地址
       → Shadowrocket 的 TAILSCALE 规则
       → Windows OpenSSH Server
```

历史上的 TCP 22 timeout 直接原因是 Windows 没有运行 `sshd`，不是 Tailscale 设备列表或本仓库规则本身。若手机能 ping 通但 SSH 仍失败，请先在 Windows 上确认 OpenSSH Server 服务正在运行并监听 TCP 22。

## 故障排查

### Shadowrocket 提示下载失败或 404

- 确认复制的是完整 Pages/Raw URL，而不是 GitHub 的 HTML 页面地址；
- Pages 刚启用时等待几分钟；
- 临时改用同一行的 Raw 地址；
- 确认代理节点能够访问 GitHub。

### Tailscale 能看到设备，但 SSH timeout

- 先确认 Windows 上 `sshd` 服务存在并运行；
- 确认 Windows 本机 `127.0.0.1:22` 正在监听；
- 再检查 Windows 防火墙入站规则；
- 最后检查 Shadowrocket 是否启用了当前配置及 Tailscale 策略。

### Finance 或购物网站仍然无法访问

- 查看 Shadowrocket 日志，确认请求命中了相应域名规则；
- 检查当前 `PROXY` 策略实际选择的节点；
- 某些服务会限制出口地区、风控或账号登录环境，本仓库不绕过这些限制。

### 广告没有完全消失

广告规则来自上游并会持续更新，但无法保证百分之百过滤。视频广告、App 内置广告和每次升级后更换域名的广告尤其可能漏过。

## 上游、许可与归属

规则和生成配置衍生自 [Johnshall/Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever) 的 `release` 分支，并保留其来源说明。上游构建使用了 [gfwlist](https://github.com/gfwlist/gfwlist)、[Loyalsoldier/cn-blocked-domain](https://github.com/Loyalsoldier/cn-blocked-domain)、[blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script) 和 [LOWERTOP/Shadowrocket](https://github.com/LOWERTOP/Shadowrocket) 等项目。

许可映射如下：

| 内容 | 许可 |
| --- | --- |
| `scripts/` 中 TailRocket 原创 Python 自动化 | [MIT](LICENSE-MIT) |
| `profiles/`、`sr_top500_custom.conf`、`custom_rules.conf` 和相关文档 | [CC BY-SA 4.0](LICENSES/CC-BY-SA-4.0.txt)，同时保留上游署名 |
| 上游及其引用规则 | 以各上游项目自己的许可和署名要求为准 |

TailRocket 不代表 Johnshall、Shadowrocket、Tailscale 或任何代理服务商。使用前请确认相关规则、代理节点和目标服务符合所在地法律及服务条款。

## 贡献与维护

- 个人域名规则：修改 `custom_rules.conf`；
- 上游配置结构变化：修改 `profiles.json` 中的配置说明和增强模式，并补充测试；
- 生成器修改：更新 `scripts/` 和标准库单元测试；
- 提交前运行：

  ```text
  python -m unittest discover -s tests -v
  ```

工作流会在提交前重新验证上游 14 项清单、sections、终结策略、Tailscale 规则唯一性以及敏感信息边界。
