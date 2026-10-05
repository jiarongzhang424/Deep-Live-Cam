# 技能列表中文显示

`localize.py` 为 30 个文件型个人 Skill 写入中文显示名称和短简介。它保留 `SKILL.md` 中的调用名称与原始操作说明，只修改各 Skill 的 `agents/openai.yaml`，并给已有文件保留一次 `.codex-backup` 备份。

先运行 `python tools/skill-localization/localize.py` 预览，再运行 `python tools/skill-localization/localize.py --apply` 应用。默认目标是当前用户主目录下的 `.agents/skills`；需要检查其他目录时可加 `--root` 指定。脚本只修改找到且列在清单中的 Skill，并列出缺少或未收录的项。

这是文件级修改。Codex 的技能列表是否立即刷新，取决于客户端是否重新读取这些文件。清单包含文件形式安装的 Agent Reach 和 Scrapling；其他插件提供的 Skill 与 Codex 内置 Skill 不会被脚本修改。
