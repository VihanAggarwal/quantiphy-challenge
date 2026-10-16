import cv2, numpy as np, sys
F='/home/user/quantiphy-challenge/research/next/labaudit/0008/'
fr=int(sys.argv[1]) if len(sys.argv)>1 else 10
v=sys.argv[2] if len(sys.argv)>2 else 'captured_0008'
im=cv2.imread(F+f'frames/{v}_f{fr:02d}.png').astype(float)
g=cv2.GaussianBlur(im,(3,3),0)
C={'BL':(478.3,416),'BR':(683.3,379.3),'FR':(755,541.7),'FL':(432.3,605)}
edges={'back':('BL','BR'),'right':('BR','FR'),'front':('FR','FL'),'left':('FL','BL')}
inside=np.array([590,490.])
def sample(p):
    return cv2.getRectSubPix(g.astype(np.float32),(1,1),(float(p[0]),float(p[1]))).reshape(3)
lines={}
for name,(a,b) in edges.items():
    A=np.array(C[a]);B=np.array(C[b]); d=(B-A)/np.linalg.norm(B-A); nrm=np.array([-d[1],d[0]])
    if np.dot(inside-A,nrm)<0: nrm=-nrm   # nrm points inward
    pts=[]
    for s in np.linspace(0.12,0.88,40):
        P=A+s*(B-A)
        offs=np.arange(-15,15.01,0.5)
        vals=np.array([sample(P+o*nrm) for o in offs])
        # wood: high brightness/high R-B ; use luminance-ish plus colour diff: project onto (inside - outside) colour
        ins=vals[offs>8].mean(0); out=vals[offs<-8].mean(0)
        dv=ins-out; proj=vals@dv/np.linalg.norm(dv)
        gr=np.gradient(proj)
        k=np.argmax(gr); pts.append(P+offs[k]*nrm)
    pts=np.array(pts)
    # robust line fit
    vx,vy,x0,y0=cv2.fitLine(pts.astype(np.float32),cv2.DIST_HUBER,0,0.01,0.01).ravel()
    res=np.abs((pts[:,0]-x0)*vy-(pts[:,1]-y0)*vx)
    lines[name]=np.cross([x0,y0,1],[x0+vx,y0+vy,1])
    print(name,'resid med %.2f max %.2f'%(np.median(res),res.max()))
def X(l1,l2):
    p=np.cross(lines[l1],lines[l2]); return p[:2]/p[2]
corn={'BL':X('back','left'),'BR':X('back','right'),'FR':X('front','right'),'FL':X('front','left')}
for k,vv in corn.items(): print(k,np.round(vv,1))
np.save(F+f'scripts/corners_{v}_{fr}.npy',np.array([corn[k] for k in ['BL','BR','FR','FL']]))
vp1=np.cross(lines['back'],lines['front']); vp2=np.cross(lines['left'],lines['right'])
print('vp back/front',vp1[:2]/vp1[2],'vp left/right',vp2[:2]/vp2[2])
