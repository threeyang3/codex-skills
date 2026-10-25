# 个人 Codex Skills

保存和维护本机自建的两个 Codex skill，包含指令、参考资料、模板及脚本。

| Skill | 用途 |
| --- | --- |
| [course-materials-to-notes](course-materials-to-notes/SKILL.md) | 整理课程资料，生成按讲次递进的学习笔记，核验内容并按要求同步 GitHub、处理审查意见。 |
| [homework-delivery](homework-delivery/SKILL.md) | 按个人偏好撰写作业、实验报告并整理报告、代码及必要数据的提交包。 |

## 目录

```text
.
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

克隆仓库后，将所需 skill 的完整目录复制到 `${CODEX_HOME:-$HOME/.codex}/skills/`。安装前先检查目标是否已有同名目录，备份后再按需更新，避免覆盖本机尚未同步的修改。不要只复制 `SKILL.md`，课程 skill 还依赖相邻的模板、参考文件和脚本。

安装后可在支持 skills 的 Codex 会话中使用 `$course-materials-to-notes` 或 `$homework-delivery` 指定调用。

## 维护

仓库是本机 skills 的独立副本，不会自动与安装目录同步。修改后应将相应目录同步到另一处，并通过 Git 提交记录版本。

课程 skill 自带验证脚本的测试，可在其目录运行：

```sh
cd course-materials-to-notes
python3 -m unittest discover -s scripts -p 'test_*.py'
```

`homework-delivery` 包含个人姓名和学号等偏好，因此仓库默认设为私有；对外分享前请先处理这些字段。
