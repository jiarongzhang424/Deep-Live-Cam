---
name: skill-localization-zh
description: 把 Codex 文件型 Skill 的显示名称和简介整理成中文，并检查中文名称是否写入界面元数据。
---

# 技能中文化

用户要求把已安装的 Codex Skill 显示成中文时，先检查个人目录中的文件型 Skill，再按 `scripts/localize.py` 中的中文名称和简介清单更新 `agents/openai.yaml`。脚本默认预览；只有用户明确要求应用时才加 `--apply`。

如果用户指定“信息监测”项目 Skill，使用 `scripts/localize_project.py`，并把 `--root` 指向项目所在目录。不要把个人 Skill 目录误当成项目目录。

完成后汇报处理数量、未收录 Skill、文件级结果，以及客户端是否需要重新加载。`SKILL.md` 的 `name` 是调用标识，不翻译它；界面显示名由 `agents/openai.yaml` 的 `interface.display_name` 决定，简介由 `interface.short_description` 决定。文件修改完成不等于新对话已经加载，只有在新对话的 `$` 列表中确认后才能说显示成功。

插件提供的 Skill 和 Codex 内置 Skill 不属于这些本地文件，脚本不会修改它们。
