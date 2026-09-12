# 变更记录

本文件记录已交付的变化。进行中的工作由同仓 [Issues](https://github.com/OKFin33/CyberCorp/issues) 与 [Milestone](https://github.com/OKFin33/CyberCorp/milestone/1) 持有，能力的验证程度见 [验证状态](docs/verification-status.md)，**每项变化背后的理由与被否决的替代方案见 [决策记录](docs/decisions/)**。

版本号形如 `0.1.0a5` 的是创建包候选，不代表默认分支已采用或行为已验收。

## 未发布

### 机制层重构

- 机制层由 13 份场景文档收敛为两份：[入口](docs/corp/README.md)持有统领规则、开工必读与场景路由，[mechanics.md](docs/corp/mechanics.md) 是全部规则的唯一定义处，按八个子问题组织。每条规则须能指出它服务的子问题与它消除的猜测。
- 引入统领规则：不可逆动作清单由项目声明，清单之外的动作执行者自主，且要求 Owner 介入的一方承担举证责任。此前"普通工程判断不自动上交人工"是与其他需求并列的一条，现在成为其他机制的授权判据。
- 开工前必须遵守的规则从散布于多份文档收敛为入口中的五条。
- 占用机制覆盖到没有预先载体的动作：生成工作与审查各自需要可见占用，规划先创建载体 Issue。
- 认领与释放改用 GitHub 维护的字段（`assignee`、`updated_at`），移除自建的 lease／renewal 记录格式——一次字段笔误曾使整条执行记录不可重放。
- 阶段审查的开启条件改为机器可核对：规划者声明阶段的关闭条件，不再由任何实例判断阶段是否接近完成。
- 事实层的 `unknown` 区分"未决"与"未登记"。
- 仓库改为常规开源结构：新增出处声明、变更记录、贡献指引、决策记录与验证状态；`docs/plan.md`、`docs/corp/preparation.md`、`docs/source-notes.md` 的内容迁入上述位置。
- 移除 `docs/evidence/` 下的 Git bundle、压缩 API 记录与原生状态快照（27 个文件、约 915KB）；证据以报告、固定提交号与 SHA-256 清单形式保留。`docs/evidence/` 由 1065KB 降至 150KB，仓库 tracked 总量由 1.4MB 降至 0.51MB。理由见[决策记录 0002](docs/decisions/0002-remove-verification-artifacts.md)。
- **切断外部代码继承链。** `spec-checkpoint.py` 与 `repo-context.py` 由未接触旧实现的独立实例按功能规格从零重写（108→176 行、447→313 行），接口契约保持不变——Spec 标记、归一化规则与输出格式一致，已发布的 acceptance 哈希不受影响。`work-state.py` 与 `format-event.py` 直接删除，它们是旧"评论即状态机"机制的实现，新机制改用 `assignee` 与 `updated_at` 后不再需要。`tests/protocols/` 从零重写（72 项）。`NOTICE` 删除——出处声明的对象已不存在。理由与隔离条件见[决策记录 0003](docs/decisions/0003-remove-inherited-code.md)。

## 0.1.0a5 — 项目准备与检查反馈

由 [Issue #5](https://github.com/OKFin33/CyberCorp/issues/5) 持有。

- 准备方法引导按项目实际从目标与验收推导粗路线、近期重点、开发骨架与首批工作。
- 按交付缺口选工接入工作循环：队列非空但必要结果缺少承接时仍补齐。
- 新增可携带的本地检查，适配项目实际检查与 CI，记录真实 Git 范围、版本与运行结果。
- 旧项目重装保护与显式采纳已本地核验；独立候选审查发现的阶段路由漏检已修正并复验。

证据：[合成消费验证](docs/evidence/issue-5/README.md)。

## 0.1.0a4 — 阶段交付与 Owner 沟通

由 [Issue #3](https://github.com/OKFin33/CyberCorp/issues/3) 与 [PR #4](https://github.com/OKFin33/CyberCorp/pull/4) 持有，已合入 `7ebc4a6`。

- 阶段候选、修正复验与交付方法。
- Owner 沟通卡机制：表达偏好可替换，不改变事实、验收与权限。

证据：[合成行为证据](docs/evidence/issue-3/README.md)，含可重建的 Git bundle 与固定提交。

## 初始 — 自身协作与基本准备

由 [Issue #1](https://github.com/OKFin33/CyberCorp/issues/1) 持有。

- 自包含创建包：确定性安装、项目自有的准备／工作／审查方法、原生 Spec、占用与上下文工具。
- 独立 checkout 入口保留原 clone 及其未提交工作；方法更新不自动改任务 pin。
- 可选启动器独立携带，支持显式 CLI 命令与用户自有适配器，Kiro 是其中一个示例。
