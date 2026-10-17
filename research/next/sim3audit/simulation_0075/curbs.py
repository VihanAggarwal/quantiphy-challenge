import cv2, numpy as np, sys
path=sys.argv[1]; r0,r1=int(sys.argv[2]),int(sys.argv[3]); seed=int(sys.argv[4])
im=cv2.imread(path).astype(int)
B,G,R=im[...,0],im[...,1],im[...,2]
road=(abs(B-G)<5)&(abs(G-R)<5)&(B>140)&(B<195)
# close small objects
road=cv2.morphologyEx(road.astype(np.uint8),cv2.MORPH_CLOSE,np.ones((1,41),np.uint8))
L=[];Rr=[]
for r in range(r0,r1):
    row=road[r]
    if not row[seed]: continue
    l=seed
    while l>0 and row[l-1]: l-=1
    rr=seed
    while rr<len(row)-1 and row[rr+1]: rr+=1
    L.append((r,l));Rr.append((r,rr))
L=np.array(L);Rr=np.array(Rr)
def fit(P):
    # u = a*v + b robust
    v,u=P[:,0].astype(float),P[:,1].astype(float)
    m=np.ones(len(v),bool)
    for it in range(5):
        a,b=np.polyfit(v[m],u[m],1)
        res=u-(a*v+b); s=np.median(abs(res[m]))*1.5+0.5
        m=abs(res)<3*s
    return a,b,np.sqrt(np.mean(res[m]**2)),m.sum(),len(v)
fl=fit(L);fr=fit(Rr)
print('left u=%.4f v+%.1f rms %.2f n %d/%d'%fl)
print('right u=%.4f v+%.1f rms %.2f n %d/%d'%fr)
# vanishing point
a1,b1=fl[:2];a2,b2=fr[:2]
v=(b2-b1)/(a1-a2);u=a1*v+b1
print('VP u=%.1f v=%.1f'%(u,v))
np.save('/dev/null',0)
