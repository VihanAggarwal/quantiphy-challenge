import cv2, numpy as np, json
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0253.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
B=json.load(open('box0253.json')); BB={r[0]:r for r in B}
th=np.radians(44.224); d=np.array([np.cos(th),np.sin(th)]); n=np.array([-d[1],d[0]])
bg=fr[0].astype(np.float32)
for i in range(15,45):
    if i not in BB or i in (27,28): continue
    f=fr[i].astype(np.float32)
    # chroma-ish signal: blue diff relative to bg (box is orange: low blue) and also luma
    sigB=bg[...,0]-f[...,0]
    Yf=f@np.array([0.114,0.587,0.299],np.float32); Yb=bg@np.array([0.114,0.587,0.299],np.float32)
    cxy=np.array(BB[i][1:3])
    res=[]
    for off in np.arange(-25,26,5):   # perpendicular offsets across the face
        r=np.arange(-90,90,0.25)
        P=cxy[None,:]+r[:,None]*d[None,:]+off*n[None,:]
        pb=cv2.remap(sigB,P[:,0].astype(np.float32).reshape(1,-1),P[:,1].astype(np.float32).reshape(1,-1),cv2.INTER_LINEAR)[0]
        core=np.median(pb[np.abs(r)<20])
        if core<20: continue
        half=core/2
        inside=np.where(pb>=half)[0]
        # contiguous run around centre
        j0=np.argmin(np.abs(r)); 
        if pb[j0]<half: continue
        a=j0
        while a>0 and pb[a-1]>=half: a-=1
        b=j0
        while b<len(r)-1 and pb[b+1]>=half: b+=1
        ra=r[a-1]+(half-pb[a-1])/(pb[a]-pb[a-1])*0.25 if a>0 else r[a]
        rb=r[b]+(pb[b]-half)/(pb[b]-pb[b+1])*0.25 if b<len(r)-1 else r[b]
        res.append((off,rb-ra))
    if res:
        L=np.array(res)
        print(i,f's={BB[i][3]:.0f}',' '.join(f'{o:+.0f}:{l:.1f}' for o,l in L), ' median=%.1f'%np.median(L[:,1]))
