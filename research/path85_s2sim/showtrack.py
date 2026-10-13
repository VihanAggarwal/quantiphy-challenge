import sys; sys.path.insert(0, '../..')
import pickle, numpy as np, pandas as pd
from common import test_table
rp = pickle.load(open('out/replay_s2.pkl', 'rb'))
t = test_table()
for v in sys.argv[1:]:
    qs = [q for q, o in rp.items() if o['video_id'] == v and o['spec'].target.kind in ('speed', 'acceleration') and o['spec'].target.time is not None]
    for q in qs:
        o = rp[q]
        print(q, o['spec'].target.kind, o['spec'].target.time, 'geo', round(o['value'], 3), 'base', round(t.base[q], 3), 'direct', t.run_direct_value[q], o['flags'])
    o = rp[qs[0]]; sc = o['debug']['scale_m_per_px']; fps = o['fps']
    tg = [tr for tr in o['tracks'] if tr.role == 'target'][0]
    T, P = [], []
    for ob in tg.obs:
        p = ob.point or ([(ob.box[0] + ob.box[2]) / 2, (ob.box[1] + ob.box[3]) / 2] if ob.box else None)
        if p is not None: T.append(ob.t); P.append(p)
    T = np.array(T); P = np.array(P, float); i = np.argsort(T); T, P = T[i], P[i]
    v_ = np.hypot(*np.diff(P, axis=0).T) / np.maximum(np.diff(T), 1e-9) * sc
    print(v, tg.source, 'scale', round(sc, 5), 'n', len(T))
    print('  ', ' '.join(f'{a:.2f}:{b:.2f}' for a, b in zip(T[1:], v_)))
