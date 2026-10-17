from common import *
from tracks import *
from fit_a import fit, model, gd, proj
db=np.load(OUT+'/b_down.npy')
ga=gd(0)
pWa,_=fit(A_W,list(range(24,38)),ga); pGa,_=fit(A_G_raw,list(range(24,37)),ga)
pWb,_=fit(B_W,list(range(24,39)),db); pGb,_=fit(B_G,list(range(24,37)),db)
ts=np.array([tcap(k) for k in range(24,37)])
A=np.vstack([model(pWa,ts,1.0,ga),model(pGa,ts,1.0,ga)])
B=np.vstack([model(pWb,ts,1.0,db),model(pGb,ts,1.0,db)])
def umeyama(X,Y,scale=True):  # find s,R,t: Y ~ s R X + t
    mx,my=X.mean(0),Y.mean(0); Xc,Yc=X-mx,Y-my
    U,S,Vt=np.linalg.svd(Yc.T@Xc/len(X)); D=np.eye(3)
    if np.linalg.det(U@Vt)<0: D[2,2]=-1
    Rm=U@D@Vt; s=np.trace(np.diag(S)@D)/((Xc**2).sum()/len(X)) if scale else 1.0
    return s,Rm,my-s*Rm@mx
s,Rm,t=umeyama(B,A)
res=A-(s*(Rm@B.T).T+t)
print('similarity b->a: scale=%.3f rms resid=%.3f m'%(s,np.sqrt((res**2).sum(1).mean())))
print('b camera centre in a frame:',np.round(t,3),' b optical axis in a:',np.round(Rm@[0,0,1],3),' b down in a frame:',np.round(Rm@db,3))
# gravity consistency: a's down vs mapped b's down
print('angle between gravity dirs: %.1f deg'%np.degrees(np.arccos(np.clip((Rm@db)@ga,-1,1))))
np.save(OUT+'/sim_b2a.npy',np.concatenate([[s],Rm.ravel(),t]))
# triangulate green at capture 39 (video 37): rays from a (origin 0) and b (origin t, dir Rm*ray_b)
def tri2(oa,da,ob,dbb):
    # closest points
    w=oa-ob; a=da@da; b=da@dbb; c=dbb@dbb; d=da@w; e=dbb@w
    den=a*c-b*b; sa=(b*e-c*d)/den; sb=(a*e-b*d)/den
    pa=oa+sa*da; pb=ob+sb*dbb; return (pa+pb)/2, np.linalg.norm(pa-pb), sa, sb
for k in [35,36,37,38]:
    for name,ta,tb,pa_ in [('G',A_G_raw,B_G,pGa),('W',A_W,B_W,pWa)]:
        if k not in ta or k not in tb: continue
        P,gap,sa,sb=tri2(np.zeros(3),ray(*ta[k]),t,Rm@ray(*tb[k]))
        Cf=model(pa_,np.array([tcap(k)]),1.0,ga)[0]
        print(f'k={k} cap={cap(k)} {name}: tri={np.round(P,3)} gap={gap:.3f} range_a={np.linalg.norm(P):.3f} down_a={P@ga:.3f} | free-flight a: range {np.linalg.norm(Cf):.3f} down {Cf@ga:.3f}')
