"""Set Chinese UI labels for the user's file-based skills.

Only agents/openai.yaml is changed. SKILL.md names and instructions stay intact.
Run without --apply to preview. Backups are kept beside files that existed.
"""

import argparse
import json
import re
from pathlib import Path


LABELS = {
    'brandkit': ('品牌视觉套件', '制作品牌规范、标志系统和视觉展示'),
    'design-taste-frontend': ('前端设计品味', '设计或改造有质感的网站界面'),
    'design-taste-frontend-v1': ('前端设计品味·旧版', '需要与旧版设计方法兼容时使用'),
    'eli5': ('通俗讲解与学习页', '讲清复杂概念，制作可复习的学习资料'),
    'full-output-enforcement': ('完整输出', '生成完整代码和内容，避免占位与省略'),
    'gpt-taste': ('高级界面与动效', '设计网页视觉层级与 GSAP 动效'),
    'gsap-core': ('GSAP 基础动画', '制作补间动画、缓动与响应式动效'),
    'gsap-frameworks': ('GSAP 框架集成', '在 Vue、Svelte 等框架中使用 GSAP'),
    'gsap-performance': ('GSAP 性能优化', '减少动画卡顿并优化帧率'),
    'gsap-plugins': ('GSAP 插件', '使用拖拽、滚动及其他 GSAP 插件'),
    'gsap-react': ('GSAP 与 React', '在 React 或 Next.js 中使用 GSAP'),
    'gsap-scrolltrigger': ('GSAP 滚动动画', '制作滚动触发、固定和视差效果'),
    'gsap-timeline': ('GSAP 时间轴', '安排多段动画的顺序与播放'),
    'gsap-utils': ('GSAP 工具函数', '使用数值映射、吸附、随机等工具'),
    'guizang-ppt-skill': ('归藏网页 PPT', '制作可翻页、带讲稿和动效的网页演示'),
    'high-end-visual-design': ('高端视觉设计', '改善网页的字体、间距和视觉质感'),
    'image-to-code': ('图片到网页代码', '参考设计图实现接近原图的网页'),
    'imagegen-frontend-mobile': ('移动应用界面图', '生成手机应用界面设计图，不编写代码'),
    'imagegen-frontend-web': ('网站界面设计图', '为网站各区块生成设计参考图'),
    'industrial-brutalist-ui': ('工业粗野风界面', '设计机械感、网格化的网页界面'),
    'minimalist-ui': ('极简风界面', '设计干净、克制的网页界面'),
    'ponytail': ('极简编码', '优先采用简单、少依赖的实现方法'),
    'redesign-existing-projects': ('现有项目改版', '检查并改善现有网站或应用的设计'),
    'scene-distillation-zine-v1-3': ('影像蒸馏', '把照片转化为有表现力的艺术插画海报'),
    'scenes-gathered-zine-v1-3': ('实景拼贴', '把真实照片做成纸张拼贴风格海报'),
    'smart-charts': ('智能图表', '把表格数据做成交互式图表'),
    'stitch-design-taste': ('Stitch 设计规范', '为 Google Stitch 项目编写设计规范'),
    'video-use': ('视频剪辑', '按对话要求剪辑、调色和添加字幕'),
}


def updated_yaml(original, title, description):
    display = '  display_name: ' + json.dumps(title, ensure_ascii=False)
    summary = '  short_description: ' + json.dumps(description, ensure_ascii=False)
    if not original:
        return 'interface:\n' + display + '\n' + summary + '\n'
    if not re.search(r'^interface:[ \t]*$', original, re.M):
        raise ValueError('Missing interface section')
    output = original
    for field, line in [('display_name', display), ('short_description', summary)]:
        pattern = r'^  ' + field + r':[^\n]*$'
        if re.search(pattern, output, re.M):
            output = re.sub(pattern, lambda _match: line, output, count=1, flags=re.M)
        else:
            output = re.sub(r'^interface:[ \t]*$', lambda _match: 'interface:\n' + line, output, count=1, flags=re.M)
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--root', type=Path, default=Path.home() / '.agents' / 'skills')
    args = parser.parse_args()
    root = args.root
    found = {p.parent.name for p in root.glob('*/SKILL.md')}
    if found != set(LABELS):
        raise SystemExit(f'Skill set changed. Missing: {sorted(set(LABELS)-found)}; extra: {sorted(found-set(LABELS))}')
    for slug, (title, description) in LABELS.items():
        path = root / slug / 'agents' / 'openai.yaml'
        original = path.read_text(encoding='utf-8') if path.exists() else ''
        changed = updated_yaml(original, title, description)
        if changed == original:
            continue
        print(f'{slug} -> {title} | {description}')
        if args.apply:
            path.parent.mkdir(exist_ok=True)
            if path.exists():
                backup = path.with_suffix('.yaml.codex-backup')
                if not backup.exists():
                    backup.write_text(original, encoding='utf-8')
            path.write_text(changed, encoding='utf-8')
    print('Applied' if args.apply else 'Preview only', len(LABELS), 'skills')


if __name__ == '__main__':
    main()
