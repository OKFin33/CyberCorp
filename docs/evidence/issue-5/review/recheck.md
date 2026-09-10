# Issue 5：B1 与采纳证据独立复验

结论：**B1 已解除，旧项目升级拒绝证据的归因问题已更正；本次固定候选的已审范围内没有剩余阻断项。** 原 `review.md` 保留为 v1 审查记录，本文件只更新明确列出的修正结论。此结论不是托管 PR review、正式阶段完成、默认分支采用或发布／merge 授权。

## 固定对象与范围

- Reviewer：`/root/phase12_candidate_review`，运行标识 `01a08952-f196-7e71-adff-0e0985f8ec11`；没有参与实现或修复，未修改被审 checkout、提交／push、写真实外部系统或启动其他实例。
- 独立 checkout：`/tmp/cybercorp-issue5-review-v2`。
- 原 base：`15682e2d9ca77dfbd8234cadc803f35557d0f76c`。
- 原审 snapshot：`8cb49d79282d7fa618b4a4f200c5169d284f2d96`。
- 修正 snapshot：`64f008b71f04503f634cb649f6cbdd68e176c229`。
- Spec pin 不变：Issue #5，SHA-256 `a0850dae9921017eebfe8191dcf60079fa3db71483e6e8e30e8a8d47719bfe59`，接受 https://github.com/OKFin33/CyberCorp/issues/5#issuecomment-5611768368。沿用首审已对真实 Issue 核验的约定；本次未改变或重新发表接受。
- 核验 `object-v2.json`、真实 HEAD 和 `source-manifest-v2.json` 的全部 147 项：无不匹配，开始和检查后工作树干净。
- v1..v2 排除 evidence 后只有两份 `check.py` 与 `tests/test_verification.py` 发生变化；证据变化包含升级探针更正、保留原探针、先前已审的准备后继结果和证据导航。未重新审查无关前置 PR #4 全套行为。

## B1：解除

源码在 `skills/cybercorp/assets/corp/.agents/corp/check.py:51` 与自身 `.agents/corp/check.py:51` 复用既有 Canon 解析结果，要求 `current-delivery-focus` 条目存在，缺失时返回明确的 `Missing required Canon route: current-delivery-focus`。两份内容相同。修正只恢复 native reader 已要求的入口结构，没有扩展通用路由 schema、联网检查、准备审批或调度层。

Reviewer 用修正创建包另建真实临时 Git 项目，独立执行以下三态，而非仅阅读新增单测：

| 实际状态 | 实际 exit / result | 判断 |
| --- | --- | --- |
| 合法初始项目，focus 条目存在但 unresolved | `0 / passed`；`unverified_routes` 明确包含 focus | 保持本地创建语义，不把共享配置缺口伪称已验证 |
| 删除整个 focus 条目 | `1 / failed`；错误明确指出 current-delivery-focus | 原错误绿灯消失 |
| 恢复原条目 | `0 / passed`，未验证范围恢复 | 可定位修正并继续 |

根实际入口 `python3 scripts/check.py --base 15682e2d9ca77dfbd8234cadc803f35557d0f76c` 在固定 v2、Python 3.14.2 上执行：Corp 结构／Git 差量检查通过；**123 项 unittest 全通过**，其中包含新增删除／合法 unresolved／恢复用例及既有版本、失效基线、真实 Git、链接和可携带检查。根测试已含 launcher 测试，不重复加总为更多证据。

## 旧项目采纳证据：更正成立

- `old-project-adoption-initial.json` 与 v1 原错误探针文件逐字相同，明确被排除，不再拿外层仓库保护证明升级拒绝。
- 更正后的 `old-project-adoption.json` 记录旧／新真实 CLI、exit=2，以及准确拒绝原因：已有不同输入／包，应适配 existing owners 而非覆盖；声明边界仍是本地探针。
- Reviewer 另在新的临时目录，从固定 `2579453fbde96df0eaac0c8f62e5d28f9942ac21` 导出 a3 创建包，真实 CLI 安装成功并核验安装版本 `0.1.0a3`，加入项目自有方法承诺，再用 v2 候选 CLI 以同一 brief 重装。实际 exit=2，准确拒绝信息与更正记录一致；比较所有非 `.git` 项目文件的 SHA-256，前后完全相同。该复现直接到达升级拒绝路径，没有触发路径别名／外层仓库分支。
- 只读核对提供的采纳现场 `/private/tmp/corp-issue5-adoption-fixed-z20ve1bo/project`：初始 `.agents/corp/install.json`、自有 `docs/owner-guide.md`、`tests/check_existing.py` 与现场 baseline 字节相同；work-corp 中明确的 storage-interface 独立审查承诺仍在；本地 `accepted-work.md` 经实际 helper 校验匹配 hash `1fd585fc86b5a1d9a08530db046bb95d806472b45655c0e25002b3cdaee8be7c`，checkpoint 文本指向相同 hash。
- 在已阅读的现场执行其现有检查及 Corp checker 均通过。原项目检查只是 `assert 2 + 2 == 4`，因此只证明检查入口与自有文件得到保留，不能证明库存业务行为。
- 本地 Spec／checkpoint 格式正确且保存，不等于服务端 Spec 接受、实际 native 占用或真实项目采用；更正后的说明准确保留了这一点。

## 仍适用的首审结论与未证明范围

准备／选工／失败方法正文未因 B1 改变。首审中已独立复建的准备后继 13 项行为测试、旧失败版到修正版的实际检查接续、阶段／队列／基础设施行为及分发／自身采纳判断继续适用。早期消费者并未执行后加的 focus 检查；它们只支撑未改的自然语言方法与实际交接，最终 helper 的 B1 边界由本次真实生成项目负例与 123 项根测试证明。

实际源码仍是本地独立审查快照。尚未证明或尚待完成：真实候选发布／PR 原生审查归档、适用托管 PR CI、前置最终集成、实际默认分支版本检查与采用、正式阶段交付，Python 3.9/3.13 托管运行、真实 GitHub 并发／跨机、Owner 理解及业务采用。合成 API、bundle 与本地通过不会消除这些边界。

父实例另告知 v2 冻结后源树的 README/docs/plan 仅更新状态和 evidence 链接；本次未将这些未纳入 v2 的文案视为已审源码。最终交付应准确列出差异及适用证据；无需仅因无行为变化的状态文案机械重跑无关消费场景。

原 `review.md` 的 B1 仅对 v1 成立；以上明确修正将其在 v2 关闭。若源码 head、相关 Spec 或实际集成 base 再变化，应做相应影响判断与必要复验。
