"""Lesson-specific workflow. Read this file before the execution adapter."""
from __future__ import annotations
import asyncio
import json
from pathlib import Path
from runtime import atomic_json, contained_path, in_process_tool

async def run(agent, data):
    import hashlib
    key = hashlib.sha256(json.dumps({'request': data['request'], 'release': data['release'], 'model': agent.model, 'live': agent.live}, sort_keys=True).encode()).hexdigest()
    path = agent.root / 'state/cache' / (key + '.json')
    if path.exists():
        answer = json.loads(path.read_text(encoding='utf8'))['answer']
        agent.event('cache_hit', key=key)
    else:
        answer = await agent.ask('answer', 'Explain ResultMessage and the is_error field.', data['request'], 'Inspect ResultMessage.is_error before accepting the final result.')
        atomic_json(path, {'answer': answer})
    gate = 'ResultMessage' in answer and 'is_error' in answer
    manifest = {'release': data['release'], 'cache_key': key, 'acceptance_gate': gate, 'deployed': False}
    atomic_json(agent.output / 'release_manifest.json', manifest)
    return {'answer': answer, 'manifest': manifest}
