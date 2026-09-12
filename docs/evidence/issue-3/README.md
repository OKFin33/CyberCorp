# 阶段交付与沟通卡候选证据

本记录对应 [Issue #3](https://github.com/OKFin33/CyberCorp/issues/3) 的第一、二部分实现，Spec hash `66cd9103c527637bfe1ee713b0bc7f9187696cd3502527ef3333523a49c43d88`，接受来源为该事项原生记录。精确包候选、独立审查、CI 和集成证据由实际 PR/Issue 持有。本页只保存可复现输入与已冻结的合成行为证据，不是任务状态台账。

> **2026-09-12：原始产物已移除。** 本页各条目原先附带 Git bundle、原生对象状态快照与压缩的 API 原始记录。它们已从当前版本移除，理由见[决策记录 0002](../../decisions/0002-remove-verification-artifacts.md)。下文保留的固定提交号、原生对象编号与全部声称仍是记录的一部分；需要原始产物时可从 Git 历史取回（`git log --all --diff-filter=D -- docs/evidence/`）。

## 环境与边界

从独立复制的创建包实际生成 Receipt Desk，移除该临时包后交给未读实现历史的独立实例。项目包含真实临时 Git 及 bare 共享仓库；GitHub API 是仓内限定接口的离线替身，身份与数据全部虚构。没有真实网络、通知、merge、托管并发或真实 Owner 理解验证。公共复现入口见[合成场景](../../../tests/scenarios/README.md)。

以下记录先冻结动作与产物，再对照规格判据；给消费者的是项目目标及环境，没有传递期望答案。报告是消费者自述。合成项目的应用树与原生 API 状态不再随仓库分发，真实 GitHub URL 不存在。

## 已完成的消费

- **空队列到实际结果。** [首个消费者报告](receipt/positive-consumer.md)记录从项目入口发现没有适用实现事项，建立、接受、认领 Issue 11，交付实际 CSV 汇总 CLI；8 个 CLI 子进程测试和额外场景通过。它保留了普通 PR 20 与未来持久化工作的明确审查承诺，没有为前者制造 review 工作。固定提交为 `96b6b212dd5069ea6afe63ec14241830b7c8eecb`；原生候选、检查点与释放的状态快照与 API 原始记录已移除，后者仅代表离线接口调用。
- **迟到答复后的真实换实例。** [后继报告](receipt/refund-successor.md)记录新实例从项目入口发现并采纳[评估者提供的合成 Owner 答复](receipt/owner-reply-input.json)，更新 Canon、受影响的 Issue 7/11 pin 和 Milestone，然后实际实现退款。固定候选 `131414ea2ec063b880e2d1bce20d0c516e5d98c6` 的 11 项 CLI 测试通过，包含负净额、零合计和负数舍入。它没有重问已解决决定，也没有将收到答复直接当成已执行。答复的身份／授权是合成输入，不是真实 Owner 通知实验。
- **整体审查、晚到实例与修正。** [场景设置](receipt/stage-setup.json)透明记录评估者在后继成果上植入的一行倒序缺陷与未接受 JSON 建议；这不是 CyberCorp 包的自然故障。新固定候选 `565c3944438fc431fa8d23d44d89797fa108d4f4` 由[独立 reviewer](receipt/stage-review.md)实际发现 B1，11 项测试有 4 项排序失败，额外 CLI 复现成立。[晚到实例](receipt/late-corpo.md)与该 reviewer 有约 48 秒可核对的实际执行重叠：评论 23 在审查占用 21 仍有效时声明修复意向，待 release 26 后才 claim 27，在原事项修复 B1；没有重复完整 review，也没有实现可选 JSON。修正 `56a975ad0f2eeecbbcdc711803a3d4cc6ede859c` 自查 11 项测试及 5 个 CLI 场景通过，checkpoint／release 29/30。原 reviewer 随后对新 head 完成[独立复验](receipt/stage-recheck.md)：11 项测试与 7 个独立 CLI 场景通过，Review 32 清除 B1，阶段结论／检查点／释放为 33/34/35；旧 Review 22 仍保留并仅适用于失败 head。这是实际两个实例在本机离线 API 上的有界交错，**不证明真实 GitHub 竞争、原子锁或跨机行为**。
- **局部绿灯但缺整体。** [独立准备报告](unintegrated/consumer-report.md)复跑两个局部分支各 1 项测试后，仍判定缺少完整 CLI 与固定集成候选；建议推进已接受的正数／零金额调用链，退款与未来持久化边界分别保留。两个局部候选的固定提交为 `b848222e5d33b580e4298fb5a98c5c4015a65c76` 与 `8f4dcd01418452c7109771b90440971a82ac7726`。没有凭两个局部测试通过新建空 review 工作或宣称整体可验收。
- **同一事实与两张卡。** 输入在[事实](../../../tests/scenarios/communication/facts.md)及[非技术卡](../../../tests/scenarios/communication/nontechnical.md)／[技术卡](../../../tests/scenarios/communication/technical.md)。[非技术草稿](cards/nontechnical.md)用照片导入场景解释结果，[技术草稿](cards/technical.md)给字节哈希、I/O 取舍、固定版本与命令。两者均保留两份不可读文件导致失败、真实环境和审查缺口、相同试点决定边界；[消费者报告](cards/consumer-report.md)记录读取与真实动作。草稿仅将本地事实链接改为仓内相对链接以便公开阅读，正文未改写。未发送，未证明 Owner 看懂。
- **旧项目保护。** [本地采纳记录](old-project-adoption.json)来自实际 `0.1.0a3` 生成项目：新版重装被明确拒绝，所有已有文件未变；逐项适配后保留项目卡、独立审查承诺、检查入口与初始安装元数据，28 个本地 Markdown 链接可达。另一个[独立消费者](adoption-consumer.md)实际从适配后的入口发现原有卡及项目明确审查承诺并执行原检查；该检查仅打印信息，未被当成产品测试。没有真实项目采纳或业务结果证据。

## 阅读成本

[逐路径计量](reading-cost.json)比较同一最小生成项目的完整方法文件冷读，使用 o200k_base / cl100k_base。普通 work 从 2,379–2,404 到 2,751–2,778 tokens；明确单 PR review 从 1,374–1,402 到 1,856–1,885；带 Owner 沟通的 work 为 3,402–3,431（旧版无该完整能力）。已有协调事项上的阶段 review 完整方法路径为 4,273–4,308 tokens，消费者实际读取范围见其报告；阶段与沟通正文仍按需读取。数字不含宿主、业务输入、源代码、原生历史和对话，也不是实际 runtime 账单；计量保留完整方法文件；原生完整历史仍按有效协议读取。

> 上述计量针对 2026-09-12 机制层重构**之前**的十一份方法文件。重构后的路径尚未重新计量。

## 检查及剩余边界

仓库根入口 `python3 -m unittest discover -s tests` 当时为 106 项，包含启动器既有范围；新增包装检查覆盖可携带路由、沟通卡保护与冲突时无部分安装。初版固定包候选已独立审查，实际 PR/CI 的最终 head 和复验记录继续由原生工作持有，不将旧 head 的通过自动套给后来版本。自身采用的共享方法与本候选维护来源一致，项目入口／卡独立适配，初始 `.agents/corp/install.json` 未改写。

本轮合成场景已观察到上述方法消费、真实实例更换、同机时间重叠、修正与独立复验。没有真实 GitHub 竞争／跨机证据、通知接入或 Owner 理解证据。合成项目未授权 merge，独立 reviewer 因此只清除固定候选阻塞，未声称正式阶段交付；CyberCorp 默认分支实际采纳同样等待具体授权与真实集成核验。长期阶段效果仍未验证。
