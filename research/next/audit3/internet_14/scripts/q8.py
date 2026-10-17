import cv2,numpy as np
c=cv2.VideoCapture('data/QuantiPhy/internet_0008.mp4')
res=[]
f=0
while True:
    ok,im=c.read()
    if not ok: break
    g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY).astype(float)
    if f%15==0 or (220<=f<=360 and f%5==0):
        # sailboat hull region rows 495-515
        band=g[498:516]
        dark=(band<60)
        cols=np.where(dark.sum(0)>=3)[0]
        # speedboat rows 518-540
        b2=g[518:540]; d2=b2<50; c2=np.where(d2.sum(0)>=2)[0]
        # group cols
        def groups(cols):
            if len(cols)==0: return []
            gs=[[cols[0],cols[0]]]
            for x in cols[1:]:
                if x-gs[-1][1]<=4: gs[-1][1]=x
                else: gs.append([x,x])
            return [g for g in gs if g[1]-g[0]>8]
        res.append((f,groups(cols),groups(c2)))
    f+=1
for r in res: print(r)
