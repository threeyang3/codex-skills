# 个人 Codex Skills

维护两个用于不同任务的 Codex skill：一个负责课程资料库与学习笔记，一个负责具体作业求解、实验报告和交付。请按任务目标选择，不要将它们当作所有学习问题的通用入口。

| Skill | 适用场景 | 不适用场景 |
| --- | --- | --- |
| [course-materials-to-notes](course-materials-to-notes/SKILL.md) | 多讲课程资料归档、学习笔记、原文重建、既有课程笔记审校 | 普通概念问答、独立作业求解 |
| [homework-delivery](homework-delivery/SKILL.md) | 理论作业、编程作业、实验报告、提交包整理 | 整门课程资料库、普通概念问答 |

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

将所需 skill 的完整目录复制到 `${CODEX_HOME:-$HOME/.codex}/skills/`。安装前先检查目标是否已有同名目录，备份后再按需更新，避免覆盖本机尚未同步的修改。课程 skill 还依赖相邻的模板、参考文件和脚本，不要只复制 `SKILL.md`。

在支持 skills 的 Codex 会话中，可使用 `$course-materials-to-notes` 或 `$homework-delivery` 指定调用。Skill 描述用于任务路由，但实际调用后仍应依据本次任务选择适当模式。

## 验证

课程 Skill 的验证器测试：

```sh
cd course-materials-to-notes
python3 -m unittest discover -s scripts -p 'test_*.py'
```

验证器可复制到课程资料包的 `tools/verify_pack.py`，在资料包根目录运行：

```sh
python3 tools/verify_pack.py .
```

脚本检查清单结构、文件与哈希、笔记讲次覆盖、部分本地链接和公式定界符；它不验证数学结论、不检查所有 Markdown 方言，也不替代目标阅读器中的实际公式渲染检查。

## 维护

仓库是本机 skills 的版本来源副本，不会自动与安装目录同步。修改后应检查差异，再同步到另一处并通过 Git 提交记录版本。避免无条件覆盖安装目录中的本地修改。

`homework-delivery` 不在 Skill 文本中硬编码姓名和学号。需要署名时使用用户当前指示或本机作业配置；对外分享前仍应检查提交历史与个人文件。

