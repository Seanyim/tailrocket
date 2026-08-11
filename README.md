# TailRocket

[![Update TailRocket profiles](https://github.com/Seanyim/tailrocket/actions/workflows/update-shadowrocket.yml/badge.svg)](https://github.com/Seanyim/tailrocket/actions/workflows/update-shadowrocket.yml)
[![License: MIT](https://img.shields.io/badge/automation-MIT-blue.svg)](LICENSE-MIT)
[![Rules: CC BY-SA 4.0](https://img.shields.io/badge/rules-CC%20BY--SA%204.0-lightgrey.svg)](LICENSES/CC-BY-SA-4.0.txt)

TailRocket 是面向 Shadowrocket 的自动更新配置集合。它跟踪 [Johnshall/Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever) 的 `release` 分支，保留每个上游配置的用途，只增加统一的网络基础设置：

- IPv6 开启并优先使用 IPv6；
- 使用系统 DNS；
- 已验证的 Tailscale IPv4 最小分流；
- GitHub Actions 每 6 小时安全重建；
- GitHub Pages 网页订阅，以及 GitHub Raw 备用地址。

TailRocket 不提供代理节点、订阅服务、Tailscale 设备或 SSH 服务，也不会在上游规则前额外插入一组固定的 Travel、Finance、Payment 或 Shopping 域名。这样可以由配置本身的分流逻辑决定网站走向，避免固定名单过期或误判。

## 直接订阅：不需要下载 conf 文件

Shadowrocket 可以直接读取网页地址。以默认推荐配置为例：

1. 打开 Shadowrocket，进入 **配置**；
2. 点击右上角 **+**；
3. 粘贴下面的 Pages 地址；
4. 点击下载，选中刚下载的配置并启用。

主订阅地址：

<https://seanyim.github.io/tailrocket/profiles/sr_cnip.conf>

如果 Pages 暂时不可用，使用同一配置的 Raw 地址：

<https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_cnip.conf>

在 Safari 或浏览器中打开时看到纯文本是正常现象；这里的地址应粘贴到 Shadowrocket 的配置下载框，而不是当作网页应用打开。

## 不知道选哪个？

默认推荐 `sr_cnip.conf`：命中上游中国规则的请求直连，其余未匹配请求交给最终 `PROXY`。这适合希望中国网站保持直连、遇到海外网站时自动使用代理的场景。

需要同时使用广告过滤时，选择 `sr_cnip_ad.conf`。如果你希望采用黑名单而不是“中国/非中国”划分，再选择 `sr_top500_banlist.conf` 或它的 `_ad` 版本。

## 配置选择表

下表中的 Pages 和 Raw 地址都可以直接粘贴到 Shadowrocket。`最终策略`表示上游配置的 `FINAL` 行；广告列只表示是否包含上游的广告规则。

| 配置 | 适合场景 | 最终策略 | 去广告 | Pages | Raw |
| --- | --- | --- | --- | --- | --- |
| `sr_cnip.conf` | 中国规则直连，其余请求代理（默认推荐） | `PROXY` | 否 | [订阅](https://seanyim.github.io/tailrocket/profiles/sr_cnip.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_cnip.conf) |
| `sr_cnip_ad.conf` | 中国规则直连，其余请求代理 + 广告过滤 | `PROXY` | 是 | [订阅](https://seanyim.github.io/tailrocket/profiles/sr_cnip_ad.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_cnip_ad.conf) |
| `sr_top500_banlist.conf` | 轻量黑名单，未知网站默认直连 | `DIRECT` | 否 | [订阅](https://seanyim.github.io/tailrocket/profiles/sr_top500_banlist.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_top500_banlist.conf) |
| `sr_top500_banlist_ad.conf` | 黑名单分流 + 广告过滤 | `DIRECT` | 是 | [订阅](https://seanyim.github.io/tailrocket/profiles/sr_top500_banlist_ad.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_top500_banlist_ad.conf) |
| `sr_top500_whitelist.conf` | 已知可直连网站直连，未知网站代理 | `PROXY` | 否 | [订阅](https://seanyim.github.io/tailrocket/profiles/sr_top500_whitelist.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_top500_whitelist.conf) |
| `sr_top500_whitelist_ad.conf` | 白名单分流 + 广告过滤 | `PROXY` | 是 | [订阅](https://seanyim.github.io/tailrocket/profiles/sr_top500_whitelist_ad.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_top500_whitelist_ad.conf) |
| `sr_proxy_banad.conf` | 局域网直连，其余请求代理并过滤广告 | `PROXY` | 是 | [订阅](https://seanyim.github.io/tailrocket/profiles/sr_proxy_banad.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_proxy_banad.conf) |
| `sr_direct_banad.conf` | 全部请求直连，仅过滤广告 | `DIRECT` | 是 | [订阅](https://seanyim.github.io/tailrocket/profiles/sr_direct_banad.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_direct_banad.conf) |
| `sr_backcn.conf` | 海外访问中国服务 | `DIRECT` | 否 | [订阅](https://seanyim.github.io/tailrocket/profiles/sr_backcn.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_backcn.conf) |
| `sr_backcn_ad.conf` | 回国分流 + 广告过滤 | `DIRECT` | 是 | [订阅](https://seanyim.github.io/tailrocket/profiles/sr_backcn_ad.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_backcn_ad.conf) |
| `lazy.conf` | 上游懒人常规分流 | `PROXY` | 否 | [订阅](https://seanyim.github.io/tailrocket/profiles/lazy.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/lazy.conf) |
| `lazy_group.conf` | 上游懒人分流 + 地区/服务策略组 | `PROXY` | 否 | [订阅](https://seanyim.github.io/tailrocket/profiles/lazy_group.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/lazy_group.conf) |
| `sr_adb.conf` | 上游旧版黑名单兼容 | `DIRECT` | 是 | [订阅](https://seanyim.github.io/tailrocket/profiles/sr_adb.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_adb.conf) |
| `sr_ad_only.conf` | 与其他配置组合的纯广告规则片段 | 不适用 | 是 | [片段](https://seanyim.github.io/tailrocket/profiles/sr_ad_only.conf) | [备用](https://raw.githubusercontent.com/Seanyim/tailrocket/main/profiles/sr_ad_only.conf) |

### 特殊配置说明

- `lazy_group.conf` 保留上游定义的 PayPal、Amazon 和地区策略组，但 TailRocket 不再强制把任何个人网站映射到这些组。
- `sr_backcn.conf` 和 `sr_backcn_ad.conf` 保留回国语义：适合海外访问中国服务，不会被改造成常规出海配置。
- `sr_direct_banad.conf` 保持全局直连语义。
- `sr_ad_only.conf` 只有 `[Rule]`，不能单独提供 `[General]`、Tailscale、IPv6、DNS 或 `update-url`。
- `sr_adb.conf` 继续发布，但它是上游旧版兼容配置；新用户通常优先考虑 `sr_cnip` 或 `sr_top500_banlist`。

旧版兼容入口仍然可用：

- Pages：<https://seanyim.github.io/tailrocket/sr_top500_custom.conf>
- Raw：<https://raw.githubusercontent.com/Seanyim/tailrocket/main/sr_top500_custom.conf>

该入口只是 `sr_top500_banlist.conf` 的兼容别名，不是另一套规则。

## TailRocket 的统一增强

所有完整配置都会在 `[General]` 中确保：

```ini
ipv6 = true
prefer-ipv6 = true
dns-server = system
```

并从 `bypass-tun`、`tun-excluded-routes` 移除 `100.64.0.0/10`，删除 `tun-included-routes`。在 `[Rule]` 顶部只加入一次：

```ini
IP-CIDR,100.64.0.0/10,TAILSCALE,no-resolve
```

TailRocket 不强制 DERP，不增加 Tailscale IPv6 路由，不匹配 `*.ts.net`，也不写入任何真实 Tailnet 地址、设备名或代理订阅。IPv6 优先是连接偏好，不代表所有节点或网站的 IPv6 路径一定更快。

### 网站显示“网络错误”时

使用 `sr_cnip.conf` 时，网站是否走代理由上游中国规则和最终 `PROXY` 共同决定。它不依赖一份需要人工维护的固定网站名单，因此遇到规则未覆盖的新站点时仍会交给代理。

如果仍然无法连接，优先检查：

1. Shadowrocket 当前是否真的启用了 `sr_cnip` 配置；
2. `PROXY` 策略组是否选择了可用节点；
3. 节点出口地区、DNS、目标网站风控或账号登录环境是否有限制；
4. 在日志中确认请求最终命中了 `PROXY`，而不是被上游规则明确设为 `DIRECT` 或其他策略。

TailRocket 不提供节点，也不保证任意网站允许任意出口地区。

## 自动更新机制

```text
Johnshall release 分支
          │
          ▼
GitHub Actions 每 6 小时检查 14 个 .conf
          │
          ▼
清单校验 → 下载重试 → 统一增强 → 逐份验证
          │                         │
          │ 任一份失败              │ 全部通过且有变化
          ▼                         ▼
保留旧成品并报错              一次提交全部 profiles
                                    │
                                    ▼
                         GitHub Pages + GitHub Raw
```

服务器更新和客户端刷新是两个独立步骤：

1. GitHub Actions 更新仓库中的配置文件；
2. Shadowrocket 需要重新刷新远程配置，或使用客户端自己的自动更新功能。

每份完整配置的 `update-url` 指向对应的 Pages 地址。仓库改名或更换 owner 后，工作流会根据 GitHub 上下文自动生成新的地址，不需要把个人身份写进脚本。

下载、结构校验或上游配置集合检查任一失败时，工作流不会覆盖现有成品。上游新增、删除或改名 `.conf` 也会安全失败，等待人工确认其用途后再更新清单。

## Windows SSH 与 Tailscale 的边界

手机 SSH 已验证的路径是：

```text
Termius → Windows 的 100.x Tailscale 地址
       → Shadowrocket 的 TAILSCALE 规则
       → Windows OpenSSH Server
```

历史 TCP 22 timeout 的直接原因是 Windows 没有运行 `sshd`，不是 Tailscale 设备列表或 TailRocket 配置本身。若手机可以 ping 通但 SSH 仍失败，请先确认 Windows OpenSSH Server 服务存在、正在运行并监听 TCP 22。

## 常见问题

### Shadowrocket 下载失败或 404

- 确认粘贴的是 Pages/Raw 的完整 `.conf` 地址，而不是 GitHub 网页地址；
- Pages 刚启用或刚部署时等待几分钟；
- 临时改用对应 Raw 地址；
- 确认当前代理节点可以访问 GitHub。

### Tailscale 能看到设备，但 SSH timeout

- 确认 Windows 的 `sshd` 服务正在运行；
- 确认 Windows 本机 `127.0.0.1:22` 正在监听；
- 检查 Windows 防火墙入站规则；
- 确认 Shadowrocket 已选中包含 Tailscale 规则的完整配置。

### 广告没有完全消失

广告规则来自上游，无法保证百分之百覆盖。视频广告、App 内置广告和更换域名后的广告尤其可能漏过。

## 上游、许可与归属

规则和生成配置衍生自 [Johnshall/Shadowrocket-ADBlock-Rules-Forever](https://github.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever) 的 `release` 分支，并保留来源说明。上游还引用了 [gfwlist](https://github.com/gfwlist/gfwlist)、[Loyalsoldier/cn-blocked-domain](https://github.com/Loyalsoldier/cn-blocked-domain)、[blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script) 和 [LOWERTOP/Shadowrocket](https://github.com/LOWERTOP/Shadowrocket) 等项目；各自的许可和署名要求以原项目为准。

| 内容 | 许可 |
| --- | --- |
| `scripts/` 中 TailRocket 原创 Python 自动化 | [MIT](LICENSE-MIT) |
| `profiles/`、`sr_top500_custom.conf` 和相关文档 | [CC BY-SA 4.0](LICENSES/CC-BY-SA-4.0.txt)，同时保留上游署名 |
| 上游及其引用规则 | 以各上游项目自己的许可和署名要求为准 |

TailRocket 不代表 Johnshall、Shadowrocket、Tailscale 或任何代理服务商。使用前请确认相关规则、节点和目标服务符合所在地法律及服务条款。

## 贡献与维护

- 上游配置结构变化：更新 `profiles.json` 中的配置说明，并补充对应测试；
- 生成器修改：更新 `scripts/` 和标准库单元测试；
- 提交前运行：

  ```text
  python -m unittest discover -s tests -v
  ```

工作流会在提交前重新验证上游 14 项清单、必需 sections、终结策略、Tailscale 规则唯一性、上游规则顺序和敏感信息边界。
