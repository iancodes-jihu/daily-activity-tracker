import json
from pathlib import Path
p = Path(__file__).resolve().parent.parent / 'data' / 'activity_log.json'
if not p.exists():
    print('no file')
    raise SystemExit(0)
with p.open('r', encoding='utf-8') as f:
    j = json.load(f)
changed = 0
for e in j:
    if isinstance(e, dict) and 'category' in e:
        del e['category']
        changed += 1
with p.open('w', encoding='utf-8') as f:
    json.dump(j, f, indent=2)
print(f'removed category from {changed} entries')
