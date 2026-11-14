import json
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'knowledge'/'curriculum.json'
d=json.loads(p.read_text(encoding='utf-8'))
ids=[x['id'] for m in d['modules'] for x in m['topics']]
assert len(ids)==len(set(ids)), 'duplicate IDs'
assert all(x['status'] in {'index_only','draft','reviewed'} for m in d['modules'] for x in m['topics'])
assert all(x['title'] for m in d['modules'] for x in m['topics'])
print(f'Validated {len(d["modules"])} modules, {len(ids)} indexed topics.')
