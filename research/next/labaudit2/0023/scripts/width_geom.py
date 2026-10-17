import numpy as np, json, itertools
D='/home/user/quantiphy-challenge/research/next/labaudit2/0023/'
E=json.load(open(D+'scripts/book_edges.json'))
def ray(x,y,f,cx=640,cy=360): return np.array([(x-cx)/f,(y-cy)/f,1.0])
def line_dist(P,Q):
    # P,Q: Nx3 points on two (near) parallel 3D lines; distance between lines (fit P line, avg perpendicular distance of Q)
    c=P.mean(0); u=np.linalg.svd(P-c)[2][0]
    d=Q-c; perp=d-np.outer(d@u,u); return np.linalg.norm(perp,axis=1).mean(), u
def routeA(rows,f,vp=(602,-58),t=0.0146,anchor='near',es=-0.0156):
    rows=np.array(rows); rows=rows[~np.isnan(rows).any(1)]
    dup=ray(vp[0],vp[1],f); dup/=np.linalg.norm(dup)
    e=np.array([1.0,es,0]); e-= (e@dup)*dup; e/=np.linalg.norm(e)
    n=np.cross(dup,e); n/=np.linalg.norm(n)
    if n[2]<0: n=-n
    if anchor=='near':
        r=ray(590,481.5,f); P=0.9555*r/np.linalg.norm(r)
    else:
        r=ray(590,356.5,f); P=1.201*r/np.linalg.norm(r)
    d=n@P
    dc=d-t
    def onplane(x,y,dd):
        r=ray(x,y,f); return r*dd/(n@r)
    B=np.array([onplane(x,yb,dc) for x,yb,yf,_ in rows]); F=np.array([onplane(x,yf,dc) for x,yb,yf,_ in rows])
    w,u=line_dist(B,F)
    # also length scale check: slope angle
    return w, d
def routeB(rows,f,yh0=350.7,xh0=598.5,sh=0.0,t=0.0146,anchor='board'):
    rows=np.array(rows); rows=rows[~np.isnan(rows).any(1)]
    # horizon line: y = yh0 + sh*(x-xh0)  -> l = (sh, -1, yh0 - sh*xh0)
    l=np.array([sh,-1.0,yh0-sh*xh0])
    K=np.array([[f,0,640],[0,f,360],[0,0,1.]])
    n=K.T@l; n/=np.linalg.norm(n)
    # orientation: points below horizon (table) should have n.P>0
    if n@ray(640,500,f)<0: n=-n
    if anchor=='board':
        r=ray(590,481.5,f); P=0.9555*r/np.linalg.norm(r)
        H=n@P
    elif anchor=='tablewidth':
        # front edge Z such that 634.5 px span = 0.603 m
        # front edge points FL (283.1,532.5) FR (917.5,528.2) on plane: find H s.t. |P_FR-P_FL|=0.603
        rl=ray(283.1,532.5,f); rr=ray(917.5,528.2,f)
        PL=rl/(n@rl); PR=rr/(n@rr); H=0.603/np.linalg.norm(PR-PL)
    Hc=H-t
    def onplane(x,y,dd):
        r=ray(x,y,f); return r*dd/(n@r)
    B=np.array([onplane(x,yb,Hc) for x,yb,yf,_ in rows]); F=np.array([onplane(x,yf,Hc) for x,yb,yf,_ in rows])
    Bot=np.array([onplane(x,yb2,H) for x,_,_,yb2 in rows])
    w,u=line_dist(B,F)
    Lbook=None
    yaw=np.degrees(np.arctan2(u[2],u[0]))
    return w,H,yaw,F[:,2].mean(),B[:,2].mean()
print('=== Route A (book resting on slope, frames 0-20) ===')
for V in ['captured_0023x','captured_0023','captured_0023s']:
    rows=E[f'{V}_slope']
    for f in [650,711,780]:
        res=[]
        for vp in [(602,-58),(602,-48),(602,-68)]:
            for anchor in ['near','far']:
                w,d=routeA(rows,f,vp=vp,anchor=anchor); res.append(w)
        w0,_=routeA(rows,f)
        print(V,'f',f,'base w=%.2f cm'%(100*w0),' range over VP+-10/anchor: %.2f-%.2f'%(100*min(res),100*max(res)))
print('=== Route B (book resting on table, frames 38-48) ===')
for V in ['captured_0023x','captured_0023','captured_0023s']:
    rows=E[f'{V}_table']
    for f in [650,711,780]:
        res=[]
        for yh in [348.7,350.7,352.7]:
            for sh in [-0.0067,0.0078]:
                for anchor in ['board','tablewidth']:
                    w,H,yaw,zf,zb=routeB(rows,f,yh0=yh,sh=sh,anchor=anchor); res.append(w)
        w0,H0,yaw0,zf,zb=routeB(rows,f)
        w1,H1,_,_,_=routeB(rows,f,anchor='tablewidth')
        print(V,'f',f,'base w=%.2f cm (H=%.3f, yaw %.1f deg, Zfront %.3f Zback %.3f); tablewidth-anchor w=%.2f H=%.3f; range %.2f-%.2f'%(100*w0,H0,yaw0,zf,zb,100*w1,H1,100*min(res),100*max(res)))
