# Issue 5 固定本地候选独立审查

结论：**请求修正 B1 后复验**。准备与选工方法符合本轮 intent，已观察到准备者离席后的实际实施及检查失败的接续修正；但新增通用检查对必需 Canon 路由缺失会错误报绿。本结论不否定已保留的前置 PR #4 证据，也不构成原生 PR review、正式阶段交付、发布或 merge 授权。

## 对象、独立性与约定

- Reviewer instance：`/root/phase12_candidate_review`，本审查运行标识 `01a08952-f196-7e71-adff-0e0985f8ec11`。未参与候选实现；只读被审源码及提供的补充证据，未修改被审 checkout，未启动其他实例、写真实外部系统或提交／push。
- 独立 checkout：`/tmp/cybercorp-issue5-review-v1`；base `15682e2d9ca77dfbd8234cadc803f35557d0f76c`；snapshot HEAD `8cb49d79282d7fa618b4a4f200c5169d284f2d96`。初始及检查后 Git 工作树均干净。
- 这是可丢弃本地 Git 快照。真实功能工作树未据此提交／发布；没有可对其发表本次原生审查的真实 PR。
- 核验 `source-manifest.json` 全部 132 项 SHA-256：无不匹配。审查增量为上述 base..HEAD 的 51 个文件，必要联动包含自身方法、创建分发、前置证据和检查入口。
- Issue #5 当前为 OPEN；实际线上 body 经 `spec-checkpoint.py --check` 确认 hash `a0850dae9921017eebfe8191dcf60079fa3db71483e6e8e30e8a8d47719bfe59`。有效接受记录为 https://github.com/OKFin33/CyberCorp/issues/5#issuecomment-5611768368，来源 intent 为同事项评论 `5611732973`。本地 `spec.md` 与该 pin 对应。
- 已读取 Corp 入口、development-loop、review-corp、spec-protocol、产品约定、实施计划、吸收规格相关部分和创建／启动包入口；未把 Spec 接受当作发布、集成或阶段验收权限。

## 阻断项

### B1 / P2：必需 current-delivery-focus 被删除后，检查仍返回 passed

**路径：** `skills/cybercorp/assets/corp/.agents/corp/check.py:50–61`，以及自身采纳的 `.agents/corp/check.py:50–61`。

**场景与实际结果：** 在真实创建包生成的临时 Git 项目中，删除 `docs/corp/canon-map.yaml` 的整条 `current-delivery-focus`，保留其余格式有效的 Canon rows，执行生成项目的 `python3 .agents/corp/check.py`。实际 exit code 为 `0`，`status=passed`；`unverified_routes` 仅包含 `active-change-specs`，没有缺失 focus 的提示。同一份映射经现有 native reader 的 `parse_map` 和 `focus_number` 读取，实际抛出 `current-delivery-focus missing`。该行为由 reviewer 独立执行得到。

**原因与影响：** `parse_map` 只验证已有条目的格式，新增检查随后只遍历已有 rows；没有核验正常全局工作发现所必需的路由是否仍存在。删除必需条目因此让检查静默缩小范围，虽然下一 Corpo 的正常 landing 已无法发现阶段。本地结构通过与远端访问未验证可以区分，但这里缺的是可在本地确定的必需结构。

**违反约定：** Issue #5 产品行为 3 及验收“生成项目的必需路由或实际检查失败”要求实际检查失败并提供定位；吸收规格第三部分要求通用检查覆盖交付路由的适用结构与可执行契约。当前错误绿灯落在承诺的本地检查范围内。

**最低修正：** 在既有 Canon 解析后验证正常入口所必需的 route ID 存在，缺失时给出具体 ID 与映射路径；同步分发与自身 owner。使用现有约定即可，不需要新增 schema、联网探测、完整 Markdown 框架或调度器。合法的 `unresolved`／`pending-relocation` 条目仍应维持当前明确未验证的本地创建语义。

**必要复验：** 真实临时生成项目中，缺失 focus 必须非零退出；恢复该条目后通过；无共享仓库的新建项目保留合法 unresolved 行时仍通过并报告未验证范围。运行根实际入口与适用新增负例，复核有效源码与新固定候选。无需重跑未受影响的前置 PR #4 消费场景。

## 证据修正与非阻断意见

1. `docs/evidence/issue-5/old-project-adoption.json` 原始 `refusal` 为 `Target is inside another Git repository; use its real root`。这次结果证明的是路径／仓库边界保护，没有到达旧包升级重装的拒绝分支，因此不能用它证明该次升级保护成立。已有 `test_changed_package_with_same_version_does_not_claim_current_installation` 和重装保留项目编辑测试仍有效；安装器本轮除版本号外无行为改动。应保留原记录的实际失败原因，补充真实 CLI、正确 root 上的升级拒绝证据，并明确 Spec pin 等自有事实如何保存。实现者已确认初次 `/var` 与 `/private/var` 入口差异，表示将补充证据；本报告尚未收到并核验修正版。此处是证据归因问题，不据此宣称安装器覆盖了用户文件。
2. 早期消费者使用的 `check.py` SHA 为 `083e7c…`，不等于最终源码 `206a91…`。补充 `method-applicability.json` 解释了后续检查范围／链接语法／错误输出的变化；snapshot 中 prepare/work/milestone 方法与最终分发内容匹配。故准备／选工行为证据可保留，早期 checker 的成功不覆盖最终 checker 全部边界。最终 checker 正反行为由此次根测试及 B1 独立负例判断。
3. 普通方法冷读计量从 a4 的 2741/2763 tokens 到 a5 的 2794/2815，增加约 52–53 tokens。按完整普通 work 路径计量，新增 verification 通过触发读取；没有发现强制每次选工通读、额外报告表或全项目重规划。数字来自冻结计量文件，reviewer 未独立重跑 tokenizer，不将其当实际账单或效率收益。

