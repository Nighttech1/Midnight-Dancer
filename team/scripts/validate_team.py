#!/usr/bin/env python3
"""Validate repository team contracts without network access or dependencies."""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
errors = []
def require(condition, message):
    if not condition:
        errors.append(message)

def existing(relative, source):
    path = (ROOT / relative).resolve()
    require(path.is_relative_to(ROOT), f'{source}: path escapes repository: {relative}')
    require(path.is_file(), f'{source}: missing file {relative}')
    return path

registry_path = ROOT / 'team/registry.json'
try:
    registry = json.loads(registry_path.read_text(encoding='utf-8'))
except (OSError, ValueError) as exc:
    print(f'FAIL: registry: {exc}')
    sys.exit(1)

roles = registry['roles']
ids = [r['id'] for r in roles]
require(len(ids) == len(set(ids)), 'Duplicate role IDs')
by_id = {r['id']: r for r in roles}
roots = [r['id'] for r in roles if r['manager'] is None]
require(roots == ['product-director'], f'Unexpected leadership roots: {roots}')
existing(registry['entrypoint'], 'entrypoint')

used_skills = set()
for r in roles:
    rid = r['id']
    profile = existing(r['path'], rid)
    text = profile.read_text(encoding='utf-8') if profile.is_file() else ''
    require(rid in text and r['title'] in text, f'{rid}: profile identity mismatch')
    require(r['manager'] is None or r['manager'] in by_id, f'{rid}: unknown manager')
    expected_reports = sorted(x['id'] for x in roles if x['manager'] == rid)
    require(sorted(r['direct_reports']) == expected_reports, f'{rid}: direct reports mismatch')
    require(bool(r['trigger']) and bool(r['default_write_scope']), f'{rid}: missing routing/scope')
    for skill in r['skills']:
        used_skills.add(skill)
        existing(skill, rid)
        require(skill in text, f'{rid}: skill missing from profile: {skill}')
    visited = set()
    current = rid
    while current in by_id:
        if current in visited:
            require(False, f'{rid}: management cycle at {current}')
            break
        visited.add(current)
        current = by_id[current]['manager']

skill_names = []
for path in sorted((ROOT / 'team/skills').glob('*/SKILL.md')):
    content = path.read_text(encoding='utf-8')
    match = re.match(r'\A---\nname: ([a-z0-9-]+)\ndescription: ([^\n]+)\n---\n', content)
    require(match is not None, f'{path.relative_to(ROOT)}: invalid skill frontmatter')
    if match:
        skill_names.append(match.group(1))
        require(len(match.group(1)) < 64, f'{path}: skill name too long')
    require(len(content.splitlines()) < 500, f'{path}: skill exceeds 500 lines')
    require(str(path.relative_to(ROOT)) in used_skills, f'{path}: unassigned skill')
require(len(skill_names) == len(set(skill_names)), 'Duplicate skill names')

for path in sorted(ROOT.rglob('*.md')):
    content = path.read_text(encoding='utf-8')
    for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)', content):
        if re.match(r'^[a-zA-Z][\w+.-]*:', target) or target.startswith('#'):
            continue
        relative = target.split('#', 1)[0]
        link = (path.parent / relative).resolve()
        require(link.is_relative_to(ROOT), f'{path.relative_to(ROOT)}: escaping link {target}')
        require(link.exists(), f'{path.relative_to(ROOT)}: broken link {target}')

required = ['team/CONSTITUTION.md', 'team/ORCHESTRATION.md', 'team/STATE.md',
 'team/DECISIONS.md', 'team/INTEGRATIONS.md', 'team/memory/product-director.md',
 'team/workflows/PRODUCT-CYCLE.md', 'team/workflows/LAUNCH.md', 'team/workflows/ENGINEERING.md',
 'team/templates/TASK.md', 'team/templates/RESULT.md', 'team/templates/EXPERIMENT.md',
 'team/templates/WAVE-REPORT.md', 'team/validation/SCENARIOS.md']
for path in required:
    existing(path, 'required team contract')

if errors:
    for message in errors:
        print('FAIL:', message)
    sys.exit(1)
print(f'PASS: {len(roles)} roles; {len(skill_names)} skills; acyclic management graph; '
      'routing, profile bindings, required contracts and local Markdown links valid.')
