import numpy as np, json
D='/home/user/quantiphy-challenge/research/next/labaudit2/0023/'
E=json.load(open(D+'scripts/book_edges.json'))
def ray(x,y,f,cx=640,cy=360): return np.array([(x-cx)/f,(y-cy)/f,1.0])
def edges(V,ph,y0,y1):
    A=np.load(D+f'frames/avg_{V}_{ph}.npy'); lum=A.mean(-1); out=[]
    for y in range(y0,y1):
        p=lum[y-300]
        xl=next(x for x in range(470,580) if p[x-400]>200); xr=next(x for x in range(720,600,-1) if p[x-400]>200)
        def subpix(xe,dirn):
            out_=p[xe-400-6*dirn]; inn=p[xe-400+4*dirn]; mid=0.5*(out_+inn)
            xs=np.arange(xe-6*dirn,xe+5*dirn,dirn); vals=p[xs-400]
            for i in range(len(xs)-1):
                if (vals[i]-mid)*(vals[i+1]-mid)<=0 and vals[i]!=vals[i+1]:
                    return xs[i]+dirn*(mid-vals[i])/(vals[i+1]-vals[i])
            return np.nan
        out.append((y,subpix(xl,1),subpix(xr,-1)))
    return np.array(out)
# pooled VP from rows 380-436, both phases, three renders
VPs=[]
for V in ['captured_0023','captured_0023s','captured_0023x']:
    for ph in ['slope','table']:
        E_=edges(V,ph,380,437)
        aL,bL=np.polyfit(E_[:,0],E_[:,1],1); aR,bR=np.polyfit(E_[:,0],E_[:,2],1)
        yv=(bR-bL)/(aL-aR); VPs.append((aL*yv+bL,yv))
VPs=np.array(VPs); print('VPs rows380-436:',np.round(VPs,1).tolist()); vp=VPs.mean(0); print('mean VP',np.round(vp,1),'sd',np.round(VPs.std(0),1))
def routeA(rows,f,vp,t=0.0146,anchor='near',es=-0.0156):
    rows=np.array(rows)
    dup=ray(vp[0],vp[1],f); dup/=np.linalg.norm(dup)
    e=np.array([1.0,es,0]); e-=(e@dup)*dup; e/=np.linalg.norm(e)
    n=np.cross(dup,e); n/=np.linalg.norm(n)
    if n[2]<0: n=-n
    if anchor=='near': r=ray(590,481.5,f); P=0.9555*r/np.linalg.norm(r)
    else: r=ray(590,356.5,f); P=1.201*r/np.linalg.norm(r)
    d=n@P; dc=d-t
    on=lambda x,y,dd: ray(x,y,f)*dd/(n@ray(x,y,f))
    ws=[]
    for x,yb,yf,_ in rows:
        Pb=on(x,yb,dc); Pf=on(x,yf,dc); ws.append(abs((Pb-Pf)@dup))
    incl=np.degrees(np.arcsin(-dup[1]))
    return np.mean(ws), incl
print('Route A per-column (projection on slope direction):')
for V in ['captured_0023','captured_0023s','captured_0023x']:
    rows=E[f'{V}_slope']
    for f in [650,711,780]:
        out=[]
        for v in [vp,(vp[0],vp[1]-10),(vp[0],vp[1]+10)]:
            for anc in ['near','far']:
                for t in [0.013,0.0146,0.017]:
                    out.append(routeA(rows,f,v,t=t,anchor=anc)[0])
        w0,inc=routeA(rows,f,vp)
        print('  %s f=%d w=%.2f cm (incl %.1f deg to cam-horizontal), spread %.2f-%.2f'%(V,f,100*w0,inc,100*min(out),100*max(out)))
def routeB(rows,f,yh0=350.7,xh0=598.5,sh=0.0,t=0.0146,anchor='board',psi_deg=None):
    rows=np.array(rows)
    l=np.array([sh,-1.0,yh0-sh*xh0]); K=np.array([[f,0,640],[0,f,360],[0,0,1.]])
    n=K.T@l; n/=np.linalg.norm(n)
    if n@ray(640,500,f)<0: n=-n
    if anchor=='board': r=ray(590,481.5,f); H=n@(0.9555*r/np.linalg.norm(r))
    else:
        rl=ray(283.1,532.5,f); rr=ray(917.5,528.2,f); H=0.603/np.linalg.norm(rr/(n@rr)-rl/(n@rl))
    Hc=H-t
    on=lambda x,y,dd: ray(x,y,f)*dd/(n@ray(x,y,f))
    B=np.array([on(x,yb,Hc) for x,yb,yf,_ in rows]); F=np.array([on(x,yf,Hc) for x,yb,yf,_ in rows]); Bt=np.array([on(x,ybt,H) for x,_,_,ybt in rows])
    # book long-axis direction from all three edge lines (pooled slope in-plane)
    def dirn(P):
        c=P.mean(0); u=np.linalg.svd(P-c)[2][0]; return u if u[0]>0 else -u
    us=[dirn(B),dirn(F),dirn(Bt)]
    u=np.mean(us,0); u-=(u@n)*n; u/=np.linalg.norm(u)
    if psi_deg is not None:
        # override: yaw angle relative to camera X axis within the table plane
        xax=np.array([1,0,0.]); xax-=(xax@n)*n; xax/=np.linalg.norm(xax); zax=np.cross(n,xax)
        u=np.cos(np.radians(psi_deg))*xax+np.sin(np.radians(psi_deg))*zax* (1 if zax[2]>0 else -1)
    wdir=np.cross(n,u); wdir/=np.linalg.norm(wdir)
    col=np.linalg.norm(B-F,axis=1).mean()
    w=np.abs((B-F)@wdir).mean()
    yaws=[np.degrees(np.arctan2(abs(q[2]),abs(q[0])))*np.sign(q[2]*q[0]) for q in us]
    return w,col,H,yaws
print('Route B:')
for V in ['captured_0023','captured_0023s','captured_0023x']:
    rows=E[f'{V}_table']
    for f in [650,711,780]:
        w,col,H,yaws=routeB(rows,f)
        alt=[routeB(rows,f,yh0=yh,sh=sh,anchor=a)[1] for yh in [348.7,350.7,352.7] for sh in [-0.0067,0.0078] for a in ['board','tablewidth']]
        print('  %s f=%d per-column dist %.2f cm; yaw-corrected %.2f (yaw est back/front/bottom %s); H=%.3f; col-dist spread %.2f-%.2f'%(V,f,100*col,100*w,np.round(yaws,1).tolist(),H,100*min(alt),100*max(alt)))