## 已核实施与消费者行为

- **准备与持续选工：** 修改位于现有 prepare-corp、milestone-delivery 和 development-loop；创建 skill 继续路由，不复制第二套准备正文。近期骨架、维护位置、真实前置、整体范围与远期粗路线均有明确引导；非代码结构、普通设计裁量、已承接工作与局部等待边界保留。没有新增固定角色、文件清单或审批层。
- **准备到后继实施：** 补充证据目录 `/tmp/cybercorp-phase12-20260910/docs/evidence/issue-5/preparation-successor/` 的 bundle、native state/API 和报告与固定候选 `795ada952daa4a46af6533864030db16595ff30e` 对应。已从 bundle 独立复建该应用树并执行 13 项测试通过，检查 README 与 architecture 的实际输入、模块、调用／检查入口。后继通过准备 `b821805…` 与 Issue 12 接手，完成 import/search 实际代码，保留贷款／归还／导出的后续范围；未把示例测试或准备文档当作应用完成。该结果支持本轮要求的有贡献首项交接；应用自身阶段审查与 main 集成仍未完成，不能将它计为完整应用交付。
- **非空队列与基础设施：** library/prerequisite 的冻结结果、原生对象和消费者记录支持选择主要库存库结果／真实前置，而非被文档和示例维护队列带偏。基础设施本身是产品的场景没有强加 CLI 或业务界面。不同场景的测试／报告不证明真实 GitHub 并发或所有领域泛化。
- **失败反馈：** 从 repair-successor bundle 独立恢复 `22b6afb1868cf59018885e4a0fe72f20ecdd4437` 与修复 `4624e8616be2b2731808a4a9230754e2a0b48f7b`，执行实际 `scripts/check.py --base 22b6…`。旧版 exit=1，定位 `verification-entry.md` 缺失并在 unittest 前停止；修正版 exit=0，实际运行 11 项行为测试。原工作及明确 checkpoint/release 承接修正；这是透明标记的评估者故障注入，未伪称产品自然故障或托管 CI。
- **自身采纳与可携带：** 本轮变更的 prepare/work/development-loop/milestone-delivery/verification/check 六项，在分发与自身有效位置逐字一致。安装溯源 `.agents/corp/install.json` 保留 a3 初次信息，符合其仅作初始溯源的约定。通用检查只导入生成项目内既有 helper，使用标准库；两包仍分别携带，启动包未扩大范围。包外移除、已有根／项目编辑保护及 fake CLI 检查进入根测试；不据此宣称 runtime 登录、模型执行或真实项目采纳。
- **前置范围：** 保留 base 中 `docs/evidence/issue-3/README.md` 指向的阶段／沟通／换实例／审查复验材料。本次增量没有改写那些历史证据；既有显式审查承诺也未被删除。未重新验证真实 PR #4 最终集成状态或 CI，因此不替它做新的交付结论。

## Reviewer 实际执行的检查

- 冻结 HEAD/base、工作树、132 项 source manifest；六项分发／自身 owner 一致性。
- 只读真实 Issue #5，核对 OPEN、当前 Spec hash 与接受 permalink。
- `python3 scripts/check.py --base 15682e2d9ca77dfbd8234cadc803f35557d0f76c`：本地 Corp 检查通过，122 项 root unittest 通过。实际环境 Python 3.14.2；包含启动器既有测试，不将内含测试重复加总。
- 对新增检查逻辑的现有正反用例随根入口执行，覆盖 staged/unstaged/untracked 差量、失效基线、初始 push、PR 合成 checkout、手动／浅历史、链接失败与 helper 错误、可携带生成结果。
- B1 的额外真实生成项目负例及 native focus 函数对照，观察到错误绿灯。
- 补充准备后继 bundle 的精确候选复建及 13 项测试；失败后继 bundle 的 11 项测试和旧／新版本实际入口失败传播对照。复建与测试使用独立临时目录，未改变被审或消费者原树。

尚未执行／仍需保留：B1 修正后的独立复验；更正后的旧项目升级保护证据；最终候选在托管 PR CI 与默认分支实际集成版本上的运行，Python 3.9/3.13 CI 环境；真实 GitHub 并发、跨机、Owner 理解和业务效果。本次合成 API 与本地 Git 检查不替代这些证据。无发布权限或尚未发布不是源码缺陷，但适用交付验收只能在取得对应证据后完成。

报告只适用于上述固定源码对象及明确列出的补充消费证据。源 head、相关 Spec 或实际集成基线改变后，按影响复验；B1 清除后也不自动获得发布或合并授权。
