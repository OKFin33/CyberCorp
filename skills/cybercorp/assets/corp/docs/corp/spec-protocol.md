# Issue-as-Spec protocol

一个 GitHub Issue 默认同时承接本次结果约定和执行入口。Issue number 是身份，不再分配 SPEC／WI 双编号。
Spec 是 Issue 中受控的内容，不是必须另建的父对象。长期产品、Acceptance、架构和机器契约仍在 Git。

## Contract area

工作正文采用以下标记。Issue body 中只有一对独占行标记之间的内容是 Spec：

    <!-- spec:start -->
    ...本次结果、边界、验收和必需输入...
    <!-- spec:end -->

该区域至少包含：共享基线的确定 baseline_commit；目标／决定来源；本次 outcome 与范围；可观察验收和
直接验证；带版本的必需 Canon／技术输入；未知、外部影响、停止条件；需要长期保留的事实及其目标 owner。
仓内维护或调查可以没有业务 REQ／AC，但仍须有结果与证据，不以“维护”为由省略约定。

不复制未改变的 Canon。正文区域外可放导航、讨论摘要和非规范说明，进展、claim、checkpoint 在评论，
执行关系在 GitHub 原生字段。范围外文字不能引入新验收、放宽约束或改变规范；若有冲突，暂停对应工作并
把改变纳入 Spec／正确 Canon 后再接受。

## Content pin and acceptance

从 GitHub 重新获取当前 body 后执行：

```bash
python3 .agents/corp/spec-checkpoint.py issue-body.md
python3 .agents/corp/spec-checkpoint.py issue-body.md --check <sha256>
python3 .agents/corp/spec-checkpoint.py issue-body.md --checkpoint --issue <number> --source <decision-locator>
```

工具仅提取唯一 Spec 区，统一换行、去行尾空白／尾部空行并计算 SHA-256；不猜语义，不证明需求正确或输入
可得。区域缺失、重复、空白或顺序错误会失败。pin = Issue number + spec_sha256 + 接受评论 permalink。
Git baseline、内容 hash 和 GitHub 评论身份提供追溯，不再维护一套人工 revision 计数。

当输入可解析、必要决定有共享来源、未知不再改变本次结果且与进行中工作无未处理冲突时，由 Agent 发布：

    SPEC_ACCEPTED issue=<number> spec_sha256=<hash> source=<shared-locator>

这是就绪的内容锁，不是例行人工审批或 merge 授权。新的产品承诺、权限／外部影响决定不能由 checkpoint
伪造。Issue 创建不等于已接受；当前 Spec 区必须匹配有效接受评论，且 Issue 开放、没有撤销／替代该约定。
来源本身也须有效；失去 authority 的约定不能仅凭 hash 继续。

source 使用可共享的 HTTPS 定位符，例如同仓决定评论 permalink、当前目标 Milestone 或固定 commit 的
blob 链接；仓内文件不能只写相对路径或浮动分支来代替版本。生成器与读取器共用 source 语法检查，拒绝
非 HTTPS、缺 host、URL 用户名／密码、空白、控制字符和不安全包装字符。语法通过不证明可达、非敏感或
决定有效，发布者仍须核实共享范围与 authority，任何秘密都不得放入 URL。
已有不支持格式的接受评论不删改；核实同一决定和当前 Spec 后，用支持的 source 追加接受记录，不改 Spec
内容或伪造一次新产品决定。仅内容未变时保留 hash，引用新接受 permalink 的受影响消费者按本协议重核。

## Change and impact

- 改变 Spec 区使旧 pin 不匹配；先停止受影响写入，补齐决定／输入并发布新接受评论。
- 区域外的进度、链接整理、claim 或原生关系调整不改变 hash；它们不能偷偷改业务约定。
- 更新者必须检查实际影响到的子项、实现与 review，说明仍兼容还是需要返工／更新 pin；不机械让全部任务
  重新生成或全树退回草稿。需要更新的依赖 pin 必须在继续受影响工作前完成。
- 旧 pin 下的代码／检查保留为历史证据，不自动证明新约定成立。review 记录绑定实际 Spec pin 和 base/head。
- 原生依赖改变不必重写 Spec，但必须重新核验依赖是否满足以及有无循环；不能靠改边抹去验收。

## Split only when useful

确有独立并行、不同依赖或独立交接需求时才使用原生 sub-issues。父项拥有总体结果，子项拥有各自差量与
执行约定，并引用实际依赖的父 Spec pin；不能互相复制全文。原生 blocked-by／blocking 是唯一依赖 owner，
DAG 按查询结果派生，不再手写 blocked_by 正文或另一份 workset。

拆分关系不等于执行阻塞：只有真实前置才添加依赖。跨工作组不自动拆票；一个主责组可以组织端到端交付。
跨 Issue 的共享语义变化应有受控前置，写权限按实际冲突协调，不按目录机械切割。

## Finish or retire

执行历史损坏的例外接续只按 [claim-protocol](claim-protocol.md#damaged-history-recovery) 处理，
不能把取消原事项当实现完成，也不能用它绕过普通有效 claim。

- 单 PR 的完整实现可以关联并关闭该 Issue；多 PR 或父项只完成一部分时用非关闭引用。
- 关闭前核对整体约定、真实 merge／目标证据和需要长期保留的 Canon promotion。关闭原因是取消／重复／
  不计划时不能声明已实现。原生 closed 只说明关闭，不单独证明验收。
- 多 PR 不必有额外 final-integration 票；确有剩余实现才建。整体对照／证据收口留在原 Issue，不能为终止
  marker 制造空 PR。调查／统筹等非代码结果可用直接结果证据关闭，不制造代码合入。
- 需长期保留的事实随对应 PR 回到其 canonical path；Git 已集成而 Issue 尚未更新时先以实际共享基线核实现况，
  不重新实现旧差量。不再要求 SPEC_INTEGRATED／SPEC_SUPERSEDED 自定义终止 marker。
