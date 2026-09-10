# Inventory library consumer report

本次结果：从本项目入口选择 Issue #6，实现了可由其他 Python 程序直接导入的库存文件库，完成行为检查与共享候选交接。未将自检视为独立审查或阶段交付。

## 实际选题依据

恢复顺序为 AGENTS.md、README.md、product.md、.scenario/README.md、docs/corp/README.md、canon-map.yaml、development-loop.md 和本项目 work-corp 方法，再读取原生 Milestone/Issues/评论与版本化输入。

product.md 明确库存文件库本身就是产品；初始项目没有应用实现，仅有 CSV 示例检查。Issue #6 已接受且没有活跃领取、依赖或既存 PR，其协议直接覆盖真实产品结果。Issue #8 是贡献者命令文档，Issue #9 是示例诊断改进，均不能替代缺失的库。因此直接推进 #6，没有另造产品界面、CLI 或服务。

协议固定：Issue #6；spec_sha256=05254ec36c91071580cc72e49527a36f4403b403712cf7aaba26873a996bb9f2；接受评论 https://github.com/fixture/receipt-desk/issues/6#issuecomment-1；基线 b66b48cc9e28e9d17639406a17bc609ff80b2a9a。

## 工作产物

提交：5331b0bbab3ece9e94ddac3fe24def2ddf7a2180。

- inventory.py：load(path)、save(path, document)、validate(document)、InventoryError；UTF-8 JSON v1 校验、唯一 ID、完整验证后同目录临时文件原子替换。
- tests/test_inventory.py：10 项库行为测试，含多组非法文档子案例；原有 tests/test_inputs.py 保留，共 11 项。
- README.md：实际调用例子、返回值/异常约定、路径要求和边界、真实测试入口。

普通工程选择：拒绝额外字段、重复 JSON 键和不可编码为 UTF-8 的字符串；版本必须是整数 1；允许空库存，保留非空字符串中的空白，ID 大小写敏感。

## 检查与证据

所有项目命令都显式在 /tmp/cybercorp-issue5-library-v1 执行；仅使用 Python 标准库，Python 3.14.2。

- python3 -m unittest discover -s tests：固定提交上 11 项通过，证据 .scenario/behavior-check.txt。
- python3 .agents/corp/check.py --base b66b48cc9e28e9d17639406a17bc609ff80b2a9a：通过，实际检查三文件差异、路由与 helper；证据 .scenario/corp-check.json。远程路由由此检查保持未验证。
- 另一个 Python 调用程序从 inputs/inventory.csv 读取两条记录，导入库保存/加载 JSON，然后尝试重复 ID 保存，验证旧文件字节不变：通过，证据 .scenario/caller-check.json。这里是实现者执行的调用冒烟，不是独立实例验收。
- git diff --check：通过；最终跟踪工作区干净。
- git ls-remote shared refs/heads/codex/inventory-library：精确匹配候选提交，已验证本地 bare Git 的共享可达性。
- 重新读取原生 PR #21，确认 open、未 merged、head 等于候选 SHA；全局 repo-context 的 open_pull_requests 可发现 PR #21。按 Issue 的 PR 投影列表为空，显式 checkpoint/PR 链接及全局入口提供恢复路径。

## 共享恢复入口

本地 bare remote：/private/tmp/cybercorp-issue5-library-v1-shared.git。
共享分支：shared/codex/inventory-library，提交 5331b0bbab3ece9e94ddac3fe24def2ddf7a2180。
离线 PR：https://github.com/fixture/receipt-desk/pull/21。
Issue 检查点：https://github.com/fixture/receipt-desk/issues/6#issuecomment-6。
领取 #4 已由 release 评论 #7 释放；最终重放 current_claim=null、rejected_events=[]。

从项目 Corp 入口运行 PATH="$PWD/tools:$PATH" python3 .agents/corp/repo-context.py --repo fixture/receipt-desk，读取 Issue #6 检查点和 PR #21，然后从 shared 拉取并核验上述提交。README 与行为测试均在共享提交中，不依赖本地报告或生成时上下文。PR 与检查点记录准确命令、版本、结果和下一步。

已在 Issue #8 评论 #5 回写共享前提变化：候选 README 和测试入口已包含真实库行为；主分支尚未集成，后续编写贡献者命令应先恢复候选结果。未更改 #8 协议或提前关闭它。

## 未完成与边界

独立审查、CI、主分支集成、正式阶段验收与真实用户采用均未验证。本次未执行 fixture main 更新，Issue #6 和 Milestone 保持 open。下一实例应使用 development-loop / milestone-delivery 形成适用的独立阶段审查，非实现者评估固定库候选，再继续集成和阶段交付。本实例没有启动其他 Agent，也没有自签独立审查。

Issue #8、#9 仍未完成。保存不提供多写者锁或断电持久化保证；这些不属于本次格式契约。所有原生记录通过替身 gh api 操作，没有直接修改原生状态文件、真实网络调用或真实 GitHub 发布。此报告及运行证据保留在被忽略的 .scenario/ 内；共享恢复所需的结果和结论已写到 Git、PR 与 Issue 检查点。
