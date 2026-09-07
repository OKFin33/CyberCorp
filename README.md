# CyberCorp

让用户的 Agent 建立一个可以换人接着做的项目。目标、事实、工作和接续依据由仓库与原生任务系统持有，创建工具可以离席。

本地首版 `0.1.0a1` 提供两个可独立携带的能力包：

- [cybercorp](skills/cybercorp/SKILL.md)：创建／接入方法与安装工具，生成项目自有的准备、工作、审查入口和原生协作辅助命令。
- [corpo-launcher](skills/corpo-launcher/SKILL.md)：面向多种 CLI runtime 的启动器半成品；由用户配置接入，附 Kiro 示例。目标 Corp 不依赖它运行。

## 建立 Corp

让 Agent 阅读 `skills/cybercorp/SKILL.md`，提供项目目标和已有材料；它会检查现有事实面，完成适配与必要交接。也可直接运行确定性安装部分：

```sh
python3 skills/cybercorp/scripts/cybercorp.py /path/to/project --brief /path/to/brief.json
```

[输入格式](skills/cybercorp/references/brief.md) 支持新项目的目标／范围，或已有项目的 `project_ref`。`--dry-run` 只输出文件计划。可以在仓库外的临时目录试用 [示例输入](examples/receipt-desk.json)。

安装会保留已有根 README／AGENTS 内容并追加入口；冲突文件需要显式适配。相同输入再次运行会保留项目后续编辑。脚本不提交、发布或创建 GitHub 工作，也不会宣称初始化完成；Agent 随后从生成项目的 `docs/corp/README.md` 继续准备与交接。

生成后的仓库自带以下命令：

```sh
python3 .agents/corp/enter.py --worktree /path/to/new-checkout
python3 .agents/corp/repo-context.py
python3 .agents/corp/repo-context.py --issue 7
```

第一条从固定远端 SHA 建独立工作树，保留原现场；后两条读取真实 GitHub 工作。`7` 换成实际 Issue。上下文读取使用远端默认分支，依赖目标项目已共享其 Corp 入口及原生工作。

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

Python 3.9+，无需第三方 Python 运行依赖；GitHub 读取另需 Git 和正常认证的 `gh`。

```sh
python3 -m unittest discover -s tests
python3 -m unittest discover -s skills/corpo-launcher/scripts/tests
```

本地验证覆盖可携带安装、已有项目保护、真实临时 Git 工作树、原生协议回放及 fake-CLI 启动／恢复。GitHub API 行为使用隔离夹具；Kiro 包装器真实模型端到端测试、独立 Corpo 在第二项目交付实际成果和新多机协作尚未验证。

[产品约定](docs/product.md) · [实现计划](docs/plan.md) · [实现来源](docs/source-notes.md)
