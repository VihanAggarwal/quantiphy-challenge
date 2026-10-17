"""Final label-style values for captured_0018 family (remeasure_b, independent).
Time mapping hypothesis H2 (primary): clip = original capture [2.00 s, 4.00 s] (51 capture frames, 49 video frames);
question t -> clip capture index round(25*(t-2.0)); video frame v <-> capture index floor(v*25/24+0.5)
(drop observed between v35/v36 via double-length steps of box & soccer).
"""
import json, math, numpy as np
OUT='/home/user/quantiphy-challenge/research/next/labaudit2/0018/remeasure_b'
f, cx, cy, H = 711.0, 640.0, 360.0, 0.875
T=json.load(open(f'{OUT}/xtracks.json'))
cap=lambda v: math.floor(v*25/24+0.5)
def P(u,v,Z): return np.array([(u-cx)*Z/f,(v-cy)*Z/f,Z])
def Z_from_range(u,v,r): return r*f/math.sqrt((u-cx)**2+(v-cy)**2+f*f)
# --- depths (surface Z, m) ---
Zs = {
 'soccer': Z_from_range(541.7,263,2.80),            # stated range 2.80 m (held); floor contact route gives centre Z 2.82
 'box':    2.54,   # floor contact row ~601 -> centre Z 2.58; occlusion/hand-spacing geometry -> ~2.53
 'tennis': 2.18,   # floor contact row ~642 -> centre 2.21; FWHM diameter 21.5 px & 6.7 cm -> 2.22
 'pineapple': 1.82 # floor contact row ~699 -> centre 1.84
}
print('surface Z:',{k:round(v,3) for k,v in Zs.items()})
# --- held clicks at video 24 (= clip cap 25 = t 3.0 s) ---
held = {'box':(481,265),'soccer':(541.7,263),'tennis':(762,249.5),'pineapple':(870,253)}
X3 = {k:P(*held[k],Zs[k]) for k in held}
pairs=[(2306,'box','soccer'),(2308,'box','tennis'),(2309,'tennis','soccer'),(2307,'box','pineapple'),(2310,'pineapple','soccer'),(2311,'pineapple','tennis')]
for q,a,b in pairs:
    print('qid %d dist %s-%s @3.0s (v24): %.1f cm'%(q,a,b,100*np.linalg.norm(X3[a]-X3[b])))
# --- velocities at 3.4 s: clip cap 35 -> 36 = video 34 -> 35 ---
print('cap(34),cap(35)=',cap(34),cap(35))
for q,k in [(2302,'box'),(2303,'soccer'),(2304,'tennis'),(2305,'pineapple')]:
    a=T[k]['34']['c']; b=T[k]['35']['c']
    Z=Zs[k]
    if k=='soccer':
        Za=Z_from_range(*a,2.80); Zb=Z_from_range(*b,2.80)
    else: Za=Zb=Z
    d=P(*b,Zb)-P(*a,Za); v=np.linalg.norm(d)*25
    # route B: parabola fit of descent in capture time
    fr=[int(i) for i in T[k] if 28<=int(i)<=(39 if k in('soccer',) else 38 if k=='box' else 35)]
    t=np.array([cap(i) for i in fr],float); y=np.array([T[k][str(i)]['c'][1] for i in fr]); xx=np.array([T[k][str(i)]['c'][0] for i in fr])
    p=np.polyfit(t,y,2); px=np.polyfit(t,xx,1)
    dy=np.polyval(p,36)-np.polyval(p,35); dx=px[0]
    vB=math.hypot(dx,dy)*Z/f*25
    vinst=math.hypot(dx,np.polyval(np.polyder(p),35))*Z/f*25
    print('qid %d v_%s @3.4s: direct %.0f cm/s (dpx=%.1f,%.1f, Z=%.2f) | fit-fwd %.0f cm/s (fit frames %s, a=%.2f px/f2) | instantaneous(fit) %.0f cm/s'%(q,k,100*v,d[0]/Z*f,d[1]/Z*f,Z,100*vB,fr,2*p[0],100*vinst))
