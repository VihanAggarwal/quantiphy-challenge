from curbs import *
from ov import draw
bg=cv2.imread('fr/bg_simulation_0066.png'); ch=cv2.GaussianBlur(chroma(bg),(5,5),0)
road=(np.abs(ch)<5).astype(np.uint8)
side=(ch>9).astype(np.uint8)
# boundary pixels: road pixels adjacent (within 3px) to sidewalk/curb pixels
dil=cv2.dilate(side,np.ones((5,5),np.uint8))
bd=(road&dil).astype(np.uint8)
bd[:150]=0
ys,xs=np.nonzero(bd)
P=np.stack([xs,ys],1).astype(float)
print(len(P))
rng=np.random.default_rng(0)
lines=[]
rem=P.copy()
for it in range(8):
    best=None
    for _ in range(3000):
        a,b=rem[rng.choice(len(rem),2,replace=False)]
        d=b-a; L=np.linalg.norm(d)
        if L<50: continue
        n=np.array([-d[1],d[0]])/L; c=-n@a
        inl=np.abs(rem@n+c)<1.5
        if best is None or inl.sum()>best[0]: best=(inl.sum(),inl)
    cnt,inl=best
    if cnt<150: break
    ln,res=fitline(rem[inl]); inl=np.abs(rem@ln[:2]+ln[2])<2.0; ln,res=fitline(rem[inl])
    ext=rem[inl]; print(it,cnt,'rms %.2f'%res.std(), 'x %d-%d y %d-%d'%(ext[:,0].min(),ext[:,0].max(),ext[:,1].min(),ext[:,1].max()), ln)
    lines.append(ln); rem=rem[~inl]
np.save('auto66.npy',np.array(lines))
im=draw(bg,lines)
for k,ln in enumerate(lines):
    pass
cv2.imwrite('fr/auto66.png',cv2.resize(im,(1080,540)))
