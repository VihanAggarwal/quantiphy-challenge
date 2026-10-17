import cv2,numpy as np,sys
v=sys.argv[1]; split=int(sys.argv[2]) if len(sys.argv)>2 else 540
c=cv2.VideoCapture(f'data/QuantiPhy/{v}.mp4')
frames=[]
while True:
    ok,im=c.read()
    if not ok: break
    frames.append(im.astype(np.int16))
n=len(frames)
bgcol=np.median(frames[-1].reshape(-1,3),axis=0)
print(v,n,'bg',bgcol)
car=[];pl=[]
for i,f in enumerate(frames):
    d=np.abs(f-bgcol).sum(2)
    m=(d>25).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
    nl,lab,st,cen=cv2.connectedComponentsWithStats(m)
    # car: components in lower part
    lo=[k for k in range(1,nl) if cen[k][1]>split and st[k][4]>50]
    up=[k for k in range(1,nl) if cen[k][1]<=split and st[k][4]>50]
    def agg(ks):
        if not ks: return None
        x0=min(st[k][0] for k in ks);y0=min(st[k][1] for k in ks)
        x1=max(st[k][0]+st[k][2] for k in ks);y1=max(st[k][1]+st[k][3] for k in ks)
        A=sum(st[k][4] for k in ks); cx=sum(cen[k][0]*st[k][4] for k in ks)/A; cy=sum(cen[k][1]*st[k][4] for k in ks)/A
        return (x0,y0,x1,y1,cx,cy,A)
    car.append(agg(lo)); pl.append(agg(up))
np.save('/tmp/claude-0/-home-user/879308ec-3ca1-5f52-960b-589240fd8127/scratchpad/%s_tracks.npy'%v,np.array([[*(a if a else [np.nan]*7),*(b if b else [np.nan]*7)] for a,b in zip(car,pl)],float))
for i in range(n):
    a=car[i];b=pl[i]
    print(i, 'car', a if a is None else tuple(round(float(x),2) for x in a), 'plane', b if b is None else tuple(round(float(x),2) for x in b))
