# 个人 Codex Skills

维护七个面向不同工作流的 Codex skill，包含指令、参考资料、模板及验证脚本。

| Skill | 适用任务 | 不应仅因以下需求而启动 |
| --- | --- | --- |
| [course-materials-to-notes](course-materials-to-notes/SKILL.md) | 整门课程的资料归档、逐讲学习笔记、既有笔记审校；用户明确要求时进行教材/讲义原文重建 | 单个概念解释、单道作业题或普通代码问题 |
| [homework-delivery](homework-delivery/SKILL.md) | 理论作业、编程作业、实验报告、结果核验与提交包整理 | 只询问概念、不需要完整作业交付的简短问题 |
| [hpc-agent](hpc-agent/SKILL.md) | 通过共享 HPC Agent 提交、跟踪和恢复远程 GPU/HPC 任务 | 用户明确要求本地执行的任务 |
| [model-training](model-training/SKILL.md) | 在 HPC 上按官方训练配置准备、校验和执行模型训练，遵守 checkpoint 恢复约束 | 只做推理、评估、基准测试或普通数据处理 |
| [product-discovery-interview](product-discovery-interview/SKILL.md) | 新产品、大功能或需求不完整的重构；通过分轮提问补齐用户、流程、边界、异常和验收标准 | 已有明确复现步骤和验收标准的小修复、机械性改动 |
| [product-documentation](product-documentation/SKILL.md) | README、用户指南、快速开始、功能说明和发布文档；规划示例、镜头清单并核对文档与当前产品一致 | 单个代码注释、内部随手笔记，或尚未收敛的产品需求 |
| [product-demo-visuals](product-demo-visuals/SKILL.md) | 为真实运行的软件制作、筛选、裁切并验收高质量演示截图和视觉素材 | 只为证明程序运行的调试截图，或尚未实现功能的概念图 |

## 推荐的产品开发链路

对需求尚不完整的新产品或大功能，可以按需串联：

`product-discovery-interview` → 实现与验证 → `product-documentation` → `product-demo-visuals`

其中 `product-documentation` 负责决定文档面向谁、应讲什么以及需要哪些镜头；`product-demo-visuals` 负责把这些镜头实际拍好并进行视觉质量验收。小型、边界清楚的修改不应机械执行整条链路。

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
├── product-documentation/
│   ├── SKILL.md
│   └── agents/openai.yaml
└── product-demo-visuals/
    ├── SKILL.md
    └── agents/openai.yaml
```

## 安装与使用

克隆仓库后，将需要的 skill 完整目录复制到 `${CODEX_HOME:-$HOME/.codex}/skills/`。安装前检查目标是否已有同名目录；如有本地修改，先备份或比较差异，不要直接覆盖。课程 skill 依赖相邻模板、参考文件与脚本，不要只复制 `SKILL.md`。

在支持 skills 的 Codex 会话中，可以使用 `$course-materials-to-notes`、`$homework-delivery`、`$hpc-agent`、`$model-training`、`$product-discovery-interview`、`$product-documentation` 或 `$product-demo-visuals` 指定调用。调用时仍应提供任务材料和交付要求。

HPC 相关的 `hpc-agent` 和 `model-training` 依赖已配置的 SSH 别名 `h100-15` 及远端 `~/hpc-agent/bin/hpc-agent`。本仓库只保存 skill 指令、界面元数据及配套参考文档，不包含远端程序、SSH 配置、任务数据库或凭据。

这两个 Skill 的**上游源仓库**为 [threeyang3/hpc-agent](https://github.com/threeyang3/hpc-agent) 的 `skills/` 目录。当前 `hpc-agent` 已与上游一致，本次同步补齐 `model-training`（含 `references/`）；此处为独立副本，后续上游更新需要再次同步，不能假设自动同步。

**能力限制：** `model-training` 中描述的无人值守 checkpoint 自动恢复尚未由远端 CLI 完整实现；实际恢复需经验证 checkpoint 后人工显式执行，不得把 Skill 指令视为已经部署的自动恢复服务。

## 维护与测试

仓库是本机 skills 的独立副本，不会自动与安装目录同步。修改后应核对两处差异并通过 Git 记录版本。

课程资料验证器使用 Python 3.9+ 标准库。运行单元测试：

```sh
cd course-materials-to-notes
python3 -m unittest discover -s scripts -p 'test_*.py'
```

课程资料包可运行 `python3 tools/verify_pack.py .`。如需检查具体课程覆盖，使用从实际课程清单得出的 `--expected-notes` 和 `--expected-lectures` 参数；不要将某门课程的讲数写死为通用常量。结构测试不证明数学内容正确。

`homework-delivery` 包含个人作业偏好。对外分享前请检查个人信息与课程材料的使用权限；仓库可见性不替代原始资料的版权许可。
