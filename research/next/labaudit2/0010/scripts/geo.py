"""Geometric route: ball centre on the sphere |C - P0| = L, C on the ray through the click.
P0 = d0 * ray(pivot pixel(k)); pivot pixel from the measured string top (running median).
(d0, L) fitted either to the stated anchors or to the size series (D = 7 cm)."""
import sys, json; sys.path.insert(0,'/home/user/quantiphy-challenge/research/next/labaudit2/0010/scripts')
from common import *
B='/home/user/quantiphy-challenge/research/next/labaudit2/0010/'
T=json.load(open(B+'track.json')); S=json.load(open(B+'size_s.json')); ST=json.load(open(B+'string_s.json'))
k=np.arange(49); n=np.array([cap(i) for i in k])
u=np.array([T['s'][i]['u'] for i in k]); v=np.array([T['s'][i]['v'] for i in k]); w=np.array([S[i]['wh'] for i in k])
xt=np.array([ST[i]['xtop'] for i in k]); yt=np.array([ST[i]['ytop'] for i in k])
def runmed(a,h=3):
    return np.array([np.median(a[max(0,i-h):i+h+1]) for i in range(len(a))])
pu_meas=runmed(xt); pv_meas=runmed(yt)
SIDE=np.where(((n>=13)&(n<=22))|(n>=43),-1,1)   # -1 near root, +1 far root (bottom crossings ~c12.5, c22.5, c42.5)
def ranges(d0,L,pu=None,pv=None,dv=0.0,side=SIDE,uu=u,vv=v):
    pu=pu_meas if pu is None else pu; pv=(pv_meas if pv is None else pv)+dv
    out=[]; disc=[]
    for i in range(len(uu)):
        r=ray(uu[i],vv[i]); P0=d0*ray(pu[i],pv[i])
        b=r@P0; c=P0@P0-L*L; D=b*b-c
        disc.append(D)
        out.append(b+side[i]*np.sqrt(max(D,0)))
    return np.array(out),np.array(disc)
STATED={0.3:1.7060,0.6:1.3440,0.9:1.4605,1.2:1.7840,1.5:1.7170,1.8:1.3500}
def anchor_frames(conv):
    # video frame index for each stated time under a convention
    m={}
    for t in STATED:
        if conv=='treal': kk=int(np.round(t*24))
        else:
            c=int(np.floor(t*25)) if conv=='floor' else int(np.ceil(t*25)) if conv=='ceil' else None
            kk=[i for i in k if n[i]==c]; kk=kk[0] if kk else None
        m[t]=kk
    return m
def grid_fit(cost, d0s=np.arange(1.30,1.80,0.0025), Ls=np.arange(0.25,0.45,0.001)):
    best=(1e18,None,None)
    for d0 in d0s:
        for L in Ls:
            c=cost(d0,L)
            if c<best[0]: best=(c,d0,L)
    return best
if __name__=='__main__':
    use=[0.3,0.6,1.2,1.5,1.8]   # t=0.9 sits at the bottom crossing (ill-conditioned)
    for conv in ['treal','floor','ceil']:
        af=anchor_frames(conv)
        idx=[(af[t],STATED[t]) for t in use if af[t] is not None]
        def cost(d0,L):
            R,D=ranges(d0,L)
            return sum((R[i]-0.035-s)**2 for i,s in idx)+ 10*sum(max(0,-D[i]) for i,_ in idx)
        c,d0,L=grid_fit(cost)
        R,D=ranges(d0,L)
        print(f"[anchors {conv}] d0={d0:.4f} L={L:.3f} rms={np.sqrt(c/len(idx))*100:.2f}cm  per-anchor:",
              ' '.join(f"t{t}:k{af[t]}:{(R[af[t]]-0.035-STATED[t])*100:+.1f}" for t in STATED if af[t] is not None))
    # size calibration (exclude frames near bottom crossings and blurred-fast frames)
    good=np.array([not (11<=nn<=14 or 21<=nn<=24 or 41<=nn<=44) for nn in n])
    def cost_s(d0,L):
        R,D=ranges(d0,L); return np.sum(((F*0.07/R-w)[good])**2)
    c,d0,L=grid_fit(cost_s)
    R,D=ranges(d0,L)
    print(f"[size D=7] d0={d0:.4f} L={L:.3f} rms width {np.sqrt(c/good.sum()):.2f}px")
    for t in STATED: 
        for conv in ['treal']:
            kk=anchor_frames(conv)[t]; print(f"   t={t} k{kk} c{n[kk]} geo-size surf {R[kk]-0.035:.4f} stated {STATED[t]}")
