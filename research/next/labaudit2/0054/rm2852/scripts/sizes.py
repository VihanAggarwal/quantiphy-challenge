import cv2, numpy as np, json, math, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from ballfit import fit, model, ray, cap, F, CX, CY
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
ax=np.load(S+'ax.npy')
anc=3.0735+0.033
r=fit('white',24,39,anchor=anc)
def widths(k,cxy):
    f=ax[k].astype(np.int16)
    d=np.sqrt(((f-np.array([0,252,0]))**2).sum(-1))
    fg=(d>60).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(fg,8)
    i=np.argmin([np.hypot(*(cen[j]-cxy)) if j>0 else 1e9 for j in range(n)])
    m=lab==i
    ys,xs=np.nonzero(m)
    pts=np.c_[xs,ys].astype(np.float32)
    rect=cv2.minAreaRect(pts)
    w,h=rect[1]
    # soft width: use alpha-ish weight d/ max
    c=np.cov(pts.T); ev=np.sort(np.linalg.eigvalsh(c))
    return min(w,h)+1, max(w,h)+1, 4*math.sqrt(ev[0]), m.sum()
comps=json.load(open(S+'comps_ax.json'))
print('k cap  minor(rect) major  4sd_minor  area   fit_center_range')
rows=[]
for k in range(23,39):
    cs=[c for c in comps[str(k)] if c['bgr'][0]>=85 and c['area']<1500 and c['c'][1]<690]
    if not cs: continue
    c=cs[0]
    wmin,wmax,w4,a=widths(k,np.array(c['c']))
    c_=cap(k)
    P=model(r['q'],np.array([c_/25]),r['th'],r['rho'],r['g'])[0]
    rows.append((k,c_,wmin,wmax,w4,a,np.linalg.norm(P)))
    print(k,c_,'%.1f %.1f %.1f %d %.3f'%(wmin,wmax,w4,a,np.linalg.norm(P)))
rows=np.array(rows)
# size-based range: range_k = range_ref * w_ref / w_k ; reference = mean of caps 25-30 (slow, little blur)
ref=rows[(rows[:,1]>=25)&(rows[:,1]<=30)]
for col,name in [(2,'rect minor'),(4,'4sd minor')]:
    # product w*range should be constant = f*D
    fD=(ref[:,col]*ref[:,6]).mean()
    print(name,'f*D from ref (fit ranges) = %.1f  -> D=%.2f cm (f=711, includes matte halo)'%(fD,100*fD/F))
    for row in rows:
        print('   cap %d  size-range=%.3f  fit-range=%.3f'%(row[1],fD/row[col],row[6]))
