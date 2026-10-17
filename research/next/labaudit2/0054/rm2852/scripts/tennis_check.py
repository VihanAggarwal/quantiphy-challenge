import sys, os, math, numpy as np, cv2, json
sys.path.insert(0, os.path.dirname(__file__))
import ballfit as B
S='/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/'
ax=np.load(S+'ax.npy'); a=np.load(S+'a.npy')
rt=B.fit('tennis',24,38,anchor=3.039+0.0335)
rw=B.fit('white',24,39,anchor=3.0735+0.033)
print('tennis fit th=%.2f rho=%.2f rms=%.2f'%(math.degrees(rt['th']),math.degrees(rt['rho']),rt['rms']))
comps=json.load(open(S+'comps_ax.json'))
def minor_width(k,cxy,arr,green=True):
    f=arr[k].astype(np.int16)
    fg=(np.sqrt(((f-np.array([0,252,0]))**2).sum(-1))>60).astype(np.uint8)
    n,lab,st,cen=cv2.connectedComponentsWithStats(fg,8)
    i=1+np.argmin([np.hypot(*(cen[j]-cxy)) for j in range(1,n)])
    ys,xs=np.nonzero(lab==i); pts=np.c_[xs,ys].astype(np.float32)
    (cx,cy),(w,h),ang=cv2.minAreaRect(pts)
    # profile width perpendicular to major axis using half-max of mask projection
    c=np.cov(pts.T); ev,evec=np.linalg.eigh(c); minor=evec[:,0]
    proj=(pts-pts.mean(0))@minor
    return min(w,h)+1, proj.max()-proj.min()+1
print('cap  tennis: fit_range  size_range(D=6.7,f=711,minAreaRect-1px halo)   white fit range')
for k in range(25,39):
    c=B.cap(k)
    cs=[x for x in comps[str(k)] if x['bgr'][0]<85 and x['area']<1500 and x['c'][1]<690]
    if not cs: continue
    w1,w2=minor_width(k,np.array(cs[0]['c']),ax)
    Pt=B.model(rt['q'],np.array([c/25]),rt['th'],rt['rho'],rt['g'])[0]
    Pw=B.model(rw['q'],np.array([c/25]),rw['th'],rw['rho'],rw['g'])[0]
    print('c%d  %.3f  %.3f (w=%.1f)   white %.3f'%(c,np.linalg.norm(Pt),711*0.067/(w1-1.5),w1,np.linalg.norm(Pw)))
for nm,r in [('tennis',rt),('white',rw)]:
    for t in [1.0,1.5]:
        V=r['q'][3:6]+B.gvec(r['th'],r['rho'],r['g'])*(t-1.0)
        print(nm,'V(%.1f)='%t,np.round(V,2),'|V|=%.2f'%np.linalg.norm(V))
