# KLT tracks over the frozen glide phase (frames 51-71) in 0302; fit common FOE (vp) and per-track t*
import cv2, numpy as np, sys
vid = sys.argv[1] if len(sys.argv)>1 else '0302'
a,b = 51,71
c = cv2.VideoCapture(f'/home/user/quantiphy-challenge/data/QuantiPhy/simulation_{vid}.mp4')
fr=[]
i=0
while True:
    ok,f=c.read()
    if not ok: break
    if a<=i<=b: fr.append(f)
    i+=1
if vid=='0309':
    fr=[f[:,160:2720] for f in fr]
bg=np.load('bg0302.npy').astype(np.float32)
def mask(f):
    d=np.abs(f.astype(np.float32)-bg).sum(2)
    m=(d>40).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(m)
    k=1+np.argmax(st[1:,4]); return (lab==k).astype(np.uint8)
g=[cv2.cvtColor(f,cv2.COLOR_BGR2GRAY) for f in fr]
if vid=='0302':
    m0=mask(fr[0])
else:
    # use 0302 mask (same render geometry assumed; verified separately)
    c2=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0302.mp4'); j=0
    while True:
        ok,f=c2.read()
        if j==a: break
        j+=1
    m0=mask(f)
m0e=cv2.erode(m0,np.ones((5,5) if vid=="0302" else (15,15),np.uint8))
p0=cv2.goodFeaturesToTrack(g[0],5000,0.0005,4,mask=m0e*255)
P=[p0.reshape(-1,2)]
ok_all=np.ones(len(p0),bool)
lk=dict(winSize=(21,21),maxLevel=3,criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,50,0.01))
cur=p0
for i in range(1,len(g)):
    nx,st,_=cv2.calcOpticalFlowPyrLK(g[i-1],g[i],cur,None,**lk)
    bk,st2,_=cv2.calcOpticalFlowPyrLK(g[i],g[i-1],nx,None,**lk)
    fb=np.linalg.norm(bk-cur,axis=2).ravel()
    ok_all&=(st.ravel()==1)&(st2.ravel()==1)&(fb<0.5)
    P.append(nx.reshape(-1,2)); cur=nx
T=np.array(P)[:,ok_all]
t=np.arange(a,b+1)/24.0
print('tracks',T.shape)
def fit_vp(T):
    # least-squares intersection of per-track lines
    A=np.zeros((2,2)); bb=np.zeros(2); lines=[]
    for j in range(T.shape[1]):
        X=T[:,j]; m=X.mean(0); U,S,Vt=np.linalg.svd(X-m); d=Vt[0]
        n=np.array([-d[1],d[0]])
        A+=np.outer(n,n); bb+=n*(n@m); lines.append((m,n))
    vp=np.linalg.solve(A,bb)
    perp=np.array([np.abs((T[:,j]-vp)@lines[j][1]).max() for j in range(T.shape[1])])
    return vp, perp
def tstar(T,vp):
    s=[];rr=[]
    for j in range(T.shape[1]):
        r=np.linalg.norm(T[:,j]-vp,axis=1)
        A=np.polyfit(t,1/r,1); s.append(-A[1]/A[0])
        rr.append(np.abs(1/np.polyval(A,t)-r).max())
    return np.array(s),np.array(rr)
vp,perp=fit_vp(T)
keep=perp<3*np.median(perp)+0.5
T=T[:,keep]
vp,perp=fit_vp(T)
s,rr=tstar(T,vp)
keep=rr<1.0
T=T[:,keep]; vp,perp=fit_vp(T); s,rr=tstar(T,vp)
print('vp',vp,'N',T.shape[1],'median perp',np.median(perp),'median radial res',np.median(rr))
np.savez(f'klt{vid}.npz',T=T,t=t,vp=vp,s=s)
