# 个人 Codex Skills

维护十二个面向不同工作流的 Codex skill，包含指令、参考资料、模板及验证脚本。

| Skill | 适用任务 | 不应仅因以下需求而启动 |
| --- | --- | --- |
| [course-materials-to-notes](course-materials-to-notes/SKILL.md) | 整门课程的资料归档、逐讲学习笔记、既有笔记审校；用户明确要求时进行教材/讲义原文重建 | 单个概念解释、单道作业题或普通代码问题 |
| [homework-delivery](homework-delivery/SKILL.md) | 理论作业、编程作业、实验报告、结果核验与提交包整理 | 只询问概念、不需要完整作业交付的简短问题 |
| [hpc-agent](hpc-agent/SKILL.md) | 通过共享 HPC Agent 提交、跟踪和恢复远程 GPU/HPC 任务 | 用户明确要求本地执行的任务 |
| [model-training](model-training/SKILL.md) | 在 HPC 上按官方训练配置准备、校验和执行模型训练，遵守 checkpoint 恢复约束 | 只做推理、评估、基准测试或普通数据处理 |
| [product-discovery-interview](product-discovery-interview/SKILL.md) | 新产品、大功能或需求不完整的重构；通过分轮提问补齐用户、流程、边界、异常和验收标准 | 已有明确复现步骤和验收标准的小修复、机械性改动 |
| [agent-goal-brief](agent-goal-brief/SKILL.md) | 把已经明确的产品/工程目标转成可交给长程 Agent 独立执行的任务书，包含基线、写入边界、防作弊验收、变更控制、止损与断点续跑 | 产品目标仍未收敛，或当前会话能快速完成的小修复 |
| [product-documentation](product-documentation/SKILL.md) | README、用户指南、快速开始、功能说明和发布文档；规划示例、镜头清单并核对文档与当前产品一致 | 单个代码注释、内部随手笔记，或尚未收敛的产品需求 |
| [product-demo-visuals](product-demo-visuals/SKILL.md) | 为真实运行的软件制作、筛选、裁切并验收高质量演示截图和视觉素材 | 只为证明程序运行的调试截图，或尚未实现功能的概念图 |
| [project-closeout](project-closeout/SKILL.md) | 开发/发布结束后，对齐产品合同、代码、运行态、README/docs、截图、AGENTS.md/规则和工作区残留，形成唯一现役答案 | 普通编码任务，或未经确认的破坏性清理 |
| [manga-organize](manga-organize/SKILL.md) | 整理指定漫画文件，制作 CBZ、标注书目与章节并验收，可按要求归档百度网盘 | 只需管理漫笺中的现有条目 |
| [manjian-library](manjian-library/SKILL.md) | 查找和整理漫笺书库，或从百度网盘登记漫画 | 只需转换、打包或标注漫画文件 |
| [mediabase-maintenance](mediabase-maintenance/SKILL.md) | 维护 Obsidian MediaBase 文娱库与 Media Core 插件，核对归档、迁移和界面 | 其他 Obsidian 库或无关插件 |

## 推荐的产品开发链路

对需求尚不完整的新产品或大功能，可以按需串联：

`product-discovery-interview` → `agent-goal-brief` → 实现与验证 → `product-documentation` / `product-demo-visuals` → `project-closeout`

小型、边界清楚的修改不应机械执行整条链路。Skill 的职责按“谁做决定、谁提供证据”划分：

| 阶段 | 主要产出 | 下游应直接继承 |
| --- | --- | --- |
| `product-discovery-interview` | `D-xx` 决策、`A-xx` 假设、`Q-xx` 未决问题、`AC-xx` 验收标准、首版范围 | 不重新询问已确认产品决定；blocking Q 不得被执行 Agent 擅自拍板 |
| `agent-goal-brief` | 任务与 AC 映射、实测基线、写入白名单、验收证据要求、变更控制、止损条件 | 实现不能静默修改产品合同；完成后保留 `AC → 实现 → 证据 → 限制` |
| `product-documentation` | 面向读者的现役文档、能力事实映射、截图镜头清单 | 文档只写当前已验证能力；镜头清单明确 `shot id`、状态和目标显示尺寸 |
| `product-demo-visuals` | 可重拍截图、捕获条件、质量结论 | 截图必须来自真实产品，并在最终显示尺寸下复核 |
| `project-closeout` | 产品合同→实现→验证→运行态→文档/截图/规则的闭环状态 | 只把已验证事实标成 closed；删除候选先汇报再清理 |

### 工作流约定

- **已有答案不重复问。** 上游已经确认的产品决定应被下游引用，而不是换一种措辞重新访谈。
- **每次交接都带证据。** “做完了”不能代替 `AC → 实现位置 → 验收方式/结果`。
- **实现发现不等于产品决定。** 库限制、架构偏好或代码现实如果会改变用户合同，必须显式返回裁决，不允许静默改需求。
- **文档和截图描述当前产品，而不是理想产品。** 规格与实现有差异时，差异本身要被记录。
- **截图是可维护资产。** 重要截图要知道怎么重新进入状态、用什么 viewport、放到文档多宽；原图清楚但实际文档里看不清也算失败。
- **收尾检查可恢复性。** 下一次 Codex 会话应能只靠仓库现役文件继续，不依赖本次聊天记录中的隐藏知识。

## 目录

