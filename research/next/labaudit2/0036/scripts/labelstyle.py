import numpy as np, json
T=json.load(open('scripts/trk_bg.json'))
Z=json.load(open('scripts/size2.json'))
R=0.02; c0=np.array([640.,360.])
def cap(k): return int(np.floor(k*25/24+0.5))
def ray(u,v,f):
    r=np.array([(u-c0[0])/f,(v-c0[1])/f,1.]); return r/np.linalg.norm(r)
ks=list(range(16,36))
Ua=np.array([[np.mean([T[v][str(k)]['cx'] for v in T]),np.mean([T[v][str(k)]['cy'] for v in T])] for k in ks])
d=np.array([Z['captured_0036'][str(k)]['d'] for k in ks]); d[ks.index(35)]=Z['captured_0036s']['35']['d']
dS=np.array([np.median([Z[v][str(k)]['d'] for v in Z]) for k in ks])
tc=np.array([cap(k) for k in ks],float)
# smooth click track: local quadratic fit in capture index (window 7)
def smooth(y,x,w=3,deg=2):
    out=np.zeros_like(y)
    for i in range(len(x)):
        s=max(0,i-w); e=min(len(x),i+w+1)
        p=np.polyfit(x[s:e]-x[i],y[s:e],deg); out[i]=p[-1]
    return out
Us=np.stack([smooth(Ua[:,0],tc),smooth(Ua[:,1],tc)],1)
def at(arr,n):  # value at capture index n (interp)
    return np.array([np.interp(n,tc,arr[:,j]) for j in range(arr.shape[1])]) if arr.ndim==2 else np.interp(n,tc,arr)
res={}
for f in [711.,766.]:
    n_tab=np.load(f'scripts/normal_{int(f)}.npy')
    for tlab,nlist in [('0.9',[22,23]),('1.4',[35])]:
        pass
    # stated centre points (click = smoothed track at capture 22.5 / 35)
    c09=at(Us,22.5); c14=at(Us,35.)
    C09=(1.010+R)*ray(*c09,f); C14=(0.716+R)*ray(*c14,f)
    h09=n_tab@C09; h14=n_tab@C14
    print('f %d  plane h_c from 0.9: %.4f  from 1.4: %.4f'%(f,h09,h14))
    # route definitions -> centre range per frame index (array over ks), using smoothed clicks
    routes={}
    # size: fit 1/d (∝ 1/r) with a quadratic in capture time over frames 18-35, K matched to stated
    sel=np.array([k>=18 for k in ks])
    for nm,dd in [('size_o',d),('size_med',dS)]:
        p=np.polyfit(tc[sel],dd[sel],2); dfit=np.polyval(p,tc)
        K09=(1.010+R)*np.polyval(p,22.5); K14=(0.716+R)*np.polyval(p,35.)
        routes[nm+'_K09']=K09/dfit; routes[nm+'_K14']=K14/dfit
        # scale interpolated in time between the two stated anchors
        w=np.clip((tc-22.5)/12.5,0,1); routes[nm+'_Kint']=(K09*(1-w)+K14*w)/dfit
    for nm,h in [('plane_h09',h09),('plane_h14',h14),('plane_hmean',0.5*(h09+h14))]:
        routes[nm]=np.array([h/(n_tab@ray(*Us[i],f)) for i in range(len(ks))])
    # plane with scale interpolation (pass through both stated)
    rp=np.array([1/(n_tab@ray(*Us[i],f)) for i in range(len(ks))])
    w=np.clip((tc-22.5)/12.5,0,1); routes['plane_int']=rp*(h09*(1-w)+h14*w)
    # line route
    D=C14-C09; rl=[]
    for i in range(len(ks)):
        r=ray(*Us[i],f); A=np.stack([D,-r],1); s,t=np.linalg.lstsq(A,-C09,rcond=None)[0]; rl.append(np.linalg.norm(C09+s*D))
    routes['line']=np.array(rl)
    print(' route         v0.9(22->23) v0.9(23->24) v0.9(avg)  v1.4(35->36)  | phys0.9 phys1.4 | disp0.9-1.4 | rad0.9 rad1.4')
    for nm,rc in routes.items():
        Pc=np.array([rc[i]*ray(*Us[i],f) for i in range(len(ks))])
        Ps=np.array([(rc[i]-R)*ray(*Us[i],f) for i in range(len(ks))])
        def fd(P,n): i=list(tc).index(n); return 100*np.linalg.norm(P[i+1]-P[i])*25
        def rad(n): i=list(tc).index(n); return 100*(rc[i+1]-rc[i])*25
        # physical: central difference of centre positions (smooth) at 22.5 and 35
        def phys(t):
            i=np.searchsorted(tc,t)
            # fit quadratic to Pc around t
            sel=(abs(tc-t)<=4)
            v=[np.polyfit(tc[sel]-t,Pc[sel,j],2)[1] for j in range(3)]
            return 100*np.linalg.norm(v)*25
        P09=0.5*(Ps[list(tc).index(22)]+Ps[list(tc).index(23)]); P14=Ps[list(tc).index(35)]
        a,b,c=fd(Ps,22),fd(Ps,23),fd(Ps,35)
        print(' %-14s %7.1f %7.1f %7.1f      %7.1f      | %6.1f %6.1f | %6.1f | %6.1f %6.1f'%(nm,a,b,(a+b)/2,c,phys(22.5),phys(35),100*np.linalg.norm(P14-P09),0.5*(rad(22)+rad(23)),rad(35)))
        res[f'{int(f)}_{nm}']=dict(v09=(a+b)/2,v09a=a,v09b=b,v14=c,ph09=phys(22.5),ph14=phys(35))
json.dump(res,open('scripts/labelstyle.json','w'),indent=1)
