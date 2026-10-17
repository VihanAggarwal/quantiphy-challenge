import cv2, numpy as np, json
c=cv2.VideoCapture('/home/user/quantiphy-challenge/data/QuantiPhy/simulation_0253.mp4')
fr=[]
while True:
    ok,f=c.read()
    if not ok: break
    fr.append(f)
bg=fr[0].astype(np.float32)
th=np.radians(44.224); d=np.array([np.cos(th),np.sin(th)]); n=np.array([-d[1],d[0]])
out=[]
for i,f in enumerate(fr):
    F=f.astype(np.float32)
    hsv=cv2.cvtColor(f,cv2.COLOR_BGR2HSV)
    diff=np.abs(F-bg).sum(2)
    m=((diff>45)&(hsv[...,1]>60)).astype(np.uint8)
    m=cv2.morphologyEx(m,cv2.MORPH_OPEN,np.ones((3,3),np.uint8))
    nn,lab,st,cen=cv2.connectedComponentsWithStats(m)
    if nn<2: continue
    k=1+np.argmax(st[1:,4]); x,y,w,h,a=st[k]
    if a<2000 or x<2 or y<2 or x+w>1918 or y+h>1078: 
        print(i,'partial/none',x,y,w,h,a); continue
    ys,xs=np.where(lab==k)
    S=xs*d[0]+ys*d[1]; N=xs*n[0]+ys*n[1]
    # robust extents (1st/99th percentiles) and full
    sp=np.percentile(S,[0.5,99.5]); npc=np.percentile(N,[0.5,99.5])
    out.append((i,float(xs.mean()),float(ys.mean()),float(S.mean()),float(sp[1]-sp[0]),float(npc[1]-npc[0]),int(a)))
    print(i,f'cen=({xs.mean():.1f},{ys.mean():.1f}) s={S.mean():.1f} along={sp[1]-sp[0]:.1f} perp={npc[1]-npc[0]:.1f} area={a} sqrtA={np.sqrt(a):.1f}')
json.dump(out,open('box0253.json','w'))
