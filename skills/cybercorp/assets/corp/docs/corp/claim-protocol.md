# Execution and recovery protocol

本协议管理一次有界执行，不另建人员系统。适用于实现、调查和需要独立承接的统筹；Issue 的结果约定
见 spec-protocol。PR review 另在固定 PR 对象记录独立结论，不要求给每次 review 造子票。

## Readiness and identity

开工先验证当前 Spec pin、必需输入、原生依赖与实际执行冲突。依赖项被关闭不等于依赖满足：核对关闭
原因、对应成果和证据。迁移事项可在授权环境处理旧 owner，但其输入边界必须明确，不能把例外传给产品实现。

- 项目可按需要标明持续责任和上下文路由；不要求预设工作组或人员表。
- agent_instance_id 使用运行时可提供的唯一 ID；无此能力时运行 `python3 -c 'import uuid; print("aid-v1-" + str(uuid.uuid4()))'`。
  ID 不编码项目、机器、任务或先后；aid-v1 仅为该生成格式版本，不代表身份认证或职级。
- ID 从第一次 claim／review 起稳定使用。新实例生成新 ID；压缩后只有仍是同一执行且持有权有效时才能沿用。
- 实现者不能改名作为独立 reviewer；同组／同模型可独立审查，但必须是未参与实现的另一实例。

## Shared execution events

执行记录是同一 Issue 的追加评论，不反复覆盖 Issue body。每条机器事件只有一个 JSON fence：

```agent-event
{"event":"claim","instance":"aid-v1-example","lease_until":"2026-09-05T23:00:00Z","base_commit":"0000000000000000000000000000000000000000","branch":"feat/example","scope":["docs/corp/"]}
```

上例仅为形状，不是可用认领。lease_until 必须明确、晚于发布时刻，并说明与本次有界工作相称的执行安排；
目前不规定 60 分钟或 8 小时默认值。后台长检查跨越到期点时须提前有效续期或 checkpoint／释放。

事件种类：

| event | 必需字段（另加 instance） | 意义 |
|---|---|---|
| claim | lease_until, base_commit, branch, scope | 申请当前事项的执行占用；无代码时 branch 可为 null |
| renew | claim, lease_until | 引用有效 claim 评论 ID，必须在其到期前发布 |
| checkpoint | claim, recovery | 引用有效 claim，保存下述恢复对象 |
| release | claim, checkpoint, reason | 引用本次有效 claim 的恢复评论 ID，释放执行占用 |

