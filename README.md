# CyberCorp

让用户的 Agent 建立一个可以换人接着做的项目。目标、事实、工作和接续依据由仓库与原生任务系统持有，创建工具可以离席。

当前创建包候选为 `0.1.0a5`；仓库提供两个可独立携带的能力包：

- [cybercorp](skills/cybercorp/SKILL.md)：创建／接入方法与安装工具，生成项目自有的准备、工作、审查入口和原生协作辅助命令。
- [corpo-launcher](skills/corpo-launcher/SKILL.md)：面向多种 CLI runtime 的启动器半成品；由用户配置接入，附 Kiro 示例。目标 Corp 不依赖它运行。

## 建立 Corp

让 Agent 阅读 `skills/cybercorp/SKILL.md`，提供项目目标和已有材料；它会检查现有事实面，完成适配与必要交接。也可直接运行确定性安装部分：

```sh
python3 skills/cybercorp/scripts/cybercorp.py /path/to/project --brief /path/to/brief.json
```

[输入格式](skills/cybercorp/references/brief.md) 支持新项目的目标／范围，或已有项目的 `project_ref`。`--dry-run` 只输出文件计划。可以在仓库外的临时目录试用 [示例输入](examples/receipt-desk.json)。

安装会保留已有根 README／AGENTS 内容并追加入口；冲突文件需要显式适配。相同输入再次运行会保留项目后续编辑。脚本不提交、发布或创建 GitHub 工作，也不会宣称初始化完成；Agent 随后从生成项目的 `docs/corp/README.md` 继续准备与交接。

准备方法引导 Agent 从项目目标、验收和现有成果推导交付路线、开发起点与首批工作；开发中继续按实际交付缺口选择 plan、work 或 review。检查与失败接续、阶段交付和 Owner 沟通方法按需读取。项目保留自己的事实来源、技术选择、沟通卡与检查入口。

新建项目获得这些方法；已有项目按[采纳说明](skills/cybercorp/references/brief.md)适配方法与链接目标，保留项目自有编辑，不能重新安装覆盖。

生成后的仓库自带以下命令：

```sh
python3 .agents/corp/enter.py --worktree /path/to/new-checkout
python3 .agents/corp/repo-context.py
python3 .agents/corp/repo-context.py --issue 7
python3 .agents/corp/check.py
```

第一条从固定远端 SHA 建独立工作树，保留原现场；中间两条读取真实 GitHub 工作。`7` 换成实际 Issue。上下文读取使用远端默认分支，依赖目标项目已共享其 Corp 入口及原生工作。

最后一条仅做本地 Corp 结构和实际 Git 差量检查，不联网或运行项目业务测试。检查结果分别报告本地结构与尚未核验的共享路由；创建 Agent 按项目需要将它接入现有检查命令与 CI。具体版本、失败与复现方法见生成项目的 `docs/corp/verification.md`。

## 接入 CLI runtime

用户自行安装、登录并选择 runtime、模型和工具权限。启动器可以把显式命令交给不同 CLI：

```sh
python3 skills/corpo-launcher/scripts/corpo.py --runtime cli start --repo /path/to/project --dry-run -- your-cli your-flags '{prompt}'
```

将 `your-cli your-flags` 换成当前 CLI 支持的命令；`{prompt}` 作为一个完整参数传入。去掉 `--dry-run` 后交接当前终端。需要专属的会话发现／恢复能力时，可通过 `--adapter /path/to/my_adapter.py` 调用用户自己的 Python 适配器。

附带的 Kiro 示例已经实现对应命令：

```sh
python3 skills/corpo-launcher/scripts/corpo.py --runtime kiro start --repo /path/to/project --dry-run
python3 skills/corpo-launcher/scripts/corpo.py --runtime kiro sessions --cwd /path/to/project
python3 skills/corpo-launcher/scripts/corpo.py --runtime kiro resume --cwd /path/to/project --session NATIVE_SESSION_ID
```

具体接法见 [启动器 skill](skills/corpo-launcher/SKILL.md)。CLI 的安装认证、权限语义和会话格式由各 runtime 持有；Kiro 的实现是示例，其他 runtime 仍需用户适配和验证。

## 开发与验证

安装、dry-run 和本地测试需要 Python 3.9+ 与 Git，无需第三方 Python 运行依赖；原生 GitHub 读取另需正常认证的 `gh`。

```sh
python3 scripts/check.py
python3 -m unittest discover -s skills/corpo-launcher/scripts/tests
```

第一条依次运行本仓 Corp 检查与根 unittest 入口（`python3 -m unittest discover -s tests`），检查失败即停止。可用 `--base <commit>` 指定差量基线。根测试已包含启动器测试；第二条用于局部验证，其结果不与根入口相加。[CI](.github/workflows/tests.yml)使用同一个命令，并保留实际版本、事件与运行证据。

本地验证覆盖可携带安装、已有项目保护、真实临时 Git 工作树、原生协议回放及 fake-CLI 启动／恢复。[独立消费证据](docs/evidence/issue-5/README.md)记录合成项目中准备后的实际实施和失败修正。离线 API、测试通过与实际项目采用分开；Kiro 包装器真实模型端到端、新多机协作和业务交付效果尚未验证。

[产品约定](docs/product.md) · [实现计划](docs/plan.md) · [实现来源](docs/source-notes.md)

<!-- cybercorp:entry:start -->
## Agent collaboration

工作 Agent 从 [Corp 入口](docs/corp/README.md) 进入项目。
<!-- cybercorp:entry:end -->
