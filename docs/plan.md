# CyberCorp 实现与接续

目标与边界由 [product.md](product.md) 持有；Spec、执行占用、候选、审查及实际交付由同仓原生事项持有。当前创建包为 `0.1.0a5` 候选，尚未代表默认分支已采用或全部行为已经验收。

## 已有基础

- 自包含创建包提供确定性安装、项目自有准备／工作／审查方法与原生 Spec、占用和上下文工具。独立 checkout 入口保留原 clone 及其 WIP，方法更新不自动改任务 pin。
- 可选启动器独立携带，支持显式 CLI 命令与用户自有适配器，Kiro 是一个示例。runtime 安装、认证、模型及原生会话接入由用户负责，目标 Corp 不依赖启动器运行。
- CyberCorp 自身协作与基本准备已沿 [Issue #1](https://github.com/OKFin33/CyberCorp/issues/1) 交付。实际默认分支、独立回执与 CI 证据在该事项及 PR，不把新版本的准备要求追溯成旧结果未完成。
- 阶段交付与 Owner 沟通由 [Issue #3](https://github.com/OKFin33/CyberCorp/issues/3)／[PR #4](https://github.com/OKFin33/CyberCorp/pull/4) 承接；PR #4 已合入 `7ebc4a6`；固定 `0.1.0a4` 候选及其[合成行为证据](evidence/issue-3/README.md)是本轮输入。它的范围与有效审查承诺保持独立。

## 当前交付：项目准备与检查反馈

[Issue #5](https://github.com/OKFin33/CyberCorp/issues/5) 持有本轮 Spec 与承接。实现从固定阶段／沟通候选继续，PR #4 合并树与本轮原基线 `15682e2` 相同；前置的正式交付结论由 Issue #3 持有。

1. **准备到开工。** 改写现有 prepare-corp 与阶段方法，引导 Corpo 按项目实际从目标和验收推导粗路线、近期重点、开发骨架与首批工作；Canon 补齐与设计可以往返。后继者应能取得依据并开始近期工作。
2. **按交付缺口选工。** 将阶段结果与必要前置接入现有工作循环。队列非空但必要结果缺少承接时仍补齐；已有安排充分则直接执行，按真实依赖并行。
3. **检查与修正接续。** 增加可携带的本地 Corp 检查，适配项目实际检查与 CI，记录真实 Git 范围、版本和运行结果。失败沿既有工作定位、复现与修正。

本候选已落下上述方法、检查工具与本仓接线，并完成准备后继、非空队列、基础设施前置／目标和失败接续的[合成消费验证](evidence/issue-5/README.md)。根入口为 `python3 scripts/check.py`，依次运行本仓 Corp 检查和原有 unittest 入口；无新增第三方 Python 运行依赖。完整要求见[吸收规格](specs/delivery-communication-verification.md)与本事项有效 Spec。

旧项目重装保护与显式采纳已经本地核验。独立候选审查发现的必需阶段路由漏检已修正并通过复验，已审范围无剩余阻断；前置 PR #4 已合入。本候选的发布、托管 CI 与最终集成证据由后续 PR／Issue #5 持有，最终默认分支采纳尚待完成。代码与本地测试、独立消费、托管 CI、默认分支采用及业务效果分开报告。最终候选、审查和交付状态从原生事项恢复。

## 方法阅读

| 当前动作 | 所需方法 |
| --- | --- |
| 普通实现 | 入口、development-loop、work-corp、claim-protocol 与 Spec 核验 |
| 全项目准备 | 入口、prepare-corp、阶段方法，按需核对输入与检查入口 |
| 新建／修改／拆分／关闭 Issue 或首次／替代接受 Spec | spec-authoring |
| 深入跨事项安排、阶段审查或生成工作 | coordination，再进入所承接事项 |
| 阶段候选、修正复验与交付 | milestone-delivery；独立 review 由未参与者按适用约定承担 |
| Owner 沟通或答复采纳 | communication 与项目当前沟通卡 |
| 检查接线、版本／CI 证据或失败接续 | verification |
| 完整取数与可信时间复核后仍有历史完整性错误 | damaged-history |

普通工作不需每次通读规划、沟通或检查设置正文；实际发生相应动作时进入。保留必需原生历史、有效约定和占用核对，不通过截断这些输入节省阅读。

## 采纳与证据边界

分发来源是 `skills/cybercorp/assets/corp/`，自身运行来源是根 `.agents/` 与 `docs/corp/`。本候选分别更新并核验这些来源；目标项目通过自身变更流程适配，保留自有事实、卡、检查、有效 pin、明确审查承诺及初始安装溯源。重装继续拒绝覆盖。

结构检查证明相应文件与可执行契约；行为试验须使用实际生成项目并保留固定输入与真实动作。合成 API 不证明真实 GitHub 或跨机协作，CLI 包装不证明 runtime 实际接入，沟通草稿不证明 Owner 理解。长期项目效果按实际需要继续取证，不自动扩展为新协议、固定角色或审批。
