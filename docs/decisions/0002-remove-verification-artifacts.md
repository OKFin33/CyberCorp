# 0002 · 移除验证产物，证据保留为报告

- 日期：2026-09-12
- 状态：已采纳
- 影响面：`docs/evidence/`

## 决策

移除 `docs/evidence/` 下的三类产物，共 27 个文件、约 915KB：

- 9 个 Git bundle（合成项目的仓库打包）
- 9 个 `*.jsonl.gz`（离线 GitHub API 替身的原始调用记录）
- 9 个 `state.json` / `*-state.json`（原生对象状态快照）

**保留**：19 份 markdown 报告（消费者自述、独立审查、复验结论）、`source-manifest-v2.json`（147 项 SHA-256 核验清单）、以及判据与度量类 json（`reading-cost.json`、`evaluator-check.json`、`stage-setup.json`、`method-applicability.json`、`old-project-adoption*.json`、`snapshot.json`、`object*.json` 等）。

`docs/evidence/` 由 1065KB 降至 150KB；仓库 tracked 总量由 1.4MB 降至 0.51MB。

## 为什么

**一、bundle 重建出来的是合成项目，不是本仓库。** [实测] `git bundle list-heads` 显示其 head 为 `refs/heads/codex/receipt-summary`，且其中的提交（`96b6b212`、`131414ea` 等）**不在本仓库历史中**。重建它们只能得到一个为验证而造的虚构项目（Receipt Desk、Kit Desk），用来复跑针对那个虚构项目的 CLI 测试。那些应用代码没有独立价值。

**二、它们支持的声称已经被本项目自己标注了范围限制。** [实测] `docs/verification-status.md` 把"多实例与跨机行为"列在**无证据**栏，理由写着"现有交错证据来自本机离线 API，不证明真实 GitHub 的竞争与原子性"；`docs/evidence/issue-3/README.md` 也明写植入缺陷"不是 CyberCorp 包的自然故障"。**一个已经带明确范围限制的声称，用文字记录加固定提交号就足够**——读者要么接受这个有限陈述，要么等真实场景证据；给他 900KB 二进制不会改变这个判断。

**三、外部实测：存这类产物反而降低可信度。** [故障] 一次零上下文的外部审查（一个不认识作者、只拿到仓库的实例）把 `docs/evidence/` 存 Git bundle 与压缩 API 记录列为第三大劝退点，原话是"引发对可信度包装的怀疑"。它的推理是：主流开源项目的验证证据在 CI 上，看到一堆手工存进 Git 的产物，第一反应是"为什么要这么用力证明自己"。**这条是决定性的——保留它们的目的是增加可信度，实测效果相反。**

**四、无技术依赖。** [实测] 没有任何代码、测试或 CI 配置引用这些文件。测试用的 `.scenario/state.json` 是场景运行时路径，与 evidence 内的文件无关。

## 被否决的替代方案

**保留产物，在 README 里加一句说明它们是什么。** 否决理由：说明解决不了信号问题。外部审查者的怀疑不来自"不知道这些文件是什么"，而来自"手工存证据"这个动作本身与开源惯例的偏离。加说明只会让偏离更显眼。

**搬到 GitHub Release assets。** 否决理由：那需要先有一个 release，而本项目尚未发布正式版本；且这批产物是"CI 尚不存在时期"的形态，搬运它们不如让它们随历史留在原处。

## 可逆性

删除只作用于当前版本。产物仍在 Git 历史中，可用 `git log --all --diff-filter=D -- docs/evidence/` 定位，用 `git show <commit>:<path>` 取回。因此这个决定不销毁任何证据，只是不再随当前版本分发。

## 后续

新的验证证据走 CI：可确定性验证的一层（能否 clone、入口能否读到、路由是否可达）进 CI 每次跑；非确定性的一层（实例是否理解并做出有价值判断）用手工触发的 workflow，报告作为 artifact 上传。届时证据在平台上而不在 Git 里，这是这类证据的常规归处。

`docs/evidence/issue-3/README.md` 的阅读成本计量针对重构前的十一份方法文件，重构后尚未重新计量——那项计量本身值得在 CI 里做，因为它是确定性的。