事件时间与排序来自 GitHub 服务端 created_at 和评论 ID，不相信正文自报 claimed_at。claim 是评论 ID，
不是实例 ID；每次重新认领产生新 claim。renew／checkpoint／release 必须匹配当前 claim 和 instance。
晚到的旧实例事件不取得权威；未延长有效期的 renew 作为无效迁移记入拒绝列表，不改变持有权，允许随后
在有效期内追加正确续期。普通讨论中行内提及或引用 fence 不算事件，机器 fence 必须独占行。
删除或编辑已有机器事件会破坏重放依据，禁止；纠正用新评论并显式处理影响。结构损坏、服务端顺序矛盾
或记录被修改属于完整性错误，仍停止冲突范围，不能当作正常续期或完整历史。
被拒绝但可重放的迁移（如未延长的 renew）可正常追加纠正；完整性错误不能靠追加合法事件消除，
仅在确认不是取数／时钟故障后，按下述 [损坏历史恢复](#damaged-history-recovery) 处理。

读取完整、未遗漏页的评论，使用以下纯读取工具派生当前执行者、恢复点和被拒绝的旧事件：

```bash
python3 .agents/corp/work-state.py comments.json --at <trusted-UTC-time>
```

输入是 REST comments 数组或分页数组。时间必须可信；工具不连接 GitHub、不验证凭据主体、不证明输入
完整或产物可达。它是重放校验器，不是分布式锁、排程器或自动接管服务。

## Claim and concurrency

近期工作供给／跨事项排序先完成 development-loop 的 **Declare before coordinating**：收敛到同一原生
Issue 后才使用以下单事项 claim 协议。单事项 claim 不仲裁另一 Issue 的持有权，也不覆盖跨事项语义冲突。

1. 核验 Issue／Spec、原生依赖及相关进行中事项，检查同一工作、语义或共享资源是否冲突。
2. 若已有有效 claim，不抢占；过期且无有效续期或已经释放时，先检查最后恢复点与现有 PR，再申请接续。
3. 发布 claim 后重新读取完整评论，确认当前有效 claim 是自己的评论 ID；在新一段写入、续期、push、
   handoff 和交付前再次核验。竞争按服务端顺序的首个有效 claim 收敛，失败者停止冲突写入。
4. GitHub 评论不是原子 lease 服务。读不到完整／最新记录、时钟不可信、事件被改删或观察互相矛盾时，
   停止冲突范围并协调，不把一次 read-after-write 称为严格排他保证。
5. 一个 branch/worktree 同时只有一个写入实例。scope 描述预期改动边界，不是自动目录锁；跨 Issue 的
   真实语义冲突仍要核对。不同工作树改同一文件不自动阻塞整个目录，分组也不构成代码禁区。
6. 到期无有效续期可按共享依据接管，不另请示 Owner；旧实例恢复须停止失效执行。不得删除前任工作树、
   force-push 或覆盖未确认成果来接管；从最后共享 commit 建立继任者独立工作树／分支。

普通先后和资源冲突由当前统筹职责协调；缺少可判定依据时可由另一实例承接有界协调。不能自主解决的
目标／权限决定交 Owner。每次 merge 的单次授权不因接管或统筹身份而改变。

## Damaged history recovery

仅适用于完整读取后仍无法重放的历史，不适用于有效竞争、普通到期、等待、网络／权限失败或失效 Spec。
保留坏记录，不能删改、过滤历史后重放成有效占用、放宽校验或向坏流追加伪 release。恢复是一次有界
协调，不新增 reset 事件、恢复登记库或永久岗位；安全条件不明时继续停止冲突范围。

1. 先复核取数完整、时间与具体损坏；在原 Issue 用普通追加评论记录证据和暂停范围。先查已有恢复承接、
   替代去向、关联 PR 和原生关系；用普通评论说明本次恢复承担者并重读确认。存在多个接续提案或无法
   确认唯一协调承接时先消除冲突，不并发创建／激活多个替代项，不从坏流申请新的实现 claim。
2. 核验旧持有者已停止，或有完整可信的独立证据表明冲突执行已结束；将依据留在共享评论。
   重放失败、Issue closed、正文自报到期或仅等待一个猜测的租期都不证明这一点。不能确认时停止并协调；
   需要执行环境／权限决定才交 Owner，不为正常可判定恢复增加例行审批。
3. 从原完整记录、真实 Git／PR／CI 核对已有成果。损坏前的 checkpoint 只是待核实线索，不是自动恢复权；
   实际验证 commit 在远端可取得、产物可读、当前 Spec／决定和剩余结果，列清未保存成果与未知。
   必需产物或执行权无法核实时不恢复实现；不得丢弃旧工作树、force-push 或重做已完成结果。
4. 确有剩余工作时复用已确认的唯一 successor，或创建一个普通替代 Issue，仅约定剩余结果、共享基线的确定
   baseline_commit 及必需输入；将未合入的恢复 commit 单独作为带版本输入／工作树起点，不冒充共享基线。
   新 claim 的 base_commit 填该执行实际起点。引用原 Spec pin、已核实成果和故障证据。
   按 development-loop 完成实际焦点的发现归属；
   双向普通评论记录旧／新 Issue 与替代原因。此时仍是恢复准备，不发布 successor 的执行 claim。
5. 核对所有受影响的父子项、blocked-by／blocking、消费者 pin 与 PR。先让下游保留阻塞并建立指向真实
   剩余结果的新依赖，再解除旧边；有循环、权限失败或不完整转接则暂停受影响消费者与后继实现。
   已有 PR 可保留并更新 Issue／Spec 引用；若须继续编码，使用自己的分支／工作树和相应 PR，保留旧 PR
   的替代与成果指针。不能让原 Issue 的关闭自动表示依赖已满足，或让旧关闭关键字提前核销新约定。
6. 核验转接完整、唯一去向与冲突执行停止，按 spec-protocol 接受后继约定，更新真正受影响的消费者 pin／
   PR review 对象。原 Issue 以 `not_planned` 关闭并说明被替代，不记 completed；关闭／网络结果不确定先
   读取真实状态，不盲重试。两侧共享记录确认恢复准备已收口后，才在后继事项按正常协议发布新 claim，
   重新读取完整评论并验证新占用，在自己的分支从已核实 commit 接续，发布新的共享 checkpoint。

原 Issue 与原事件保持历史，即使再读仍是 incomplete；后来实例沿普通评论的去向读取后继，不将旧流当
新的执行依据。新 claim 不继承旧 claim／lease、检查适用性或 merge 授权。每次关键写入仍重核事项是否
开放、Spec／关系及冲突；旧实例回归只能重新进入共同入口，不能继续被暂停或替代的执行。
若成果实际已完整，不创建空后继或空 PR：停止旧执行后在原 Issue 留真实验收证据，按正常完成规则核销；
坏历史仍不因此变为有效执行日志。

## Recovery checkpoint

recovery 至少包含：

```json
{
  "commit": null,
  "branch": null,
  "artifacts": [],
  "done": "已完成的结果或明确尚无产物",
  "checks": [],
  "remaining": "未完成、失败或待核实内容",
  "next": "下一安全动作及停止条件",
  "waiting_on": []
}
```

代码成果：commit 固定到已共享 feature 分支；无代码成果：artifacts 指向 Issue／PR 等可共享结果，或在
上文字段明确无成果。Spec pin 放在当前事项及关联 PR，不复制正文。checks 引用命令／运行及结果，不以
“检查过”代替证据。waiting_on 记录具体阻塞、所等输入和恢复条件，而不是另一套工作状态机。

在有阶段价值成果、关键选择／失败排除、路线改变、显式交接以及进入等待时保存；不要只等压缩提示或
准备 merge。只保存影响接续的结论／理由，不逐步转存思考、不制造 Manager 记忆库。

只存在本地工作树或未推送 commit 的成果不算跨机器可恢复。网络不可用时可保存本地，但必须披露损失
风险，不能发布声称共享成功的 checkpoint。工具只检验形状；发布者与接替者须实际核验产物可读、commit
在远端可取得。恢复成本与近期未保存工作成正比，当前没有已验证的量化损失上限。

## Wait, review and integrate

实现已无法继续、等待 review／merge／外部输入时：发布 checkpoint，写 release 并保留等待原因、责任
落点和 PR。释放不撤销 Spec、不重新 ready、不允许重做已提交实现。恢复条件成立后只认领实际剩余工作。

review 的记录至少含 reviewer instance、未参与实现声明、实际 base/head、Spec pin、检查范围
和结论。同组／同模型均可；共享语义变化补受影响方视角，不按组数强制多名 reviewer。参与过实现的实例
只能自审，不能用分开写两轮评语替代独立审查。代码 head 或相关 Spec 改变时重新检查；集成 base 变化时
重新核验兼容性与所需检查，不把旧组合的绿色结果当新组合证据。

merge 前读取真实 PR/head/检查，取得 Owner 当次授权后只执行一次；执行结果不确定时先查真实 GitHub／Git
结果，不盲重试。成功后对照 Issue 验收和目标缺口。其他外部动作同样先核实已发生结果，恢复不授予重复
付款、通知、真实设备操作等权限。