```text
.
├── README.md
├── course-materials-to-notes/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── assets/lecture-note-template.md
│   ├── references/
│   └── scripts/
├── homework-delivery/
│   └── SKILL.md
├── hpc-agent/
│   ├── SKILL.md
│   └── agents/openai.yaml
├── model-training/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
│       ├── official-defaults.md
│       └── recovery.md
├── product-discovery-interview/
│   ├── SKILL.md
│   └── agents/openai.yaml
├── agent-goal-brief/
│   ├── SKILL.md
│   ├── UPSTREAM.md
│   └── agents/openai.yaml
├── product-documentation/
│   ├── SKILL.md
│   └── agents/openai.yaml
├── product-demo-visuals/
│   ├── SKILL.md
│   └── agents/openai.yaml
├── project-closeout/
│   ├── SKILL.md
│   ├── UPSTREAM.md
│   └── agents/openai.yaml
├── manga-organize/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/
│   └── scripts/
├── manjian-library/
│   └── SKILL.md
└── mediabase-maintenance/
    ├── SKILL.md
    ├── agents/openai.yaml
    └── references/
```

## 用 CC Switch 安装和更新

1. 在 CC Switch 的 **Skills → 仓库管理** 添加并启用 `threeyang3/codex-skills`，分支填 `main`，目录留空，从仓库根目录发现 skill。
2. 安装新 skill 时，打开 **Skills → 发现**，点击 **刷新仓库**，搜索 skill 名称。在 **安装到** 选择 **Codex**，再点击 **安装**。
3. 更新已安装的 skill 时，在 **Skills** 中选择 **检查更新**，选中要更新的条目并确认。若预期的更新未出现，先确认改动已进入 GitHub 的 `main`，再核对安装来源。
4. 在 **已安装** 中确认条目的来源为 `threeyang3/codex-skills`，且 **Codex** 已启用。若同名条目显示为「本地导入」，先把需要保留的改动合入仓库，再卸载该条目并从 **发现** 页安装仓库版本。

在支持 skills 的 Codex 会话中，输入 `$` 加上表中的 skill 名称即可指定调用，例如 `$manga-organize`。调用时提供任务材料和交付要求。

HPC 相关的 `hpc-agent` 和 `model-training` 需要可用的 SSH 连接和已部署的远端 HPC Agent CLI。具体前提见对应的 `SKILL.md`。

这两个 Skill 的**上游源仓库**为 [threeyang3/hpc-agent](https://github.com/threeyang3/hpc-agent) 的 `skills/` 目录。当前 `hpc-agent` 已与上游一致，本次同步补齐 `model-training`（含 `references/`）；此处为独立副本，后续上游更新需要再次同步，不能假设自动同步。

`agent-goal-brief` 与 `project-closeout` 分别改编自 [KKKKhazix/khazix-skills](https://github.com/KKKKhazix/khazix-skills) 的 `leader` 与 `neat-freak`。上游为 MIT License；各 Skill 目录中的 `UPSTREAM.md` 保留了来源、审阅 commit 和完整许可声明。本仓库没有原样复制上游全部平台特定逻辑或 eval fixtures，而是按当前 Codex 工作流做了收敛适配。

**能力限制：** `model-training` 中描述的无人值守 checkpoint 自动恢复尚未由远端 CLI 完整实现；实际恢复需经验证 checkpoint 后人工显式执行，不得把 Skill 指令视为已经部署的自动恢复服务。

## 发布新建或修改的 Skill

GitHub 的 `main` 是 CC Switch 的更新来源。在仓库工作副本中编辑和提交，发布后通过 CC Switch 同步到 Codex。CC Switch 更新会用仓库内容替换安装副本，请先把要保留的修改合入 Git。

1. 有仓库写权限时，先进入 `codex-skills` 工作副本，检查并处理未提交的改动，再同步 `main`。首次贡献可先克隆仓库。

   ```sh
   git status --short --branch
   git switch main
   git pull --ff-only origin main
   ```

2. 新建 skill 时，在仓库根目录添加同名目录，放入 `SKILL.md` 和所需的脚本、模板或参考资料，并在 README 中登记。修改已有 skill 时，编辑对应目录。
3. 提交前核对 `SKILL.md` 的 `name`、`description`、相对链接和配套文件，运行相关本地检查。只暂存本次要公开的文件，确认差异中没有凭据、个人信息或私有资料。
4. 提交并推送到 `main`。以下以修改 `manga-organize` 为例，如果同时修改了 README，也将其暂存。

   ```sh
   git add -- manga-organize/
   git diff --cached --check
   git diff --cached
   git commit -m "Update manga-organize skill"
   git push origin main
   ```

   使用 PR 时，合并到 `main` 后再按上面的步骤安装或检查更新。

## 测试

课程资料验证器使用 Python 3.9+ 标准库。运行单元测试：

```sh
cd course-materials-to-notes
python3 -m unittest discover -s scripts -p 'test_*.py'
```

课程资料包可运行 `python3 tools/verify_pack.py .`。如需检查具体课程覆盖，使用从实际课程清单得出的 `--expected-notes` 和 `--expected-lectures` 参数；不要将某门课程的讲数写死为通用常量。结构测试不证明数学内容正确。

`homework-delivery` 包含个人作业偏好。对外分享前请检查个人信息与课程材料的使用权限；仓库可见性不替代原始资料的版权许可。
