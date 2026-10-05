# 技能列表中文显示

`localize.py` 为 28 个文件型个人 Skill 写入中文显示名称和短简介。它保留 `SKILL.md` 中的调用名称与原始操作说明，只修改各 Skill 的 `agents/openai.yaml`，并给已有文件保留一次 `.codex-backup` 备份。

先运行 `python tools/skill-localization/localize.py` 预览，再运行 `python tools/skill-localization/localize.py --apply` 应用。默认目标是当前用户主目录下的 `.agents/skills`；需要检查其他目录时可加 `--root` 指定。为了避免误改，实际 Skill 清单与脚本中的 28 项不一致时，脚本会停止。

这是文件级修改。Codex 的技能列表是否立即刷新，取决于客户端是否重新读取这些文件。插件提供的 Skill 和 Codex 内置 Skill 不在这 28 项里，也不会被脚本修改。
