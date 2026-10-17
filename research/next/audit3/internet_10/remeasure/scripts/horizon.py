import cv2, numpy as np, sys
fr=int(sys.argv[1]) if len(sys.argv)>1 else 0
c=cv2.VideoCapture('data/QuantiPhy/internet_0054.mp4')
c.set(cv2.CAP_PROP_POS_FRAMES,fr); ok,f=c.read()
X0,Y0=1100,1250
cr=f[Y0:1600,X0:2600].astype(int)
hsv=cv2.cvtColor(f[Y0:1600,X0:2600],cv2.COLOR_BGR2HSV)
m=((cr.min(2)>165)&(hsv[...,1]<60)).astype(np.uint8)
m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
# center line columns: find per row
H,Wd=m.shape
# remove centre line: per row, the white run near x~735
for y in range(H):
    row=m[y]
    xs=np.nonzero(row[650:820])[0]
    # find the run containing the centre line: assume line ~ 12-25 px wide; take runs in 650-820
    m[y,650:820]=0 if True else row[650:820]
# rings: components
n,lab,st,cen=cv2.connectedComponentsWithStats(m)
idx=[j for j in range(1,n) if st[j,4]>500]
print([(j,st[j].tolist()) for j in idx])
def edges_for(mask_ring):
    top_out=[];top_in=[];bot_in=[];bot_out=[]
    for x in range(mask_ring.shape[1]):
        col=mask_ring[:,x]
        ys=np.nonzero(col)[0]
        if len(ys)==0: continue
        # runs
        br=np.nonzero(np.diff(ys)>1)[0]
        starts=np.r_[ys[0],ys[br+1]]; ends=np.r_[ys[br],ys[-1]]
        if len(starts)!=2: continue
        top_out.append((x,starts[0]-0.5)); top_in.append((x,ends[0]+0.5))
        bot_in.append((x,starts[1]-0.5)); bot_out.append((x,ends[1]+0.5))
    return np.array(top_out),np.array(top_in),np.array(bot_in),np.array(bot_out)
def fitconic(P):
    x=P[:,0].astype(float);y=P[:,1].astype(float)
    mx,my=x.mean(),y.mean(); s=np.sqrt(((x-mx)**2+(y-my)**2).mean())
    T=np.array([[1/s,0,-mx/s],[0,1/s,-my/s],[0,0,1]])
    xn=(x-mx)/s; yn=(y-my)/s
    A=np.c_[xn*xn,xn*yn,yn*yn,xn,yn,np.ones_like(xn)]
    _,_,vt=np.linalg.svd(A); a,b,cc,d,e,ff=vt[-1]
    Cn=np.array([[a,b/2,d/2],[b/2,cc,e/2],[d/2,e/2,ff]])
    C=T.T@Cn@T
    return C/np.linalg.norm(C)
# group components into outer ring (larger) and inner ring
areas=sorted(idx,key=lambda j:-st[j,2])
outer=[j for j in idx if st[j,3]>150]; inner=[j for j in idx if st[j,3]<=150 and st[j,3]>40]
print('outer',outer,'inner',inner)
conics={}
for name,comps in (('outer',outer),('inner',inner)):
    mm=np.isin(lab,comps).astype(np.uint8)
    to,ti,bi,bo=edges_for(mm)
    oute=np.r_[to,bo]; inne=np.r_[ti,bi]
    oute=oute+[X0,Y0]; inne=inne+[X0,Y0]
    conics[name+'_o']=fitconic(oute); conics[name+'_i']=fitconic(inne)
    print(name,len(oute),len(inne))
def ell_params(C):
    # centre, extents
    A=C[:2,:2]; b=C[:2,2]
    ctr=-np.linalg.solve(A,b)
    return ctr
for k,C in conics.items():
    ctr=ell_params(C)
    # x extent at centre row, y extent at centre col
    print(k,'centre',ctr.round(1))
def vanline(C1,C2):
    M=np.linalg.solve(C2,C1)
    w,v=np.linalg.eig(M)
    w=np.real(w)
    # find the pair of closest eigenvalues
    best=None
    for i in range(3):
        for j in range(i+1,3):
            d=abs(w[i]-w[j])
            if best is None or d<best[0]: best=(d,(w[i]+w[j])/2)
    lam=best[1]
    D=C1-lam*C2
    u,s,vt=np.linalg.svd(D)
    l=u[:,0]*np.sqrt(s[0])
    return l/np.linalg.norm(l[:2]),s,w
res=[]
keys=list(conics)
for i in range(4):
    for j in range(i+1,4):
        l,s,w=vanline(conics[keys[i]],conics[keys[j]])
        # horizon y at x=1920 and x=1000,3000
        yh=lambda x: -(l[0]*x+l[2])/l[1]
        res.append((keys[i],keys[j],yh(1000),yh(1920),yh(3000),s[1]/s[0]))
for r in res: print(r[0],r[1],'yh@1000 %.1f yh@1920 %.1f yh@3000 %.1f rank %.3f'%r[2:])
