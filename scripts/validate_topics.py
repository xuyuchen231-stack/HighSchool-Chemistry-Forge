#!/usr/bin/env python3
"""Validate topic IDs, prerequisites and dependency cycles; stdlib only."""
import json
from pathlib import Path

def validate(path):
    data=json.loads(Path(path).read_text(encoding='utf-8'))
    topics=data['topics']; ids=[t['id'] for t in topics]
    assert len(ids)==len(set(ids)), 'Duplicate topic IDs'
    edges={t['id']:t['prerequisites'] for t in topics}
    for topic, deps in edges.items():
        for dep in deps:
            assert dep in edges, f'Unknown prerequisite {dep} for {topic}'
    seen=set(); active=set()
    def visit(node):
        assert node not in active, f'Cycle at {node}'
        if node in seen: return
        active.add(node)
        for dep in edges[node]: visit(dep)
        active.remove(node); seen.add(node)
    for node in edges: visit(node)
    return len(topics)

if __name__=='__main__':
    path=Path(__file__).resolve().parents[1]/'data/topics.json'
    print(f'OK: {validate(path)} topics; all prerequisites valid and acyclic')
