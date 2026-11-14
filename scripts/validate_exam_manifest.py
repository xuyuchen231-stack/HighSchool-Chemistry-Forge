import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'data'/'haidian_exam_manifest.json'
d=json.loads(p.read_text(encoding='utf-8'))
assert d['pages']==8 and d['total_points']==100
assert [q['number'] for q in d['questions']]==list(range(1,20))
allowed={'pending_independent_solution','needs_visual_check','needs_chemistry_check','ambiguous','verified'}
assert all(q['status'] in allowed for q in d['questions'])
for q in d['questions']:
 if q['status']=='verified':
  assert q.get('evidence') and q.get('items'), 'verified requires evidence and item IDs'
print('PASS: 19-question inventory with explicit item/evidence requirements; not a scientific certification')
