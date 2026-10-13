"""Dump Claude's spec + prior/target tracks for a video (test run v1_high_854)."""
import json, sys, numpy as np
run = sys.argv[2] if len(sys.argv) > 2 else 'runs/test_v1_high_854/test/records'
v = sys.argv[1]
r = json.load(open(f'{run}/{v}.json')); m = r['meta']
print(v, 'img', m['image_size'], 'scale', round(m['scale'], 4), 'fps', m['fps'], 'nframes', m['n_frames_total'])
for q in r['parsed']['questions']:
    sp = q['spec']
    print(f"Q{q['qid']} target={sp['target'].get('kind')}/{sp['target'].get('dimension')} t={sp['target'].get('time')} w={sp['target'].get('window')} | prior={sp['prior'].get('kind')}/{sp['prior'].get('dimension')} {sp['prior'].get('value_si')} | direct={q['direct_answer']} conf={q.get('confidence')} | {sp.get('notes','')[:160]}")
    for t in q['tracks']:
        ex = [o for o in t['obs'] if o.get('extent')]
        if ex:
            L = [float(np.hypot(o['extent'][1][0]-o['extent'][0][0], o['extent'][1][1]-o['extent'][0][1])) for o in ex]
            print(f"    {t['role']:6s} {t['object'][:30]:30s} extent px med={np.median(L):.1f} n={len(L)} first={ex[0]['extent']}")
        pts = [o for o in t['obs'] if o.get('point')]
        if pts:
            print(f"    {t['role']:6s} {t['object'][:30]:30s} points n={len(pts)} f={pts[0]['frame']}..{pts[-1]['frame']} p0={pts[0]['point']} p1={pts[-1]['point']}")
