import cv2, numpy as np
def frames(v):
    cap=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/%s.mp4'%v)
    out=[]
    while True:
        ok,f=cap.read()
        if not ok: break
        out.append(f)
    return out
a=frames('simulation_0211'); b=frames('simulation_0212')
bg=np.median(np.stack(a[::2]),axis=0).astype(np.uint8)
res=[]
for i,f in enumerate(b):
    d=np.abs(f.astype(int)-bg.astype(int)).sum(2)
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    m=(d>45)
    # remove the cat: dark pixels (black fur) and cat white paws - cat is low saturation; dog fur is saturated brown
    dogcol=(hsv[...,1]>60)&(hsv[...,2]>50)
    md=(m&dogcol).astype(np.uint8)
    md=cv2.morphologyEx(md,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    md=cv2.morphologyEx(md,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8))
    n,lab,st,cen=cv2.connectedComponentsWithStats(md)
    k=1+np.argmax(st[1:,4])
    mm=(lab==k)
    ys,xs=np.nonzero(mm)
    res.append((i,xs.min(),xs.max(),ys.min(),ys.max(),xs.mean(),ys.mean(),mm.sum()))
    if i%6==0:
        vis=f.copy(); vis[mm]=(0,0,255)
        cv2.imwrite('frames/dogmask_%03d.png'%i,cv2.resize(vis[500:1080,400:1800],None,fx=0.6,fy=0.6))
np.save('dogbox.npy',np.array(res,float))
for r in res: print(' '.join('%.1f'%x for x in r))
