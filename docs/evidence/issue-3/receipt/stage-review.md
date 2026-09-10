# Receipt Desk 独立阶段审查

结论：固定候选可审查，但不满足 Stage 1 验收。已确认一个验收阻塞 B1：`receipt_desk.py:57` 使用 `sorted(totals, reverse=True)`，导致多分类摘要倒序，违背 product.md、Issue 11 Spec、Issue 7 保留要求和 README 的字母顺序契约。未发现其他验收阻塞。未改候选，未 merge，未关闭阶段。

## 独立性与恢复路径

实例 `aid-v1-4f7882cc-0713-4b6f-86b9-d83c17e81266` 未参与实现。只从 `/tmp/corpo3-stage-review` 恢复项目，未读取 CyberCorp 源仓、其他代理报告或父代理历史。读取顺序：AGENTS.md / README.md → docs/corp/README.md → product.md / canon-map.yaml → development-loop.md → 项目内 review-corp/SKILL.md → spec-protocol、milestone-delivery、coordination、claim-protocol。使用 `PATH="$PWD/tools:$PATH"` 下离线 gh / repo-context 发现 Milestone 1 与唯一协调 Issue 11，再读取完整分页评论、Issue 7/8、PR 22 及 reviews。

首个原生全局观察开始：2026-09-09T18:45:33.523461+00:00。审查占用：Issue 11 评论 21，2026-09-09T18:46:15.626110+00:00，租约到 19:06:15.489866+00:00。完成释放复核：2026-09-09T18:48:43.982909+00:00。以上均为实际本地 UTC；未使用虚构经过时间。

## 固定对象与授权

- Base / main：`7f64ffdea6c921a7b90d5cbdee2057563762915a`。
- Head：`565c3944438fc431fa8d23d44d89797fa108d4f4`，PR 22 / `codex/receipt-stage-candidate`。
- 同一 bare 仓 `/tmp/corpo3-receipt-shared.git` 的实际 clone remote 名为 `origin`。首次 `git ls-remote shared` 因无此别名失败；读取 remote 后以 `git ls-remote origin` 成功验证 base/head，没有修改配置。merge-base 等于 base。
- Issue 11 Spec SHA：`adb48b9e053b931336c8b32f49c44d1ccc8e7fe7b01712c95b06e1eecda2f878`，接受评论 8。
- Issue 7 Spec SHA：`b9984f6f2aa122f1818663e2193bf9128a5dc42713179aef4159e2e8f168cdab`，接受评论 9。
- 两个 Spec 均以项目 helper 校验。原生完整评论中的合成 Owner 回复为 Issue 7 评论 7；退款决定已采用到候选 product.md。评论 20 固定当前较新候选，祖先 `131414ea2ec063b880e2d1bce20d0c516e5d98c6` 的 11 测试通过记录没有迁移到当前 head。
- Stage 1 要求工作 CLI 场景与独立整体判断；没有 merge 或后续阶段授权。Issue 8 的未来持久存储审查承诺保留，当前不触发。JSON 输出建议未接受，不扩大范围。

## 检查和发现

Python 3.14.2 上执行 `python3 -m unittest discover -s tests`：11 项，4 项失败，均为输出顺序。涉及 quoted Unicode、正数分币 rounding、退款负净额/零分类和负数 rounding 场景。`git diff --check` 通过。

另行运行 10 个实际 subprocess CLI 场景：字母顺序复现失败；其余 9 项通过，覆盖 quoted Unicode 精确加法、退款负净额、零分类保留、负数 half-even、精确求和后 rounding、合法行后非法金额无 stdout、破损 CSV 无 stdout、空输入及 UTF-8 文件的换列/额外列/空格处理。逐行审阅 63 行 app、tests、README 与 product。应用只使用标准库、内存聚合、文件/stdin 输入与 stdout 输出，未发现上传或持久存储路径。

B1 最小复现：

```csv
category,amount
Banana,2
Apple,1
```

实际 exit 0、stderr 空、stdout 为 `Banana,2.00\nApple,1.00\n`；预期为 `Apple,1.00\nBanana,2.00\n`。第 57 行倒序排序是相对祖先候选唯一 app 变化。影响所有含多个不同分类的摘要，属于 P2 缺陷及明确阶段验收阻塞。修复应回到现有阶段工作，发布精确新 head，独立复查字母序、quoted Unicode、退款以及必要全阶段测试链；不应改弱测试或改写已接受排序要求。

原生 check-runs endpoint 在此离线替代工具不支持，CI 未验证；没有把本地测试当成远程 CI。未测试/未证明真实 GitHub、真实网络、用户使用价值、Owner 理解、真实 runtime 集成或阶段交付。

## 原生动作与后续

- Claim：Issue 11 评论 21，完整分页回读确认持有。
- PR Review：https://github.com/fixture/receipt-desk/pull/22#pullrequestreview-22，id 22，`CHANGES_REQUESTED`，绑定当前 head；时间 2026-09-09T18:47:46.823340+00:00。
- 整体阶段结论：https://github.com/fixture/receipt-desk/issues/11#issuecomment-24，评论 24；包含冻结的 Milestone 1 快照、完整独立 CLI 输入/输出和验收边界，时间 2026-09-09T18:48:43.387756+00:00。
- Checkpoint：Issue 11 评论 25，时间 2026-09-09T18:48:43.653542+00:00。
- Release：Issue 11 评论 26，时间 2026-09-09T18:48:43.938994+00:00。回读确认 current_claim=null 且无 rejected_events。

阶段仍未交付。下一步是现有 Issue 11 范围内修复 B1、发布精确修正候选并取得非实现者复查；之后仍需具体 PR/head/checks/method 的 merge 授权和实际集成。无须另造审查 Issue、JSON 功能或后续阶段。

最终 Git HEAD 与固定对象一致，tracked source 无变更。`git status --short` 为：

```text
?? .scenario
```

`.scenario` 是提供的共享离线状态链接；应用、测试、Canon、生成方法均未修改。原生记录均由离线 API 正常发布，未直接编辑 state.json。所有结论只覆盖此离线合成环境。
