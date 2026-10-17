import numpy as np, json
W='research/next/labaudit2/0028/remeasure_work'
tr=json.load(open(f'{W}/track_captured_0028x.json'))
f=711.; cx=640.; cy=360.; R=0.02
def cap(k): return k + (k>=12) + (k>=36)
vid={cap(k):k for k in range(49)}
fr=list(range(27,36)); t=np.array([cap(k) for k in fr],float)
py=np.polyfit(t,[tr[k]['cy'] for k in fr],2); px=np.polyfit(t,[tr[k]['cx'] for k in fr],1)
tap=-py[1]/(2*py[0])
def ray(u,v):
    d=np.array([(u-cx)/f,(v-cy)/f,1.]); return d/np.linalg.norm(d)
r_apex_surface=1.4115   # depth_info at t=1.3 (range to visible surface)
print('apex capture t=%.2f'%tap)
for Vz in [-0.40,-0.50,-0.58,-0.65,-0.73]:
    for k in [32,33]:
        for src in ['raw','fit']:
            def uv(c):
                if src=='raw': return tr[vid[c]]['cx'],tr[vid[c]]['cy']
                return np.polyval(px,c),np.polyval(py,c)
            u0,v0=uv(k); u1,v1=uv(k+1)
            # surface range at k: anchor at capture 33 = 1.4115; propagate with Vz (range rate ~ Vz*cos)
            def rng(c): return r_apex_surface + Vz*(c-33)/25*1.0
            P0=rng(k)*ray(u0,v0); P1=rng(k+1)*ray(u1,v1)
            print(f'Vz {Vz:5.2f} k {k}->{k+1} ({src}, video {vid[k]}->{vid[k+1]}): label-style |dP|*25 = {np.linalg.norm(P1-P0)*25*100:6.1f} cm/s   dP(cm)={np.round((P1-P0)*100,2)}')
# physical instantaneous at capture 33 (centre), Vx from x drift given Vz
Z=1.41
for Vz in [-0.45,-0.55,-0.65]:
    du=px[0]*25; Vx=(du*Z/f)+(np.polyval(px,33)-cx)/f*Vz
    vy=py[0]*2*(33-tap)*25*Z/f
    print(f'phys Vz {Vz}: Vx {Vx:.3f} Vy {vy:.3f} speed {np.sqrt(Vx**2+vy**2+Vz**2)*100:.1f} cm/s')
