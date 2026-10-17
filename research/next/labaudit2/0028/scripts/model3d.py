import json, numpy as np
# 3D emulation of the label process for family 0028 (capture clock 25 fps, drops after video 11 and 35)
F=711.0; CX=640.0; CY=360.0
T=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0028/track.json'))
W=json.load(open('/home/user/quantiphy-challenge/research/next/labaudit2/0028/width.json'))['captured_0028x']
def cap(k): return k + (k>=12) + (k>=36)
def ray(u,v):
    d=np.array([(u-CX)/F,(v-CY)/F,1.0]); return d/np.linalg.norm(d)
REND=['captured_0028x','captured_0028']
# video frame of a capture frame
def vid(n):
    for k in range(49):
        if cap(k)==n: return k
    return None
# ---------- range models (surface range at the click, like the ToF) ----------
# A: stated anchors at the labeller's frames, linear between, constant-slope extrapolation inside arc 1
def RA(n, n11, n13):
    s=(1.4115-1.557)/(n13-n11)
    if n<=n13+3 and n>=n11: return 1.557+s*(n-n11)
    return None
# B: size: surface range = k / w - r ; k from apex (w~21.7 at 1.4115+0.02) and from 0032 (30.6)
w=np.array([np.nan if W[k] is None else W[k]['w'] for k in range(49)])
nn=np.array([cap(k) for k in range(49)])
sel=[k for k in range(29,36)]  # arc 1 frames after bounce (sharp enough)
for kk,lab in [(31.06,'k=31.06 (apex ToF)'),(30.6,'k=30.6 (0032 ping-pong)')]:
    Rc=kk/w
    c=np.polyfit(nn[sel],Rc[sel],1)
    print(f'size {lab}: arc1 frames video 29-35 centre range fit: slope {c[0]*25:.3f} m/s, R(n=27.26)={np.polyval(c,27.26):.3f} R(n=32.88)={np.polyval(c,32.88):.3f}')
    sel2=list(range(39,45)); c2=np.polyfit(nn[sel2],Rc[sel2],1)
    print(f'   arc2 frames video 39-44: slope {c2[0]*25:.3f} m/s, R(apex2 n=43.63)={np.polyval(c2,43.63):.3f};  held frames 0-20 mean R={np.nanmean(Rc[:21]):.3f}')
    print('   per-frame centre range:', ' '.join(f'{k}:{Rc[k]:.3f}' for k in range(20,49)))
