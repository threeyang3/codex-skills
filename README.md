# 个人 Codex Skills

维护两个面向不同工作流的 Codex skill，包含指令、参考资料、模板及验证脚本。

| Skill | 适用任务 | 不应仅因以下需求而启动 |
| --- | --- | --- |
| [course-materials-to-notes](course-materials-to-notes/SKILL.md) | 整门课程的资料归档、逐讲学习笔记、既有笔记审校；用户明确要求时进行教材/讲义原文重建 | 单个概念解释、单道作业题或普通代码问题 |
| [homework-delivery](homework-delivery/SKILL.md) | 理论作业、编程作业、实验报告、结果核验与提交包整理 | 只询问概念、不需要完整作业交付的简短问题 |

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
└── homework-delivery/
    └── SKILL.md
```

## 安装与使用

克隆仓库后，将需要的 skill 完整目录复制到 `${CODEX_HOME:-$HOME/.codex}/skills/`。安装前检查目标是否已有同名目录；如有本地修改，先备份或比较差异，不要直接覆盖。课程 skill 依赖相邻模板、参考文件与脚本，不要只复制 `SKILL.md`。

在支持 skills 的 Codex 会话中，可以使用 `$course-materials-to-notes` 或 `$homework-delivery` 指定调用。调用时仍应提供任务材料和交付要求。

## 维护与测试

仓库是本机 skills 的独立副本，不会自动与安装目录同步。修改后应核对两处差异并通过 Git 记录版本。

课程资料验证器使用 Python 3.9+ 标准库。运行单元测试：

```sh
cd course-materials-to-notes
python3 -m unittest discover -s scripts -p 'test_*.py'
```

课程资料包可运行 `python3 tools/verify_pack.py .`。如需检查具体课程覆盖，使用从实际课程清单得出的 `--expected-notes` 和 `--expected-lectures` 参数；不要将某门课程的讲数写死为通用常量。结构测试不证明数学内容正确。

`homework-delivery` 包含个人作业偏好。对外分享前请检查个人信息与课程材料的使用权限；仓库可见性不替代原始资料的版权许可。
