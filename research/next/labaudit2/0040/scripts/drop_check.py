"""Which time base fits the flight video 34..40? Ballistic g=9.8 fit for alternative frame->time maps:
rms reprojection and the range implied at video 36 (stated surface 0.7045 -> centre 0.7245)."""
import sys, numpy as np
sys.path.insert(0, '/home/user/quantiphy-challenge/research/next/labaudit2/0040/scripts')
import motion as M
from ballistic25 import lsq, proj, nup
maps = {'25fps drop 35->36': lambda n: (n + (n >= 36)) / 25.0,
        '25fps drop 34->35': lambda n: (n + (n >= 35)) / 25.0,
        '25fps drop 36->37': lambda n: (n + (n >= 37)) / 25.0,
        '25fps drop 37->38': lambda n: (n + (n >= 38)) / 25.0,
        '24fps no drop':     lambda n: n / 24.0,
        '25fps no drop':     lambda n: n / 25.0}
for R in ('x',):
    for mode in ('caps', 'cent'):
        tr = M.load(R, mode)
        frames = (34, 35, 36, 37, 38, 39, 40)
        for name, tm in maps.items():
            t0 = tm(36)
            def res(p):
                r = []
                for n in frames:
                    tt = tm(n) - t0
                    X = p[:3] + p[3:6] * tt - 0.5 * 9.8 * nup * tt * tt
                    r += list(proj(X) - [tr[n]['u'], tr[n]['v']])
                return np.array(r)
            p, f = lsq(res, np.r_[0.72 * M.ray(tr[36]['u'], tr[36]['v']), 0.8, -0.1, -0.1])
            rr = f.reshape(-1, 2)
            print(f'{mode} {name:18s}: rms {np.sqrt((rr**2).mean()):5.2f}px  max {np.abs(rr).max():5.1f}px  range@v36 {np.linalg.norm(p[:3]):.3f}')
