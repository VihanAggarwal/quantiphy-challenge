"""3D ball positions from the x/s tracks: range from minor axis (D=4 cm, tangential extent = f D /(d cos th))."""
import json, numpy as np, sys
F, CX, CY, D = 711.0, 640.0, 360.0, 0.04
B = '/home/user/quantiphy-challenge/research/next/labaudit/0040'
R = sys.argv[1] if len(sys.argv) > 1 else 'x'
tr = {int(k): v for k, v in json.load(open(f'{B}/track_{R}.json')).items()}
def ray(u, v):
    r = np.array([(u - CX) / F, (v - CY) / F, 1.0]); return r / np.linalg.norm(r)
P = {}
for i in range(22, 49):
    t = tr[i]; r = ray(t['u'], t['v']); cos = r[2]
    d = F * D / (t['minor'] * cos)
    P[i] = d * r
    print(f"{i:2d} t={i/24:.3f} range={d:.3f} P={np.round(P[i]*100,1)}")
print('stated: t=1.5 0.7045, t=2.0 0.627')
def sp(a, b):
    return np.linalg.norm(P[b] - P[a]) / ((b - a) / 24) * 100
print('frame-to-frame speeds cm/s:')
for i in range(22, 48):
    print(i, f'{sp(i, i+1):.1f}')
