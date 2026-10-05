"""Localize project-level Information Monitor skill labels on this computer."""

import argparse
import json
import os
import re
from pathlib import Path


TITLE = '信息监测｜核实帖子与更新'
SUMMARY = '查看监测结果，核实来源并整理有用线索'
SKIP_DIRS = {
    'AppData', '.git', 'node_modules', '.venv', 'venv', '__pycache__',
    '.cache', '.npm', '.cargo', '.rustup', 'site-packages',
}


def find_skills(root):
    for directory, subdirs, files in os.walk(root):
        subdirs[:] = [name for name in subdirs if name not in SKIP_DIRS]
        path = Path(directory)
        if (path.name == 'information-monitor'
                and path.parent.name == 'skills'
                and path.parent.parent.name in {'.agents', '.codex'}
                and 'SKILL.md' in files):
            yield path
            subdirs[:] = []


def updated_yaml(original):
    title = '  display_name: ' + json.dumps(TITLE, ensure_ascii=False)
    summary = '  short_description: ' + json.dumps(SUMMARY, ensure_ascii=False)
    if not original:
        return 'interface:\n' + title + '\n' + summary + '\n'
    if not re.search(r'^interface:[ \t]*$', original, re.M):
        raise ValueError('Existing openai.yaml has no interface section')
    output = original
    for field, line in [('display_name', title), ('short_description', summary)]:
        pattern = r'^  ' + field + r':[^\n]*$'
        if re.search(pattern, output, re.M):
            output = re.sub(pattern, lambda _match: line, output, count=1, flags=re.M)
        else:
            output = re.sub(r'^interface:[ \t]*$', lambda _match: 'interface:\n' + line, output,
                            count=1, flags=re.M)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, default=Path.home())
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    skills = list(find_skills(args.root))
    if not skills:
        raise SystemExit(f'No Information Monitor project skill found under {args.root}')
    changed = 0
    for skill in skills:
        path = skill / 'agents' / 'openai.yaml'
        original = path.read_text(encoding='utf-8') if path.exists() else ''
        output = updated_yaml(original)
        print(('Already Chinese: ' if output == original else 'Found: ') + str(skill))
        if output == original:
            continue
        changed += 1
        if args.apply:
            path.parent.mkdir(exist_ok=True)
            if path.exists():
                backup = path.with_suffix('.yaml.codex-backup')
                if not backup.exists():
                    backup.write_text(original, encoding='utf-8')
            path.write_text(output, encoding='utf-8')
    print(('Applied' if args.apply else 'Preview only'), changed, 'project skills')


if __name__ == '__main__':
    main()
