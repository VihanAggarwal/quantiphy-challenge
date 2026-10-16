import cv2, numpy as np, json
d='/home/user/quantiphy-challenge/research/next/labaudit/0020/'
T=json.load(open(d+'tracks.json'))
def alpha(im):
    # fraction of non-green: use green excess
    b,g,r=[im[...,k].astype(float) for k in range(3)]
    ge=g-np.maximum(r,b)       # pure green ~ 255-0
    a=1-np.clip(ge/200.,0,1)
    return a
for obj,frames in (('toy',[13,14,15,16,17,19,20,21,22,23,24]),('jar',[15,16,17,19,20,21,22,23,24,25,26,27])):
    tr=T['x'][obj]
    for i in frames:
        im=cv2.imread(d+f'frames/0020x_f{i:02d}.png')
        a=alpha(im)
        u,v=tr[str(i)][:2]
        # motion direction: central difference on o track
        to=T['o'][obj]
        p=np.array(to[str(i+1)][:2]) if str(i+1) in to else np.array(to[str(i)][:2])
        q=np.array(to[str(i-1)][:2]) if str(i-1) in to else np.array(to[str(i)][:2])
        m=p-q; m/=np.linalg.norm(m); n=np.array([-m[1],m[0]])
        # mask: alpha>0.5 component containing centre
        M=(a>0.5).astype(np.uint8)
        nl,lab,st,cen=cv2.connectedComponentsWithStats(M)
        k=lab[int(round(v)),int(round(u))]
        if k==0:
            ds=[np.hypot(*(cen[j]-[u,v])) for j in range(1,nl)]; k=1+int(np.argmin(ds))
        ys,xs=np.nonzero(lab==k)
        if len(xs)>20000: print(obj,i,'merged'); continue
        P=np.c_[xs-u,ys-v]
        along=P@m; perp=P@n
        # robust extents (1st-99th pct)
        Wp=np.percentile(perp,99)-np.percentile(perp,1); Wa=np.percentile(along,99)-np.percentile(along,1)
        print(obj,i,'area %d'%len(xs),'motion (%.2f,%.2f) step %.1f'%(m[0],m[1],np.linalg.norm(p-q)/2),'perp %.1f along %.1f'%(Wp,Wa))
