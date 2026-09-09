# 阶段交付与沟通卡候选证据

本记录对应 [Issue #3](https://github.com/OKFin33/CyberCorp/issues/3) 的第一、二部分实现，Spec hash `66cd9103c527637bfe1ee713b0bc7f9187696cd3502527ef3333523a49c43d88`，接受来源为该事项原生记录。精确包候选、独立审查、CI 和集成证据由实际 PR/Issue 持有。本页只保存可复现输入与已冻结的合成行为证据，不是任务状态台账。

## 环境与边界

从独立复制的创建包实际生成 Receipt Desk，移除该临时包后交给未读实现历史的独立实例。项目包含真实临时 Git 及 bare 共享仓库；GitHub API 是仓内限定接口的离线替身，身份与数据全部虚构。没有真实网络、通知、merge、托管并发或真实 Owner 理解验证。公共复现入口见[合成场景](../../../tests/scenarios/README.md)。

以下记录先冻结动作与产物，再对照规格判据；给消费者的是项目目标及环境，没有传递期望答案。报告是消费者自述；Git bundle、原生对象快照和压缩原始 API 记录保留复核入口。解压 API 记录可用 Python 标准库 `gzip`，Git bundle 可通过 `git clone` 在新目录重建。

## 已完成的消费

- **空队列到实际结果。** [首个消费者报告](receipt/positive-consumer.md)记录从项目入口发现没有适用实现事项，建立、接受、认领 Issue 11，交付实际 CSV 汇总 CLI；8 个 CLI 子进程测试和额外场景通过。它保留了普通 PR 20 与未来持久化工作的明确审查承诺，没有为前者制造 review 工作。固定提交 `96b6b212dd5069ea6afe63ec14241830b7c8eecb` 在[真实 Git bundle](receipt/positive.bundle)，原生候选、检查点与释放见[快照](receipt/positive-state.json)；[API 原始记录](receipt/positive-api.jsonl.gz)仅代表离线接口调用。
- **同一事实与两张卡。** 输入在[事实](../../../tests/scenarios/communication/facts.md)及[非技术卡](../../../tests/scenarios/communication/nontechnical.md)/[技术卡](../../../tests/scenarios/communication/technical.md)。[非技术草稿](cards/nontechnical.md)用照片导入场景解释结果，[技术草稿](cards/technical.md)给字节哈希、I/O 取舍、固定版本与命令。两者均保留两份不可读文件导致失败、真实环境和审查缺口、相同试点决定边界；[消费者报告](cards/consumer-report.md)记录读取与真实动作。草稿仅将本地事实链接改为仓内相对链接以便公开阅读，正文未改写。未发送，未证明 Owner 看懂。
- **旧项目保护。** [本地采纳记录](old-project-adoption.json)来自实际 `0.1.0a3` 生成项目：新版重装被明确拒绝，所有已有文件未变；逐项适配后保留项目卡、独立审查承诺、检查入口与初始安装元数据，28 个本地 Markdown 链接可达。另一个[独立消费者](adoption-consumer.md)实际从适配后的入口发现原有卡及项目明确审查承诺并执行原检查；该检查仅打印信息，未被当成产品测试。没有真实项目采纳或业务结果证据。

## 阅读成本

[逐路径计量](reading-cost.json)比较同一最小生成项目的完整方法文件冷读，使用 o200k_base / cl100k_base。普通 work 从 2,379–2,404 到 2,751–2,778 tokens；明确单 PR review 从 1,374–1,402 到 1,856–1,885；带 Owner 沟通的 work 为 3,402–3,431（旧版无该完整能力）。阶段与沟通正文仍按需读取。数字不含宿主、业务输入、源代码、原生历史和对话，也不是实际 runtime 账单；计量保留完整方法文件；原生完整历史仍按有效协议读取。

## 尚待补齐的证据

答复后换实例采纳、整体审查修正与独立复验正在本轮隔离场景中继续。真实多实例并发、真实通知/Owner 理解、默认分支实际采纳和长期阶段效果仍未验证。通用验证反馈属于下一步范围，本次没有实现其检查工具或失败调度。
